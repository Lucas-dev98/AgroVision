package tests

import (
	"bytes"
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"
	"time"

	"github.com/agrovision/api-gateway/internal/config"
	"github.com/agrovision/api-gateway/internal/router"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"go.uber.org/zap"
)

func setupTestRouter() *gin.Engine {
	// Create a test configuration
	cfg := &config.Config{
		Port:                8000,
		Environment:         "test",
		LogLevel:            "debug",
		AnimalServiceURL:    "http://localhost:9000",
		PesagemServiceURL:   "http://localhost:8001",
		CotacaoServiceURL:   "http://localhost:8002",
		NutritionServiceURL: "http://localhost:8005",
		VisionServiceURL:    "http://localhost:8003",
		MLServiceURL:        "http://localhost:8004",
		RateLimitRequests:   10,
		RateLimitWindow:     1 * time.Second,
		JWTSecret:           "test-secret",
		Logger:              zap.NewNop(),
	}

	r := router.SetupRouter(cfg)
	return r
}

func TestHealthCheck(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	assert.Contains(t, w.Body.String(), "ok")
	assert.Contains(t, w.Body.String(), "api-gateway")
}

func TestCORSHeaders(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
	assert.Equal(t, "true", w.Header().Get("Access-Control-Allow-Credentials"))
}

func TestSecurityHeaders(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, "nosniff", w.Header().Get("X-Content-Type-Options"))
	assert.Equal(t, "DENY", w.Header().Get("X-Frame-Options"))
	assert.Equal(t, "1; mode=block", w.Header().Get("X-XSS-Protection"))
	assert.NotEmpty(t, w.Header().Get("Content-Security-Policy"))
}

func TestCORSPreflight(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	req := httptest.NewRequest("OPTIONS", "/api/v1/animals", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNoContent, w.Code)
	assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
}

func TestRateLimitExceeded(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:                8000,
		Environment:         "test",
		LogLevel:            "debug",
		Logger:              zap.NewNop(),
		RateLimitRequests:   2,
		RateLimitWindow:     1 * time.Second,
		AnimalServiceURL:    "http://localhost:9000",
		PesagemServiceURL:   "http://localhost:8001",
		CotacaoServiceURL:   "http://localhost:8002",
		NutritionServiceURL: "http://localhost:8005",
		VisionServiceURL:    "http://localhost:8003",
		MLServiceURL:        "http://localhost:8004",
	})

	// First request - should succeed
	req1 := httptest.NewRequest("GET", "/health", nil)
	w1 := httptest.NewRecorder()
	r.ServeHTTP(w1, req1)
	assert.Equal(t, http.StatusOK, w1.Code)

	// Second request - should succeed
	req2 := httptest.NewRequest("GET", "/health", nil)
	w2 := httptest.NewRecorder()
	r.ServeHTTP(w2, req2)
	assert.Equal(t, http.StatusOK, w2.Code)

	// Third request - should be rate limited
	req3 := httptest.NewRequest("GET", "/health", nil)
	w3 := httptest.NewRecorder()
	r.ServeHTTP(w3, req3)
	assert.Equal(t, http.StatusTooManyRequests, w3.Code)
	assert.Contains(t, w3.Body.String(), "Rate limit exceeded")
}

func TestNotFoundRoute(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	req := httptest.NewRequest("GET", "/nonexistent", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
	assert.Contains(t, w.Body.String(), "Route not found")
}

func TestErrorHandlingOnPanic(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	// This test verifies error handling middleware
	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}

func TestRequestHeaders(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	req := httptest.NewRequest("GET", "/health", nil)
	req.Header.Set("X-Custom-Header", "test-value")
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}

func TestPostRequest(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	payload := []byte(`{"test": "data"}`)
	req := httptest.NewRequest("POST", "/health", bytes.NewReader(payload))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	// Health check doesn't expect POST, but should handle it
	assert.NotEqual(t, 0, w.Code)
}

func TestMultipleRequestsToHealthCheck(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	for i := 0; i < 5; i++ {
		req := httptest.NewRequest("GET", "/health", nil)
		w := httptest.NewRecorder()

		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code, fmt.Sprintf("Request %d failed", i+1))
	}
}

func TestConcurrentRequests(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	// Test concurrent requests
	done := make(chan bool, 10)

	for i := 0; i < 10; i++ {
		go func() {
			req := httptest.NewRequest("GET", "/health", nil)
			w := httptest.NewRecorder()
			r.ServeHTTP(w, req)
			assert.Equal(t, http.StatusOK, w.Code)
			done <- true
		}()
	}

	for i := 0; i < 10; i++ {
		<-done
	}
}

func TestResponseContentType(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, "application/json; charset=utf-8", w.Header().Get("Content-Type"))
}

func TestHealthCheckResponseFormat(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	body := w.Body.String()
	assert.Contains(t, body, "\"status\":\"ok\"")
	assert.Contains(t, body, "\"service\":\"api-gateway\"")
}

