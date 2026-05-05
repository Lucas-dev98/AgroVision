package main

import (
	"fmt"
	"net/http"

	"github.com/agrovision/api-gateway/internal/config"
	"github.com/agrovision/api-gateway/internal/router"
)

func main() {
	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		panic(fmt.Sprintf("Failed to load config: %v", err))
	}

	// Setup router
	r := router.SetupRouter(cfg)

	// Start server
	addr := fmt.Sprintf(":%d", cfg.Port)
	cfg.Logger.Info(fmt.Sprintf("Starting API Gateway on %s", addr))

	srv := &http.Server{
		Addr:    addr,
		Handler: r,
	}

	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		cfg.Logger.Fatal(fmt.Sprintf("Failed to start server: %v", err))
	}
}
