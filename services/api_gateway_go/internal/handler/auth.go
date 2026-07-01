package handler

import (
	"database/sql"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/agrovision/api-gateway/internal/models"
	"github.com/agrovision/api-gateway/internal/repository"
	"github.com/agrovision/api-gateway/internal/utils"

	"github.com/gin-gonic/gin"
)

type AuthHandler struct {
	userRepo  *repository.UserRepository
	jwtSecret string
}

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
	ID       int    `json:"id"`
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

type LogoutRequest struct {
	RefreshToken string `json:"refresh_token"`
}

type RegisterRequest struct {
	CpfCnpj  string `json:"cpf_cnpj" binding:"required"`
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=6"`
	Nome     string `json:"nome"`
}

type RegisterResponse struct {
	UserID  int    `json:"user_id"`
	CpfCnpj string `json:"cpf_cnpj"`
	Email   string `json:"email"`
	Nome    string `json:"nome"`
}

func NewAuthHandler(jwtSecret string, db ...*sql.DB) *AuthHandler {
	var conn *sql.DB
	if len(db) > 0 {
		conn = db[0]
	}
	if jwtSecret == "" {
		jwtSecret = "change-me-in-production"
	}

	return &AuthHandler{
		userRepo:  repository.NewUserRepository(conn),
		jwtSecret: jwtSecret,
	}
}

func (h *AuthHandler) buildLoginResponse(user *models.User) (LoginResponse, error) {
	accessToken, err := utils.GenerateToken(user, h.jwtSecret, utils.TokenTypeAccess, 24*time.Hour)
	if err != nil {
		return LoginResponse{}, err
	}

	refreshToken, err := utils.GenerateToken(user, h.jwtSecret, utils.TokenTypeRefresh, 7*24*time.Hour)
	if err != nil {
		return LoginResponse{}, err
	}

	if err := h.userRepo.StoreRefreshToken(user.ID, refreshToken, time.Now().Add(7*24*time.Hour)); err != nil {
		return LoginResponse{}, err
	}

	return LoginResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		TokenType:    "Bearer",
		ExpiresIn:    86400,
		User: User{
			ID:       user.ID,
			Username: user.Username,
			Email:    user.Email,
		},
	}, nil
}

// Register endpoint - creates a new user account
func (h *AuthHandler) Register(c *gin.Context) {
	var req RegisterRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid request body. cpf_cnpj, email and password are required.",
		})
		return
	}

	passwordHash, err := utils.HashPassword(req.Password)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to process password",
		})
		return
	}

	newUser := &models.User{
		Username:     strings.TrimSpace(req.CpfCnpj),
		Email:        strings.TrimSpace(strings.ToLower(req.Email)),
		PasswordHash: passwordHash,
		FullName:     strings.TrimSpace(req.Nome),
		Role:         "user",
		IsActive:     true,
	}

	if err := h.userRepo.Create(newUser); err != nil {
		if strings.Contains(err.Error(), "already exists") {
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to create user",
		})
		return
	}

	c.JSON(http.StatusCreated, RegisterResponse{
		UserID:  newUser.ID,
		CpfCnpj: newUser.Username,
		Email:   newUser.Email,
		Nome:    newUser.FullName,
	})
}

// Login endpoint - validates credentials against database and returns a Bearer token
func (h *AuthHandler) Login(c *gin.Context) {
	var req LoginRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid request body. Username and password required.",
		})
		return
	}

	// Validate input
	if req.Username == "" || req.Password == "" {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Invalid credentials",
		})
		return
	}

	// Get user from database
	user, err := h.userRepo.GetByUsername(req.Username)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Invalid credentials",
		})
		return
	}

	// Verify password
	if !utils.VerifyPassword(req.Password, user.PasswordHash) {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Invalid credentials",
		})
		return
	}

	response, err := h.buildLoginResponse(user)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate tokens"})
		return
	}

	c.JSON(http.StatusOK, response)
}

// Logout endpoint
func (h *AuthHandler) Logout(c *gin.Context) {
	var req LogoutRequest
	_ = c.ShouldBindJSON(&req)

	if req.RefreshToken != "" {
		_ = h.userRepo.RevokeRefreshToken(req.RefreshToken)
	}

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

	if req.RefreshToken == "" {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "Invalid refresh token",
		})
		return
	}

	claims, err := utils.ParseToken(req.RefreshToken, h.jwtSecret, utils.TokenTypeRefresh)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid refresh token"})
		return
	}

	userIDFromStore, err := h.userRepo.ValidateRefreshToken(req.RefreshToken)
	if err != nil || userIDFromStore != claims.UserID {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid refresh token"})
		return
	}

	user, err := h.userRepo.GetByID(claims.UserID)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not found"})
		return
	}

	_ = h.userRepo.RevokeRefreshToken(req.RefreshToken)

	response, err := h.buildLoginResponse(user)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate tokens"})
		return
	}

	c.JSON(http.StatusOK, RefreshResponse{
		AccessToken:  response.AccessToken,
		RefreshToken: response.RefreshToken,
		TokenType:    response.TokenType,
		ExpiresIn:    response.ExpiresIn,
	})
}

// GetProfile endpoint - returns current user profile
func (h *AuthHandler) GetProfile(c *gin.Context) {
	userIDRaw, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	userID, ok := userIDRaw.(int)
	if !ok {
		if s, castOk := userIDRaw.(string); castOk {
			parsed, err := strconv.Atoi(s)
			if err != nil {
				c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
				return
			}
			userID = parsed
		} else {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
			return
		}
	}

	user, err := h.userRepo.GetByID(userID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"user": User{
			ID:       user.ID,
			Username: user.Username,
			Email:    user.Email,
		},
	})
}