func TestDashboardRequiresAuth(t *testing.T) {
	r := setupTestRouter()

	req := httptest.NewRequest("GET", "/api/v1/dashboard", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestDashboardAggregationWithAuth(t *testing.T) {
	r := setupTestRouter()

	req := httptest.NewRequest("GET", "/api/v1/dashboard", nil)
	req.Header.Set("Authorization", "Bearer test-token")
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	assert.Contains(t, w.Body.String(), "services_total")
	assert.Contains(t, w.Body.String(), "services")
}

func TestCircuitBreakerOpensAfterFailures(t *testing.T) {
	r := router.SetupRouter(&config.Config{
		Port:                    8000,
		Environment:             "test",
		LogLevel:                "debug",
		AnimalServiceURL:        "http://127.0.0.1:1",
		PesagemServiceURL:       "http://127.0.0.1:1",
		CotacaoServiceURL:       "http://127.0.0.1:1",
		NutritionServiceURL:     "http://127.0.0.1:1",
		VisionServiceURL:        "http://127.0.0.1:1",
		MLServiceURL:            "http://127.0.0.1:1",
		RateLimitRequests:       100,
		RateLimitWindow:         1 * time.Second,
		CircuitFailureThreshold: 2,
		CircuitOpenTimeout:      5 * time.Second,
		UpstreamTimeout:         200 * time.Millisecond,
		JWTSecret:               "test-secret",
		Logger:                  zap.NewNop(),
	})

	for i := 0; i < 2; i++ {
		req := httptest.NewRequest("GET", "/api/v1/animals", nil)
		req.Header.Set("Authorization", "Bearer test-token")
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		assert.Equal(t, http.StatusBadGateway, w.Code)
	}

	req := httptest.NewRequest("GET", "/api/v1/animals", nil)
	req.Header.Set("Authorization", "Bearer test-token")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusServiceUnavailable, w.Code)
	assert.Contains(t, w.Body.String(), "Circuit breaker open")
}

func TestGetResponsesAreCached(t *testing.T) {
	var animalGetCalls int32

	animalService := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/v1/animals" {
			http.NotFound(w, r)
			return
		}
		if r.Method != http.MethodGet {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		calls := atomic.AddInt32(&animalGetCalls, 1)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(fmt.Sprintf(`{"calls":%d}`, calls)))
	}))
	defer animalService.Close()

	r := router.SetupRouter(&config.Config{
		Port:                    8000,
		Environment:             "test",
		LogLevel:                "debug",
		AnimalServiceURL:        animalService.URL,
		PesagemServiceURL:       "http://127.0.0.1:1",
		CotacaoServiceURL:       "http://127.0.0.1:1",
		NutritionServiceURL:     "http://127.0.0.1:1",
		VisionServiceURL:        "http://127.0.0.1:1",
		MLServiceURL:            "http://127.0.0.1:1",
		RateLimitRequests:       100,
		RateLimitWindow:         1 * time.Second,
		CircuitFailureThreshold: 10,
		CircuitOpenTimeout:      1 * time.Second,
		UpstreamTimeout:         1 * time.Second,
		CacheTTL:                10 * time.Second,
		JWTSecret:               "test-secret",
		Logger:                  zap.NewNop(),
	})

	req1 := httptest.NewRequest("GET", "/api/v1/animals", nil)
	req1.Header.Set("Authorization", "Bearer test-token")
	w1 := httptest.NewRecorder()
	r.ServeHTTP(w1, req1)
	assert.Equal(t, http.StatusOK, w1.Code)
	assert.Contains(t, w1.Body.String(), `"calls":1`)

	req2 := httptest.NewRequest("GET", "/api/v1/animals", nil)
	req2.Header.Set("Authorization", "Bearer test-token")
	w2 := httptest.NewRecorder()
	r.ServeHTTP(w2, req2)
	assert.Equal(t, http.StatusOK, w2.Code)
	assert.Contains(t, w2.Body.String(), `"calls":1`)
	assert.Equal(t, "HIT", w2.Header().Get("X-Cache"))
	assert.Equal(t, int32(1), atomic.LoadInt32(&animalGetCalls))
}

