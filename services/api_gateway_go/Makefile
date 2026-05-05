.PHONY: help build run test test-e2e test-rate-limit test-load test-all clean logs

# =============================================================================
# Makefile - AgroVision API Gateway Tests
# =============================================================================

# Colors
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

help:
	@echo "$(BLUE)AgroVision API Gateway - Test Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Build Commands:$(NC)"
	@echo "  make build              - Build the API Gateway Docker image"
	@echo "  make build-compose      - Build all services with docker-compose"
	@echo ""
	@echo "$(GREEN)Run Commands:$(NC)"
	@echo "  make up                 - Start all services with docker-compose"
	@echo "  make down               - Stop all services"
	@echo "  make run-local          - Run API Gateway locally"
	@echo ""
	@echo "$(GREEN)Test Commands:$(NC)"
	@echo "  make test-go            - Run Go unit tests"
	@echo "  make test-go-coverage   - Run Go tests with coverage report"
	@echo "  make test-e2e           - Run E2E tests"
	@echo "  make test-rate-limit    - Run rate limiting tests"
	@echo "  make test-load          - Run load testing (Apache Bench)"
	@echo "  make test-all           - Run all tests"
	@echo ""
	@echo "$(GREEN)Utility Commands:$(NC)"
	@echo "  make logs               - View API Gateway logs"
	@echo "  make logs-all           - View all services logs"
	@echo "  make health-check       - Check API Gateway health"
	@echo "  make install-deps       - Install Apache Bench"
	@echo "  make clean              - Remove containers and volumes"
	@echo ""

# =============================================================================
# Build Commands
# =============================================================================

build:
	@echo "$(BLUE)Building API Gateway Docker image...$(NC)"
	docker build -t agrovision/api-gateway:latest .

build-compose:
	@echo "$(BLUE)Building services with docker-compose...$(NC)"
	docker-compose -f docker-compose.test.yml build

# =============================================================================
# Run Commands
# =============================================================================

up:
	@echo "$(BLUE)Starting services with docker-compose...$(NC)"
	docker-compose -f docker-compose.test.yml up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo ""
	@echo "API Gateway: http://localhost:8000"
	@echo "Animal Service: http://localhost:9000"
	@echo "Pesagem Service: http://localhost:8001"
	@echo "Cotacao Service: http://localhost:8002"
	@echo ""

down:
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose -f docker-compose.test.yml down

run-local:
	@echo "$(BLUE)Running API Gateway locally...$(NC)"
	@echo "Make sure to set environment variables or use .env file"
	go run ./cmd/main/main.go

# =============================================================================
# Test Commands
# =============================================================================

test-go:
	@echo "$(BLUE)Running Go unit tests...$(NC)"
	go test ./tests -v

test-go-coverage:
	@echo "$(BLUE)Running Go tests with coverage...$(NC)"
	go test ./tests -v -coverprofile=coverage.out
	go tool cover -html=coverage.out -o coverage.html
	@echo "$(GREEN)Coverage report generated: coverage.html$(NC)"

test-e2e: up
	@echo ""
	@echo "$(BLUE)Running E2E tests...$(NC)"
	@echo "Waiting for services to be ready..."
	@sleep 5
	bash tests/e2e_tests.sh
	@echo ""
	@echo "$(GREEN)E2E tests completed!$(NC)"

test-rate-limit: up
	@echo ""
	@echo "$(BLUE)Running rate limit tests...$(NC)"
	@echo "Waiting for services to be ready..."
	@sleep 5
	bash tests/rate_limit_tests.sh 100 60
	@echo ""
	@echo "$(GREEN)Rate limit tests completed!$(NC)"

test-load: install-deps up
	@echo ""
	@echo "$(BLUE)Running load tests...$(NC)"
	@echo "Waiting for services to be ready..."
	@sleep 5
	bash tests/load_tests.sh
	@echo ""
	@echo "$(GREEN)Load tests completed!$(NC)"

test-all: test-go test-e2e test-rate-limit
	@echo ""
	@echo "$(GREEN)All tests completed!$(NC)"

# =============================================================================
# Utility Commands
# =============================================================================

logs:
	docker-compose -f docker-compose.test.yml logs -f api_gateway

logs-all:
	docker-compose -f docker-compose.test.yml logs -f

health-check:
	@echo "$(BLUE)Checking API Gateway health...$(NC)"
	@curl -s http://localhost:8000/health | jq . || echo "Gateway not responding"

install-deps:
	@echo "$(BLUE)Installing Apache Bench...$(NC)"
	@command -v ab >/dev/null 2>&1 && echo "$(GREEN)Apache Bench already installed$(NC)" || { \
		echo "Installing apache2-utils..."; \
		sudo apt-get update && sudo apt-get install -y apache2-utils; \
	}

benchmark:
	@echo "$(BLUE)Running benchmarks...$(NC)"
	go test -bench=. -benchmem ./tests

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	docker-compose -f docker-compose.test.yml down -v
	rm -f coverage.out coverage.html
	@echo "$(GREEN)Cleanup completed!$(NC)"

# =============================================================================
# Development Commands
# =============================================================================

fmt:
	@echo "$(BLUE)Formatting code...$(NC)"
	gofmt -w ./cmd ./internal ./tests

lint:
	@echo "$(BLUE)Running linter...$(NC)"
	golint ./cmd ./internal ./tests || true

vet:
	@echo "$(BLUE)Running go vet...$(NC)"
	go vet ./cmd ./internal ./tests

dev-setup: build-compose
	@echo "$(GREEN)Development setup complete!$(NC)"
	@echo "Run 'make up' to start services"

# =============================================================================
# Documentation Commands
# =============================================================================

docs:
	@echo "$(BLUE)API Gateway Documentation:$(NC)"
	@echo ""
	@echo "Configuration: .env.example"
	@echo "Routes: internal/router/router.go"
	@echo "Middleware: internal/middleware/ratelimit.go"
	@echo "README: README.md"
	@echo ""

# =============================================================================
# Quick Commands
# =============================================================================

quick-test: build test-go
	@echo "$(GREEN)Quick test completed!$(NC)"

quick-e2e: build-compose test-e2e
	@echo "$(GREEN)Quick E2E test completed!$(NC)"

# Default target
.DEFAULT_GOAL := help
