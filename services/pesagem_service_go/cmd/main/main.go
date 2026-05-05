package main

import (
	"fmt"

	"github.com/agrovision/pesagem-service/internal/config"
	"github.com/agrovision/pesagem-service/internal/db"
	"github.com/agrovision/pesagem-service/internal/handler"
	"github.com/agrovision/pesagem-service/internal/repository"
	"github.com/agrovision/pesagem-service/internal/router"
	"github.com/agrovision/pesagem-service/internal/service"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func main() {
	cfg := config.Load()
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	logger.Info("Starting Pesagem Service", zap.String("environment", cfg.Environment))

	// Connect to database
	database, err := db.Connect(cfg.DatabaseURL)
	if err != nil {
		logger.Fatal("Failed to connect to database", zap.Error(err))
	}
	defer database.Close()

	logger.Info("Database connected successfully")

	// Initialize repository, service, and handler
	pesagemRepository := repository.NewPesagemRepository(database)
	pesagemService := service.NewPesagemService(pesagemRepository, logger)
	pesagemHandler := handler.NewPesagemHandler(pesagemService, logger)

	// Setup router
	r := gin.Default()
	router.SetupRoutes(r, pesagemHandler)

	// Start server
	port := fmt.Sprintf(":%s", cfg.Port)
	logger.Info("Server starting", zap.String("port", cfg.Port))
	if err := r.Run(port); err != nil {
		logger.Fatal("Server failed to start", zap.Error(err))
	}
}
