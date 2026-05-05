package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

// AuthMiddleware validates Bearer token in Authorization header
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")

		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Missing authorization header",
			})
			c.Abort()
			return
		}

		// Check if Bearer token
		if !strings.HasPrefix(authHeader, "Bearer ") {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid authorization header format. Expected: Bearer <token>",
			})
			c.Abort()
			return
		}

		// Extract token (just validate it exists for now)
		token := strings.TrimPrefix(authHeader, "Bearer ")
		if token == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Token is empty",
			})
			c.Abort()
			return
		}

		// Store token in context for potential later use
		c.Set("token", token)

		c.Next()
	}
}
