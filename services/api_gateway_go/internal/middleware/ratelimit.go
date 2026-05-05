package middleware

import (
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type RateLimitConfig struct {
	RequestsPerWindow int
	Window            time.Duration
}

type RateLimiter struct {
	config   RateLimitConfig
	limiters map[string]*clientLimiter
	mu       sync.RWMutex
	logger   *zap.Logger
}

type clientLimiter struct {
	requests []time.Time
	mu       sync.Mutex
}

func NewRateLimiter(config RateLimitConfig, logger *zap.Logger) *RateLimiter {
	rl := &RateLimiter{
		config:   config,
		limiters: make(map[string]*clientLimiter),
		logger:   logger,
	}

	// Cleanup expired requests every minute
	go func() {
		ticker := time.NewTicker(time.Minute)
		defer ticker.Stop()
		for range ticker.C {
			rl.cleanup()
		}
	}()

	return rl
}

func (rl *RateLimiter) Middleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		clientID := c.ClientIP()

		if !rl.allow(clientID) {
			rl.logger.Warn("Rate limit exceeded", zap.String("client_ip", clientID))
			c.JSON(http.StatusTooManyRequests, gin.H{
				"error":       "Rate limit exceeded",
				"retry_after": int(rl.config.Window.Seconds()),
			})
			c.Abort()
			return
		}

		c.Next()
	}
}

func (rl *RateLimiter) allow(clientID string) bool {
	rl.mu.Lock()
	limiter, exists := rl.limiters[clientID]
	if !exists {
		limiter = &clientLimiter{
			requests: make([]time.Time, 0),
		}
		rl.limiters[clientID] = limiter
	}
	rl.mu.Unlock()

	limiter.mu.Lock()
	defer limiter.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-rl.config.Window)

	// Remove old requests outside the window
	validRequests := make([]time.Time, 0)
	for _, reqTime := range limiter.requests {
		if reqTime.After(windowStart) {
			validRequests = append(validRequests, reqTime)
		}
	}

	limiter.requests = validRequests

	// Check if we're within the limit
	if len(limiter.requests) < rl.config.RequestsPerWindow {
		limiter.requests = append(limiter.requests, now)
		return true
	}

	return false
}

func (rl *RateLimiter) cleanup() {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-rl.config.Window * 2) // Keep data for 2 windows

	for clientID, limiter := range rl.limiters {
		limiter.mu.Lock()
		if len(limiter.requests) == 0 {
			limiter.mu.Unlock()
			delete(rl.limiters, clientID)
			continue
		}

		// Remove old requests
		validRequests := make([]time.Time, 0)
		for _, reqTime := range limiter.requests {
			if reqTime.After(windowStart) {
				validRequests = append(validRequests, reqTime)
			}
		}
		limiter.requests = validRequests
		limiter.mu.Unlock()

		// Remove empty limiters
		if len(limiter.requests) == 0 {
			rl.mu.Lock()
			delete(rl.limiters, clientID)
			rl.mu.Unlock()
		}
	}
}

// CORSMiddleware handles CORS headers
func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE, PATCH")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

// LoggingMiddleware logs requests
func LoggingMiddleware(logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		startTime := time.Now()

		c.Next()

		duration := time.Since(startTime)
		statusCode := c.Writer.Status()

		logger.Info("Request processed",
			zap.String("method", c.Request.Method),
			zap.String("path", c.Request.URL.Path),
			zap.Int("status", statusCode),
			zap.Duration("duration", duration),
			zap.String("client_ip", c.ClientIP()),
		)
	}
}

// ErrorHandlingMiddleware catches and logs errors
func ErrorHandlingMiddleware(logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				logger.Error("Panic recovered",
					zap.Any("error", err),
					zap.String("path", c.Request.URL.Path),
				)
				c.JSON(http.StatusInternalServerError, gin.H{
					"error": "Internal server error",
				})
			}
		}()
		c.Next()
	}
}

// HeaderMiddleware adds common security headers
func HeaderMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("X-Content-Type-Options", "nosniff")
		c.Writer.Header().Set("X-Frame-Options", "DENY")
		c.Writer.Header().Set("X-XSS-Protection", "1; mode=block")
		c.Writer.Header().Set("Content-Security-Policy", "default-src 'self'")
		c.Next()
	}
}
