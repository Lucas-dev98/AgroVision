package proxy

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type ProxyConfig struct {
	AnimalServiceURL  string
	PesagemServiceURL string
	CotacaoServiceURL string
	VisionServiceURL  string
	MLServiceURL      string
	CircuitThreshold  int
	CircuitOpenWindow time.Duration
	UpstreamTimeout   time.Duration
	CacheTTL          time.Duration
	Logger            *zap.Logger
}

type Proxy struct {
	config   ProxyConfig
	client   *http.Client
	cbMu     sync.Mutex
	circuits map[string]*circuitState
	cacheMu  sync.RWMutex
	cache    map[string]cacheEntry
}

type ServiceStatus struct {
	Service     string `json:"service"`
	URL         string `json:"url"`
	Status      string `json:"status"`
	HTTPStatus  int    `json:"http_status"`
	LatencyMS   int64  `json:"latency_ms"`
	CircuitOpen bool   `json:"circuit_open"`
	Error       string `json:"error,omitempty"`
}

type circuitState struct {
	failures  int
	openUntil time.Time
}

type cacheEntry struct {
	statusCode int
	headers    http.Header
	body       []byte
	expiresAt  time.Time
}

func NewProxy(config ProxyConfig) *Proxy {
	if config.Logger == nil {
		config.Logger = zap.NewNop()
	}
	if config.CircuitThreshold <= 0 {
		config.CircuitThreshold = 3
	}
	if config.CircuitOpenWindow <= 0 {
		config.CircuitOpenWindow = 30 * time.Second
	}
	if config.UpstreamTimeout <= 0 {
		config.UpstreamTimeout = 5 * time.Second
	}
	if config.CacheTTL <= 0 {
		config.CacheTTL = 30 * time.Second
	}

	return &Proxy{
		config:   config,
		client:   &http.Client{Timeout: config.UpstreamTimeout},
		circuits: make(map[string]*circuitState),
		cache:    make(map[string]cacheEntry),
	}
}

func (p *Proxy) ForwardRequest(c *gin.Context, targetURL string, cacheKey string) (int, error) {
	// Create a new request with the same method and body
	req, err := http.NewRequest(c.Request.Method, targetURL, c.Request.Body)
	if err != nil {
		p.config.Logger.Error("Failed to create proxy request", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create proxy request"})
		return http.StatusInternalServerError, err
	}

	// Copy headers from the original request
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	// Remove hop-by-hop headers
	removeHopByHopHeaders(req.Header)

	// Make the request
	resp, err := p.client.Do(req)
	if err != nil {
		p.config.Logger.Error("Failed to forward request", zap.Error(err), zap.String("target_url", targetURL))
		c.JSON(http.StatusBadGateway, gin.H{"error": "Failed to forward request to upstream service"})
		return http.StatusBadGateway, err
	}
	defer resp.Body.Close()

	// Remove hop-by-hop headers before propagating downstream.
	removeHopByHopHeaders(resp.Header)

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		p.config.Logger.Error("Failed to read response body", zap.Error(err))
		c.JSON(http.StatusBadGateway, gin.H{"error": "Invalid upstream response"})
		return http.StatusBadGateway, err
	}

	// Copy response headers
	for key, values := range resp.Header {
		for _, value := range values {
			c.Writer.Header().Add(key, value)
		}
	}

	// Set status code
	c.Writer.WriteHeader(resp.StatusCode)

	// Copy response body
	if _, err := c.Writer.Write(bodyBytes); err != nil {
		p.config.Logger.Error("Failed to copy response body", zap.Error(err))
		return resp.StatusCode, err
	}

	if cacheKey != "" && resp.StatusCode >= 200 && resp.StatusCode < 300 {
		p.storeCachedResponse(cacheKey, resp.StatusCode, resp.Header, bodyBytes)
	}

	return resp.StatusCode, nil
}

