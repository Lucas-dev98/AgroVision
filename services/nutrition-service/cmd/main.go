package main

import (
	"log"
	"net/http"
	"os"

	"github.com/agrovision/nutrition-service/internal/handler"
	"github.com/agrovision/nutrition-service/internal/repository"
	"github.com/gorilla/mux"
)

func main() {
	repo := repository.NewNutritionRepository()
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
