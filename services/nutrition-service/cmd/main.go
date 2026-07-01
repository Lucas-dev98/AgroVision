package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/agrovision/nutrition-service/internal/handler"
	"github.com/agrovision/nutrition-service/internal/repository"
	"github.com/gorilla/mux"
	_ "github.com/lib/pq"
)

func main() {
	demoMode := getEnv("DEMO_MODE", "true") == "true"
	var db *sql.DB

	if !demoMode {
		dbHost := getEnv("DB_HOST", "localhost")
		dbPort := getEnv("DB_PORT", "5432")
		dbUser := getEnv("DB_USER", "postgres")
		dbPassword := getEnv("DB_PASSWORD", "agrovision")
		dbName := getEnv("DB_NAME", "agrovision_db")

		psqlInfo := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
			dbHost, dbPort, dbUser, dbPassword, dbName)

		var err error
		db, err = sql.Open("postgres", psqlInfo)
		if err != nil {
			log.Fatalf("failed to open database connection: %v", err)
		}
		defer db.Close()

		if err = db.Ping(); err != nil {
			log.Fatalf("failed to ping database: %v", err)
		}
		log.Println("connected to PostgreSQL")
	} else {
		log.Println("running in DEMO mode (in-memory repository)")
	}

	repo := repository.NewNutritionRepository(db)
	nutritionHandler := handler.NewNutritionHandler(repo)

	router := mux.NewRouter()
	router.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ok","service":"nutrition-service"}`))
	}).Methods(http.MethodGet)
	nutritionHandler.RegisterRoutes(router)

	port := getEnv("SERVICE_PORT", "8088")
	log.Printf("nutrition-service listening on :%s", port)
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
