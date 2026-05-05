package config

import (
	"os"
	"strconv"
	"time"

	"github.com/joho/godotenv"
	"go.uber.org/zap"
)

type Config struct {
	Port              int
	Environment       string
	LogLevel          string
	AnimalServiceURL  string
	PesagemServiceURL string
	CotacaoServiceURL string
	VisionServiceURL  string
	MLServiceURL      string
	RateLimitRequests int
	RateLimitWindow   time.Duration
	JWTSecret         string
	Logger            *zap.Logger
}

func Load() (*Config, error) {
	// Load .env file if it exists
	_ = godotenv.Load(".env")

	// Initialize logger
	var logger *zap.Logger
	var err error

	logLevel := os.Getenv("LOG_LEVEL")
	if logLevel == "" {
		logLevel = "info"
	}

	if logLevel == "debug" {
		logger, err = zap.NewDevelopment()
	} else {
		logger, err = zap.NewProduction()
	}

	if err != nil {
		panic(err)
	}
	defer logger.Sync()

	port := 8000
	if p := os.Getenv("PORT"); p != "" {
		if parsed, err := strconv.Atoi(p); err == nil {
			port = parsed
		}
	}

	rateLimitRequests := 100
	if r := os.Getenv("RATE_LIMIT_REQUESTS"); r != "" {
		if parsed, err := strconv.Atoi(r); err == nil {
			rateLimitRequests = parsed
		}
	}

	rateLimitWindow := time.Minute
	if w := os.Getenv("RATE_LIMIT_WINDOW"); w != "" {
		if parsed, err := time.ParseDuration(w); err == nil {
			rateLimitWindow = parsed
		}
	}

	return &Config{
		Port:              port,
		Environment:       os.Getenv("ENVIRONMENT"),
		LogLevel:          logLevel,
		AnimalServiceURL:  os.Getenv("ANIMAL_SERVICE_URL"),
		PesagemServiceURL: os.Getenv("PESAGEM_SERVICE_URL"),
		CotacaoServiceURL: os.Getenv("COTACAO_SERVICE_URL"),
		VisionServiceURL:  os.Getenv("VISION_SERVICE_URL"),
		MLServiceURL:      os.Getenv("ML_SERVICE_URL"),
		RateLimitRequests: rateLimitRequests,
		RateLimitWindow:   rateLimitWindow,
		JWTSecret:         os.Getenv("JWT_SECRET"),
		Logger:            logger,
	}, nil
}
