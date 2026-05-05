package main

import (
	"log"

	"github.com/agrovision/animal-service/internal/config"
	"github.com/agrovision/animal-service/internal/db"
	"github.com/agrovision/animal-service/internal/handler"
	"github.com/agrovision/animal-service/internal/repository"
	"github.com/agrovision/animal-service/internal/router"
	"github.com/agrovision/animal-service/internal/service"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Setup logger
	logger, err := zap.NewProduction()
	if err != nil {
		log.Fatalf("Failed to create logger: %v", err)
	}
	defer logger.Sync()

	// Connect to database
	database, err := db.Connect(cfg.DatabaseURL)
	if err != nil {
		logger.Fatal("Failed to connect to database", zap.Error(err))
	}
	defer database.Close()

	logger.Info("Connected to database")

	// Initialize dependencies
	animalRepo := repository.NewAnimalRepository(database)
	animalService := service.NewAnimalService(animalRepo, logger)
	animalHandler := handler.NewAnimalHandler(animalService, logger)

	// Setup router
	r := gin.Default()
	router.SetupRoutes(r, animalHandler)

	// Start server
	port := cfg.Port
	logger.Info("Starting Animal Service", zap.String("port", port))
	if err := r.Run(":" + port); err != nil {
		logger.Fatal("Server failed", zap.Error(err))
	}
}