func (p *Proxy) RouteToService(c *gin.Context) {
	path := c.Request.URL.Path

	// Route based on path prefix
	var targetURL string
	var targetService string

	switch {
	case strings.HasPrefix(path, "/api/v1/animals"):
		targetURL = p.config.AnimalServiceURL
		targetService = "animal"
	case strings.HasPrefix(path, "/api/v1/pesagens"):
		targetURL = p.config.PesagemServiceURL
		targetService = "pesagem"
	case strings.HasPrefix(path, "/api/v1/cotacoes"):
		targetURL = p.config.CotacaoServiceURL
		targetService = "cotacao"
	case strings.HasPrefix(path, "/api/v1/vision"):
		targetURL = p.config.VisionServiceURL
		targetService = "vision"
	case strings.HasPrefix(path, "/api/v1/ml"):
		targetURL = p.config.MLServiceURL
		targetService = "ml"
	default:
		p.config.Logger.Warn("Unknown route", zap.String("path", path))
		c.JSON(http.StatusNotFound, gin.H{"error": "Route not found"})
		return
	}

	// Check if the target service is configured
	if targetURL == "" {
		p.config.Logger.Error("Service URL not configured", zap.String("service", targetService))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Service unavailable"})
		return
	}

	if p.isCircuitOpen(targetService) {
		retryAfter := int(time.Until(p.circuits[targetService].openUntil).Seconds())
		if retryAfter < 1 {
			retryAfter = 1
		}
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"error":       "Circuit breaker open",
			"service":     targetService,
			"retry_after": retryAfter,
		})
		return
	}

	// Build the target URL
	parsedURL, err := url.Parse(targetURL)
	if err != nil {
		p.config.Logger.Error("Invalid target URL", zap.Error(err), zap.String("url", targetURL))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// Add query parameters
	fullURL := parsedURL.Scheme + "://" + parsedURL.Host + path
	if c.Request.URL.RawQuery != "" {
		fullURL += "?" + c.Request.URL.RawQuery
	}

	if c.Request.Method == http.MethodGet {
		cacheKey := buildCacheKey(c.Request.Method, fullURL)
		if entry, ok := p.getCachedResponse(cacheKey); ok {
			for key, values := range entry.headers {
				for _, value := range values {
					c.Writer.Header().Add(key, value)
				}
			}
			c.Writer.Header().Set("X-Cache", "HIT")
			c.Writer.WriteHeader(entry.statusCode)
			_, _ = c.Writer.Write(entry.body)
			return
		}
	}

	p.config.Logger.Debug("Forwarding request",
		zap.String("service", targetService),
		zap.String("path", path),
		zap.String("target_url", fullURL),
	)

	cacheKey := ""
	if c.Request.Method == http.MethodGet {
		cacheKey = buildCacheKey(c.Request.Method, fullURL)
	}

	status, err := p.ForwardRequest(c, fullURL, cacheKey)
	if err != nil || status >= http.StatusInternalServerError {
		p.markFailure(targetService)
		return
	}

	if c.Request.Method == http.MethodPost || c.Request.Method == http.MethodPut || c.Request.Method == http.MethodPatch || c.Request.Method == http.MethodDelete {
		p.invalidateServiceCache(targetService)
	}

	p.markSuccess(targetService)
}

func (p *Proxy) Dashboard(c *gin.Context) {
	services := []ServiceStatus{
		{Service: "animal", URL: p.config.AnimalServiceURL},
		{Service: "pesagem", URL: p.config.PesagemServiceURL},
		{Service: "cotacao", URL: p.config.CotacaoServiceURL},
		{Service: "vision", URL: p.config.VisionServiceURL},
		{Service: "ml", URL: p.config.MLServiceURL},
	}

	client := &http.Client{Timeout: 2 * time.Second}
	var wg sync.WaitGroup
	var mu sync.Mutex

	for i := range services {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()

			if p.isCircuitOpen(services[idx].Service) {
				mu.Lock()
				services[idx].Status = "circuit_open"
				services[idx].CircuitOpen = true
				services[idx].Error = "circuit breaker open"
				mu.Unlock()
				return
			}

			if services[idx].URL == "" {
				mu.Lock()
				services[idx].Status = "unconfigured"
				services[idx].Error = "service URL not configured"
				mu.Unlock()
				return
			}

			healthURL := fmt.Sprintf("%s/health", strings.TrimSuffix(services[idx].URL, "/"))
			startedAt := time.Now()
			resp, err := client.Get(healthURL)
			latency := time.Since(startedAt).Milliseconds()

			mu.Lock()
			defer mu.Unlock()
			services[idx].LatencyMS = latency

			if err != nil {
				services[idx].Status = "down"
				services[idx].Error = err.Error()
				return
			}
			defer resp.Body.Close()

			services[idx].HTTPStatus = resp.StatusCode
			if resp.StatusCode >= 200 && resp.StatusCode < 300 {
				services[idx].Status = "up"
			} else {
				services[idx].Status = "degraded"
			}
		}(i)
	}

	wg.Wait()

	upCount := 0
	for _, service := range services {
		if service.Status == "up" {
			upCount++
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"status":         "ok",
		"services_total": len(services),
		"services_up":    upCount,
		"services":       services,
	})
}

