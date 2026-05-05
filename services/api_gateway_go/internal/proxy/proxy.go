package proxy

import (
	"io"
	"net/http"
	"net/url"
	"strings"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type ProxyConfig struct {
	AnimalServiceURL  string
	PesagemServiceURL string
	CotacaoServiceURL string
	VisionServiceURL  string
	MLServiceURL      string
	Logger            *zap.Logger
}

type Proxy struct {
	config ProxyConfig
}

func NewProxy(config ProxyConfig) *Proxy {
	return &Proxy{config: config}
}

func (p *Proxy) ForwardRequest(c *gin.Context, targetURL string) {
	// Create a new request with the same method and body
	req, err := http.NewRequest(c.Request.Method, targetURL, c.Request.Body)
	if err != nil {
		p.config.Logger.Error("Failed to create proxy request", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create proxy request"})
		return
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
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		p.config.Logger.Error("Failed to forward request", zap.Error(err), zap.String("target_url", targetURL))
		c.JSON(http.StatusBadGateway, gin.H{"error": "Failed to forward request to upstream service"})
		return
	}
	defer resp.Body.Close()

	// Copy response headers
	for key, values := range resp.Header {
		for _, value := range values {
			c.Writer.Header().Add(key, value)
		}
	}

	// Remove hop-by-hop headers from response
	removeHopByHopHeaders(resp.Header)

	// Set status code
	c.Writer.WriteHeader(resp.StatusCode)

	// Copy response body
	if _, err := io.Copy(c.Writer, resp.Body); err != nil {
		p.config.Logger.Error("Failed to copy response body", zap.Error(err))
	}
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

	p.config.Logger.Debug("Forwarding request",
		zap.String("service", targetService),
		zap.String("path", path),
		zap.String("target_url", fullURL),
	)

	p.ForwardRequest(c, fullURL)
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
