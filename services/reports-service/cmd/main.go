package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/agrovision/reports-service/internal/handler"
	"github.com/agrovision/reports-service/internal/repository"
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
		log.Println("running in DEMO mode (no database)")
	}

	repo := repository.NewReportRepository(db)
	reportHandler := handler.NewReportHandler(repo)

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
	reportHandler.RegisterRoutes(router)

	port := getEnv("SERVICE_PORT", "8086")
	log.Printf("reports-service listening on :%s", port)
	if listenErr := http.ListenAndServe(":"+port, router); listenErr != nil {
		log.Fatalf("server failed: %v", listenErr)
	}
}

func getEnv(key, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}
