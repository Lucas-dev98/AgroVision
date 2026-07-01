package models

import (
	"time"
)

// User model
type User struct {
	ID           int       `db:"id" json:"id"`
	Username     string    `db:"username" json:"username"`
	Email        string    `db:"email" json:"email"`
	PasswordHash string    `db:"password_hash" json:"-"` // Never expose password hash
	FullName     string    `db:"full_name" json:"full_name"`
	Role         string    `db:"role" json:"role"` // admin, operator, viewer, user
	IsActive     bool      `db:"is_active" json:"is_active"`
	CreatedAt    time.Time `db:"created_at" json:"created_at"`
	UpdatedAt    time.Time `db:"updated_at" json:"updated_at"`
}

// UserCreate DTO for creating a user
type UserCreate struct {
	Username string `json:"username" binding:"required,min=3,max=100"`
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=6"`
	FullName string `json:"full_name" binding:"max=100"`
	Role     string `json:"role" binding:"oneof=admin operator viewer user"`
}

// UserResponse DTO for returning user data
type UserResponse struct {
	ID        int       `json:"id"`
	Username  string    `json:"username"`
	Email     string    `json:"email"`
	FullName  string    `json:"full_name"`
	Role      string    `json:"role"`
	IsActive  bool      `json:"is_active"`
	CreatedAt time.Time `json:"created_at"`
}

// UserUpdate DTO for updating a user
type UserUpdate struct {
	Email    string `json:"email" binding:"email"`
	FullName string `json:"full_name"`
	Role     string `json:"role" binding:"oneof=admin operator viewer user"`
	IsActive bool   `json:"is_active"`
}

// ToResponse converts User to UserResponse
func (u *User) ToResponse() UserResponse {
	return UserResponse{
		ID:        u.ID,
		Username:  u.Username,
		Email:     u.Email,
		FullName:  u.FullName,
		Role:      u.Role,
		IsActive:  u.IsActive,
		CreatedAt: u.CreatedAt,
	}
}
