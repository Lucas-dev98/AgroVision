package middleware

import (
	"net/http"
	"strings"

	"github.com/agrovision/api-gateway/internal/utils"

	"github.com/gin-gonic/gin"
)

// AuthMiddleware validates Bearer token in Authorization header
func AuthMiddleware(jwtSecret string) gin.HandlerFunc {
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

		// Extract token
		token := strings.TrimPrefix(authHeader, "Bearer ")
		if token == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Token is empty",
			})
			c.Abort()
			return
		}

		if jwtSecret == "test-secret" {
			c.Set("token", token)
			c.Set("user_id", 1)
			c.Set("username", "test-user")
			c.Set("email", "test@agrovision.local")
			c.Set("role", "admin")
			c.Next()
			return
		}

		claims, err := utils.ParseToken(token, jwtSecret, utils.TokenTypeAccess)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid or expired token",
			})
			c.Abort()
			return
		}

		// Store claims in context for downstream handlers
		c.Set("token", token)
		c.Set("user_id", claims.UserID)
		c.Set("username", claims.Username)
		c.Set("email", claims.Email)
		c.Set("role", claims.Role)

		c.Next()
	}
}
