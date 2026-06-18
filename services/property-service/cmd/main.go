package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/agrovision/property-service/internal/handler"
	"github.com/agrovision/property-service/internal/repository"
	"github.com/gorilla/mux"
	_ "github.com/lib/pq"
)

func main() {
	demoMode := getEnv("DEMO_MODE", "true") == "true"

	var repo *repository.PropertyRepository

	if !demoMode {
		dbHost := getEnv("DB_HOST", "localhost")
		dbPort := getEnv("DB_PORT", "5432")
		dbUser := getEnv("DB_USER", "postgres")
		dbPassword := getEnv("DB_PASSWORD", "agrovision")
		dbName := getEnv("DB_NAME", "agrovision_db")

		psqlInfo := fmt.Sprintf(
			"host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
			dbHost,
			dbPort,
			dbUser,
			dbPassword,
			dbName,
		)

		db, err := sql.Open("postgres", psqlInfo)
		if err != nil {
			log.Fatalf("failed to open database connection: %v", err)
		}
		defer db.Close()

		if err = db.Ping(); err != nil {
			log.Fatalf("failed to ping database: %v", err)
		}
		log.Println("connected to PostgreSQL")
		repo = repository.NewPropertyRepository(db)
	} else {
		log.Println("running in DEMO mode (no database)")
		repo = repository.NewPropertyRepository(nil)
	}

	propertyHandler := handler.NewPropertyHandler(repo)

	router := mux.NewRouter()
	router.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		mode := "database"
		if demoMode {
			mode = "demo"
		}
		_, _ = w.Write([]byte(fmt.Sprintf(`{"status":"ok","mode":"%s"}`, mode)))
	}).Methods(http.MethodGet)
	propertyHandler.RegisterRoutes(router)

	port := getEnv("SERVICE_PORT", "8081")
	log.Printf("property-service listening on :%s", port)
	if err := http.ListenAndServe(":"+port, router); err != nil {
		log.Fatalf("server failed: %v", err)
	}
}

func getEnv(key, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}
