package main
package main

import (
	"fmt"
	"net/http"

	"github.com/agrovision/vision-service/internal/config"
	"github.com/agrovision/vision-service/internal/router"
	"github.com/joho/godotenv"
)

func main() {
	// Load .env file if it exists
	_ = godotenv.Load()

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		panic(fmt.Sprintf("Failed to load config: %v", err))
	}

	// Setup router
	r := router.SetupRouter()

	// Start server
	addr := fmt.Sprintf("%s:%d", cfg.Hostname, cfg.Port)
	fmt.Printf("Starting Vision Service on %s\n", addr)

	srv := &http.Server{
		Addr:    addr,
		Handler: r,
	}

	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		fmt.Printf("Failed to start server: %v\n", err)
	}
}