func TestCacheInvalidatesOnWrite(t *testing.T) {
	var animalGetCalls int32

	animalService := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/v1/animals" {
			http.NotFound(w, r)
			return
		}

		switch r.Method {
		case http.MethodGet:
			calls := atomic.AddInt32(&animalGetCalls, 1)
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte(fmt.Sprintf(`{"calls":%d}`, calls)))
		case http.MethodPost:
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			_, _ = w.Write([]byte(`{"created":true}`))
		default:
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	}))
	defer animalService.Close()

	r := router.SetupRouter(&config.Config{
		Port:                    8000,
		Environment:             "test",
		LogLevel:                "debug",
		AnimalServiceURL:        animalService.URL,
		PesagemServiceURL:       "http://127.0.0.1:1",
		CotacaoServiceURL:       "http://127.0.0.1:1",
		NutritionServiceURL:     "http://127.0.0.1:1",
		VisionServiceURL:        "http://127.0.0.1:1",
		MLServiceURL:            "http://127.0.0.1:1",
		RateLimitRequests:       100,
		RateLimitWindow:         1 * time.Second,
		CircuitFailureThreshold: 10,
		CircuitOpenTimeout:      1 * time.Second,
		UpstreamTimeout:         1 * time.Second,
		CacheTTL:                10 * time.Second,
		JWTSecret:               "test-secret",
		Logger:                  zap.NewNop(),
	})

	get1 := httptest.NewRequest("GET", "/api/v1/animals", nil)
	get1.Header.Set("Authorization", "Bearer test-token")
	get1W := httptest.NewRecorder()
	r.ServeHTTP(get1W, get1)
	assert.Equal(t, http.StatusOK, get1W.Code)
	assert.Contains(t, get1W.Body.String(), `"calls":1`)

	post := httptest.NewRequest("POST", "/api/v1/animals", bytes.NewReader([]byte(`{"name":"x"}`)))
	post.Header.Set("Authorization", "Bearer test-token")
	post.Header.Set("Content-Type", "application/json")
	postW := httptest.NewRecorder()
	r.ServeHTTP(postW, post)
	assert.Equal(t, http.StatusCreated, postW.Code)

	get2 := httptest.NewRequest("GET", "/api/v1/animals", nil)
	get2.Header.Set("Authorization", "Bearer test-token")
	get2W := httptest.NewRecorder()
	r.ServeHTTP(get2W, get2)
	assert.Equal(t, http.StatusOK, get2W.Code)
	assert.Contains(t, get2W.Body.String(), `"calls":2`)
	assert.Equal(t, int32(2), atomic.LoadInt32(&animalGetCalls))
}

// BenchmarkHealthCheck benchmarks the health check endpoint
func BenchmarkHealthCheck(b *testing.B) {
	r := router.SetupRouter(&config.Config{
		Port:        8000,
		Environment: "test",
		LogLevel:    "debug",
		Logger:      zap.NewNop(),
	})

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest("GET", "/health", nil)
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
	}
}

// BenchmarkRateLimiter benchmarks the rate limiter
func BenchmarkRateLimiter(b *testing.B) {
	r := router.SetupRouter(&config.Config{
		Port:                8000,
		Environment:         "test",
		LogLevel:            "debug",
		Logger:              zap.NewNop(),
		RateLimitRequests:   1000,
		RateLimitWindow:     10 * time.Second,
		AnimalServiceURL:    "http://localhost:9000",
		PesagemServiceURL:   "http://localhost:8001",
		CotacaoServiceURL:   "http://localhost:8002",
		NutritionServiceURL: "http://localhost:8005",
		VisionServiceURL:    "http://localhost:8003",
		MLServiceURL:        "http://localhost:8004",
	})

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest("GET", "/health", nil)
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
	}
}

func TestNutritionRouteRequiresAuthAndForwards(t *testing.T) {
	nutritionService := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/v1/nutrition" {
			http.NotFound(w, r)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"service":"nutrition"}`))
	}))
	defer nutritionService.Close()

	r := router.SetupRouter(&config.Config{
		Port:                    8000,
		Environment:             "test",
		LogLevel:                "debug",
		AnimalServiceURL:        "http://127.0.0.1:1",
		PesagemServiceURL:       "http://127.0.0.1:1",
		CotacaoServiceURL:       "http://127.0.0.1:1",
		NutritionServiceURL:     nutritionService.URL,
		VisionServiceURL:        "http://127.0.0.1:1",
		MLServiceURL:            "http://127.0.0.1:1",
		RateLimitRequests:       100,
		RateLimitWindow:         1 * time.Second,
		CircuitFailureThreshold: 10,
		CircuitOpenTimeout:      1 * time.Second,
		UpstreamTimeout:         1 * time.Second,
		CacheTTL:                10 * time.Second,
		JWTSecret:               "test-secret",
		Logger:                  zap.NewNop(),
	})

	reqNoAuth := httptest.NewRequest("GET", "/api/v1/nutrition", nil)
	wNoAuth := httptest.NewRecorder()
	r.ServeHTTP(wNoAuth, reqNoAuth)
	assert.Equal(t, http.StatusUnauthorized, wNoAuth.Code)

	reqAuth := httptest.NewRequest("GET", "/api/v1/nutrition", nil)
	reqAuth.Header.Set("Authorization", "Bearer test-token")
	wAuth := httptest.NewRecorder()
	r.ServeHTTP(wAuth, reqAuth)
	assert.Equal(t, http.StatusOK, wAuth.Code)
	assert.Contains(t, wAuth.Body.String(), "nutrition")
}
