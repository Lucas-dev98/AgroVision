package main

import (
	"fmt"

	"github.com/agrovision/cotacao-service/internal/config"
	"github.com/agrovision/cotacao-service/internal/db"
	"github.com/agrovision/cotacao-service/internal/handler"
	"github.com/agrovision/cotacao-service/internal/repository"
	"github.com/agrovision/cotacao-service/internal/router"
	"github.com/agrovision/cotacao-service/internal/service"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func main() {
	cfg := config.Load()
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	logger.Info("Starting Cotacao Service", zap.String("environment", cfg.Environment))

	// Connect to database
	database, err := db.Connect(cfg.DatabaseURL)
	if err != nil {
		logger.Fatal("Failed to connect to database", zap.Error(err))
	}
	defer database.Close()

	logger.Info("Database connected successfully")

	// Initialize repository, service, and handler
	cotacaoRepository := repository.NewCotacaoRepository(database)
	cotacaoService := service.NewCotacaoService(cotacaoRepository, logger)
	cotacaoHandler := handler.NewCotacaoHandler(cotacaoService, logger)

	// Setup router
	r := gin.Default()
	router.SetupRoutes(r, cotacaoHandler)

	// Start server
	port := fmt.Sprintf(":%s", cfg.Port)
	logger.Info("Server starting", zap.String("port", cfg.Port))
	if err := r.Run(port); err != nil {
		logger.Fatal("Server failed to start", zap.Error(err))
	}
}
