package config

import (
	"os"
	"strconv"
	"time"

	"github.com/joho/godotenv"
	"go.uber.org/zap"
)

type Config struct {
	Port                    int
	Environment             string
	LogLevel                string
	AnimalServiceURL        string
	PesagemServiceURL       string
	CotacaoServiceURL       string
	NutritionServiceURL     string
	VisionServiceURL        string
	MLServiceURL            string
	RateLimitRequests       int
	RateLimitWindow         time.Duration
	CircuitFailureThreshold int
	CircuitOpenTimeout      time.Duration
	UpstreamTimeout         time.Duration
	CacheTTL                time.Duration
	JWTSecret               string
	Logger                  *zap.Logger
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

	circuitFailureThreshold := 3
	if c := os.Getenv("CIRCUIT_FAILURE_THRESHOLD"); c != "" {
		if parsed, err := strconv.Atoi(c); err == nil {
			circuitFailureThreshold = parsed
		}
	}

	circuitOpenTimeout := 30 * time.Second
	if c := os.Getenv("CIRCUIT_OPEN_TIMEOUT"); c != "" {
		if parsed, err := time.ParseDuration(c); err == nil {
			circuitOpenTimeout = parsed
		}
	}

	upstreamTimeout := 5 * time.Second
	if u := os.Getenv("UPSTREAM_TIMEOUT"); u != "" {
		if parsed, err := time.ParseDuration(u); err == nil {
			upstreamTimeout = parsed
		}
	}

	cacheTTL := 30 * time.Second
	if ttl := os.Getenv("CACHE_TTL"); ttl != "" {
		if parsed, err := time.ParseDuration(ttl); err == nil {
			cacheTTL = parsed
		}
	}

	return &Config{
		Port:                    port,
		Environment:             os.Getenv("ENVIRONMENT"),
		LogLevel:                logLevel,
		AnimalServiceURL:        os.Getenv("ANIMAL_SERVICE_URL"),
		PesagemServiceURL:       os.Getenv("PESAGEM_SERVICE_URL"),
		CotacaoServiceURL:       os.Getenv("COTACAO_SERVICE_URL"),
		NutritionServiceURL:     os.Getenv("NUTRITION_SERVICE_URL"),
		VisionServiceURL:        os.Getenv("VISION_SERVICE_URL"),
		MLServiceURL:            os.Getenv("ML_SERVICE_URL"),
		RateLimitRequests:       rateLimitRequests,
		RateLimitWindow:         rateLimitWindow,
		CircuitFailureThreshold: circuitFailureThreshold,
		CircuitOpenTimeout:      circuitOpenTimeout,
		UpstreamTimeout:         upstreamTimeout,
		CacheTTL:                cacheTTL,
		JWTSecret:               os.Getenv("JWT_SECRET"),
		Logger:                  logger,
	}, nil
}
