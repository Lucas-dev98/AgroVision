package main
package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/agrovision/ml-service/internal/config"
	"github.com/agrovision/ml-service/internal/db"
	"github.com/agrovision/ml-service/internal/router"
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

	fmt.Printf("Config loaded: %s\n", cfg.String())

	// Connect to MongoDB
	mongoConn, err := db.NewMongoConnection(cfg.MongoURI, cfg.MongoDBName)
	if err != nil {
		fmt.Printf("Warning: MongoDB connection failed: %v\n", err)
		fmt.Println("Continuing without MongoDB persistence...")
	} else {
		fmt.Println("MongoDB connected successfully")
		defer mongoConn.Close()
	}

	// Setup router with MongoDB and JWT
	r := router.SetupRouter(mongoConn, cfg.JWTSecret)

	// Start server
	addr := fmt.Sprintf("%s:%d", cfg.Hostname, cfg.Port)
	fmt.Printf("Starting ML Service on %s\n", addr)

	srv := &http.Server{
		Addr:    addr,
		Handler: r,
	}

	// Graceful shutdown
	go func() {
		sigint := make(chan os.Signal, 1)
		signal.Notify(sigint, syscall.SIGINT, syscall.SIGTERM)
		<-sigint

		fmt.Println("\nShutting down ML Service...")
		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()

		if err := srv.Shutdown(ctx); err != nil {
			fmt.Printf("Shutdown error: %v\n", err)
		}
	}()

	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		fmt.Printf("Failed to start server: %v\n", err)
	}
}