func (p *Proxy) isCircuitOpen(service string) bool {
	p.cbMu.Lock()
	defer p.cbMu.Unlock()

	state, ok := p.circuits[service]
	if !ok {
		return false
	}

	if state.openUntil.IsZero() {
		return false
	}

	if time.Now().After(state.openUntil) {
		state.failures = 0
		state.openUntil = time.Time{}
		return false
	}

	return true
}

func (p *Proxy) markFailure(service string) {
	p.cbMu.Lock()
	defer p.cbMu.Unlock()

	state, ok := p.circuits[service]
	if !ok {
		state = &circuitState{}
		p.circuits[service] = state
	}

	state.failures++
	if state.failures >= p.config.CircuitThreshold {
		state.openUntil = time.Now().Add(p.config.CircuitOpenWindow)
		p.config.Logger.Warn("Circuit breaker opened",
			zap.String("service", service),
			zap.Int("failures", state.failures),
			zap.Duration("open_window", p.config.CircuitOpenWindow),
		)
	}
}

func (p *Proxy) markSuccess(service string) {
	p.cbMu.Lock()
	defer p.cbMu.Unlock()

	state, ok := p.circuits[service]
	if !ok {
		return
	}

	state.failures = 0
	state.openUntil = time.Time{}
}

func buildCacheKey(method, fullURL string) string {
	return method + ":" + fullURL
}

func (p *Proxy) getCachedResponse(key string) (cacheEntry, bool) {
	p.cacheMu.RLock()
	entry, ok := p.cache[key]
	p.cacheMu.RUnlock()

	if !ok {
		return cacheEntry{}, false
	}

	if time.Now().After(entry.expiresAt) {
		p.cacheMu.Lock()
		delete(p.cache, key)
		p.cacheMu.Unlock()
		return cacheEntry{}, false
	}

	return entry, true
}

func (p *Proxy) storeCachedResponse(key string, statusCode int, headers http.Header, body []byte) {
	headersCopy := make(http.Header, len(headers))
	for k, values := range headers {
		cloned := make([]string, len(values))
		copy(cloned, values)
		headersCopy[k] = cloned
	}

	bodyCopy := make([]byte, len(body))
	copy(bodyCopy, body)

	p.cacheMu.Lock()
	p.cache[key] = cacheEntry{
		statusCode: statusCode,
		headers:    headersCopy,
		body:       bodyCopy,
		expiresAt:  time.Now().Add(p.config.CacheTTL),
	}
	p.cacheMu.Unlock()
}

func (p *Proxy) invalidateServiceCache(service string) {
	p.cacheMu.Lock()
	defer p.cacheMu.Unlock()

	prefix := ""
	switch service {
	case "animal":
		prefix = "GET:" + strings.TrimSuffix(p.config.AnimalServiceURL, "/") + "/api/v1/animals"
	case "pesagem":
		prefix = "GET:" + strings.TrimSuffix(p.config.PesagemServiceURL, "/") + "/api/v1/pesagens"
	case "cotacao":
		prefix = "GET:" + strings.TrimSuffix(p.config.CotacaoServiceURL, "/") + "/api/v1/cotacoes"
	case "vision":
		prefix = "GET:" + strings.TrimSuffix(p.config.VisionServiceURL, "/") + "/api/v1/vision"
	case "ml":
		prefix = "GET:" + strings.TrimSuffix(p.config.MLServiceURL, "/") + "/api/v1/ml"
	}

	if prefix == "" {
		return
	}

	for k := range p.cache {
		if strings.HasPrefix(k, prefix) {
			delete(p.cache, k)
		}
	}
}

// removeHopByHopHeaders removes hop-by-hop headers from the header map
func removeHopByHopHeaders(header http.Header) {
	hopByHopHeaders := []string{
		"Connection",
		"Keep-Alive",
		"Proxy-Authenticate",
		"Proxy-Authorization",
		"TE",
		"Trailers",
		"Transfer-Encoding",
		"Upgrade",
	}

	for _, headerName := range hopByHopHeaders {
		header.Del(headerName)
	}
}
