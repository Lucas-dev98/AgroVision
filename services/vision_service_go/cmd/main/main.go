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

	"agrovision/vision-service/internal/config"
	"agrovision/vision-service/internal/db"
	"agrovision/vision-service/internal/router"
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

	// Connect to MongoDB
	var mongoConn *db.MongoConnection
	mongoConn, err = db.NewMongoConnection(cfg.MongoURI, cfg.MongoDBName)
	if err != nil {
		fmt.Printf("⚠ Warning: MongoDB connection failed: %v\n", err)
		fmt.Println("⚠ Continuing without persistent storage (in-memory only)")
	} else {
		defer func() {
			ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
			defer cancel()
			mongoConn.Close(ctx)
		}()
	}

	// Setup router
	r := router.SetupRouter(mongoConn)

	// Start server
	addr := fmt.Sprintf("%s:%d", cfg.Hostname, cfg.Port)
	fmt.Printf("Starting Vision Service on %s\n", addr)
	fmt.Println(cfg)

	srv := &http.Server{
		Addr:    addr,
		Handler: r,
	}

	// Graceful shutdown
	go func() {
		sigint := make(chan os.Signal, 1)
		signal.Notify(sigint, syscall.SIGINT, syscall.SIGTERM)
		<-sigint

		fmt.Println("\nShutting down server...")
		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()

		if err := srv.Shutdown(ctx); err != nil {
			fmt.Printf("Server forced to shutdown: %v\n", err)
		}
	}()

	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		fmt.Printf("Failed to start server: %v\n", err)
	}
}
