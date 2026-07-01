package main

import (
	"fmt"
	"net/http"

	"github.com/agrovision/api-gateway/internal/config"
	"github.com/agrovision/api-gateway/internal/db"
	"github.com/agrovision/api-gateway/internal/router"
)

func main() {
	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		panic(fmt.Sprintf("Failed to load config: %v", err))
	}

	postgresDB, err := db.ConnectPostgres(
		cfg.DBHost,
		cfg.DBPort,
		cfg.DBUser,
		cfg.DBPassword,
		cfg.DBName,
		cfg.DBSSLMode,
	)
	if err != nil {
		cfg.Logger.Fatal(fmt.Sprintf("Failed to connect to database: %v", err))
	}
	defer postgresDB.Close()

	if err := db.EnsureUsersSchema(postgresDB); err != nil {
		cfg.Logger.Fatal(fmt.Sprintf("Failed to ensure users schema: %v", err))
	}

	if err := db.SeedUsers(postgresDB); err != nil {
		cfg.Logger.Fatal(fmt.Sprintf("Failed to seed users: %v", err))
	}

	// Setup router
	r := router.SetupRouter(cfg, postgresDB)

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
