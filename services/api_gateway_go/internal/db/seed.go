package db

import (
	"database/sql"

	"github.com/agrovision/api-gateway/internal/models"
	"github.com/agrovision/api-gateway/internal/repository"
	"github.com/agrovision/api-gateway/internal/utils"
)

// SeedUsers initializes default users in the database
func SeedUsers(db *sql.DB) error {
	userRepo := repository.NewUserRepository(db)

	// Check if admin user already exists
	_, err := userRepo.GetByUsername("admin")
	if err == nil {
		// Admin already exists, skip seeding
		return nil
	}

	// Hash password for admin
	passwordHash, err := utils.HashPassword("password123")
	if err != nil {
		return err
	}

	// Create admin user
	adminUser := &models.User{
		Username:     "admin",
		Email:        "admin@agrovision.local",
		PasswordHash: passwordHash,
		FullName:     "Administrator",
		Role:         "admin",
		IsActive:     true,
	}

	if err := userRepo.Create(adminUser); err != nil {
		// Ignore if user already exists (race condition)
		return nil
	}

	// Create operator user
	operatorHash, err := utils.HashPassword("operator123")
	if err != nil {
		return err
	}

	operatorUser := &models.User{
		Username:     "operator",
		Email:        "operator@agrovision.local",
		PasswordHash: operatorHash,
		FullName:     "Operador",
		Role:         "operator",
		IsActive:     true,
	}

	if err := userRepo.Create(operatorUser); err != nil {
		return nil
	}

	// Create viewer user
	viewerHash, err := utils.HashPassword("viewer123")
	if err != nil {
		return err
	}

	viewerUser := &models.User{
		Username:     "viewer",
		Email:        "viewer@agrovision.local",
		PasswordHash: viewerHash,
		FullName:     "Visualizador",
		Role:         "viewer",
		IsActive:     true,
	}

	if err := userRepo.Create(viewerUser); err != nil {
		return nil
	}

	return nil
}
