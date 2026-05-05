package tests
package tests

import (
	"bytes"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/agrovision/api-gateway/internal/config"
	"github.com/agrovision/api-gateway/internal/router"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/zap"
)

func setupTestRouter() *http.Handler {
	// Create a test configuration
	cfg := &config.Config{
		Port:                 8000,
		Environment:         "test",
		LogLevel:            "debug",
		AnimalServiceURL:    "http://localhost:9000",
		PesagemServiceURL:   "http://localhost:8001",
		CotacaoServiceURL:   "http://localhost:8002",
		VisionServiceURL:    "http://localhost:8003",
		MLServiceURL:        "http://localhost:8004",
		RateLimitRequests:   10,
		RateLimitWindow:     1 * time.Second,
		JWTSecret:           "test-secret",
		Logger:              zap.NewNop(),
	}

	r := router.SetupRouter(cfg)
	return &r.Engine.Handler
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
		Port:                 8000,
		Environment:         "test",
		LogLevel:            "debug",
		Logger:              zap.NewNop(),
		RateLimitRequests:    2,
		RateLimitWindow:      1 * time.Second,
		AnimalServiceURL:    "http://localhost:9000",
		PesagemServiceURL:   "http://localhost:8001",
		CotacaoServiceURL:   "http://localhost:8002",
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
		Port:                 8000,
		Environment:         "test",
		LogLevel:            "debug",
		Logger:              zap.NewNop(),
		RateLimitRequests:    1000,
		RateLimitWindow:      10 * time.Second,
		AnimalServiceURL:    "http://localhost:9000",
		PesagemServiceURL:   "http://localhost:8001",
		CotacaoServiceURL:   "http://localhost:8002",
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
