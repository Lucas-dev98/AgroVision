package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type AuthHandler struct{}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type LoginResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"`
	User         User   `json:"user"`
}

type User struct {
	ID       string `json:"id"`
	Username string `json:"username"`
	Email    string `json:"email"`
}

type RefreshRequest struct {
	RefreshToken string `json:"refresh_token" binding:"required"`
}

type RefreshResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"`
}

func NewAuthHandler() *AuthHandler {
	return &AuthHandler{}
}

// Login endpoint - returns a Bearer token for API access
func (h *AuthHandler) Login(c *gin.Context) {
	var req LoginRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid request body. Username and password required.",
		})
		return
	}

	// For development: accept any non-empty username/password
	if req.Username == "" || req.Password == "" {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Invalid credentials",
		})
		return
	}

	// Generate simple tokens (in production, use proper JWT)
	accessToken := uuid.New().String()
	refreshToken := uuid.New().String()
	expiresIn := 86400 // 24 hours in seconds

	response := LoginResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		TokenType:    "Bearer",
		ExpiresIn:    expiresIn,
		User: User{
			ID:       uuid.New().String(),
			Username: req.Username,
			Email:    req.Username + "@agrovision.local",
		},
	}

	c.JSON(http.StatusOK, response)
}

// Logout endpoint
func (h *AuthHandler) Logout(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message": "Logout successful",
	})
}

// Refresh endpoint - refreshes access token using refresh token
func (h *AuthHandler) Refresh(c *gin.Context) {
	var req RefreshRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid request body. Refresh token required.",
		})
		return
	}

	// For development: accept any non-empty refresh token
	if req.RefreshToken == "" {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Invalid refresh token",
		})
		return
	}

	// Generate new tokens
	accessToken := uuid.New().String()
	refreshToken := uuid.New().String()
	expiresIn := 86400 // 24 hours in seconds

	response := RefreshResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		TokenType:    "Bearer",
		ExpiresIn:    expiresIn,
	}

	c.JSON(http.StatusOK, response)
}

// GetProfile endpoint - returns current user profile
func (h *AuthHandler) GetProfile(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"user": User{
			ID:       uuid.New().String(),
			Username: "user",
			Email:    "user@agrovision.local",
		},
	})
}
