package config

import (
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	DatabaseURL string
	Port        string
	LogLevel    string
	Environment string
	JWTSecret   string
}

func Load() *Config {
	godotenv.Load()

	return &Config{
		DatabaseURL: getEnv("DATABASE_URL", "postgresql://agrovision:agrovision@db:5432/agrovision?sslmode=disable"),
		Port:        getEnv("PORT", "8000"),
		LogLevel:    getEnv("LOG_LEVEL", "info"),
		Environment: getEnv("ENVIRONMENT", "development"),
		JWTSecret:   getEnv("JWT_SECRET", "dev-secret-key"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
