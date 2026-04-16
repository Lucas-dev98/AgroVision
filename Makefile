.PHONY: help build up down logs clean test

# ==================== DOCKER COMPOSE ====================
help:
@echo "╔════════════════════════════════════════════════════════════════╗"
@echo "║        AgroVision - Docker Compose Management Commands         ║"
@echo "╚════════════════════════════════════════════════════════════════╝"
@echo ""
@echo "🚀 STARTUP:"
@echo "  make build               - Build Docker images"
@echo "  make up                  - Start all services"
@echo "  make down                - Stop all services"
@echo "  make ps                  - List running containers"
@echo "  make logs                - View all services logs"
@echo "  make clean               - Remove containers and volumes"
@echo ""
@echo "🧪 TESTING (Local - without Docker):"
@echo "  make test-animal         - Test animal-service (41 tests)"
@echo "  make test-pesagem        - Test pesagem-service (33 tests)"
@echo "  make test-cotacao        - Test cotacao-service (41 tests)"
@echo "  make test-all            - Run all tests (115 total)"
@echo ""
@echo "🔧 UTILITIES:"
@echo "  make env                 - Create .env from .env.example"
@echo "  make validate            - Validate docker-compose.yml"
@echo "  make health              - Check services health"
@echo "  make clean               - Remove containers and volumes"
@echo ""

build:
@echo "🔨 Building Docker images..."
docker-compose build

up:
@echo "🚀 Starting AgroVision stack..."
docker-compose up -d
@echo "✅ Services starting..."
@echo "🌐 Services available at:"
@echo "  - animal-service:   http://localhost:8000/docs"
@echo "  - pesagem-service:  http://localhost:8001/docs"
@echo "  - cotacao-service:  http://localhost:8002/docs"
@echo "  - PostgreSQL:       localhost:5432"
@echo "  - Redis:            localhost:6379"
@sleep 5
docker-compose ps

down:
@echo "⏹️  Stopping AgroVision stack..."
docker-compose down

ps:
@docker-compose ps

logs:
@docker-compose logs -f

health:
@echo "🏥 Checking services health..."
@docker-compose ps --format "table {{.Names}}\t{{.State}}\t{{.Status}}"

# ==================== TESTING (LOCAL) ====================
test-animal:
@echo "🧪 Testing animal-service (41 tests)..."
@./venv/bin/python -m pytest services/animal_service/tests/ -v --tb=short

test-pesagem:
@echo "🧪 Testing pesagem-service (33 tests)..."
@./venv/bin/python -m pytest services/pesagem_service/tests/ -v --tb=short

test-cotacao:
@echo "🧪 Testing cotacao-service (41 tests)..."
@./venv/bin/python -m pytest services/cotacao_service/tests/ -v --tb=short

test-all: test-animal test-pesagem test-cotacao
@echo "✅ All 115 tests completed!"

# ==================== UTILITIES ====================
env:
@if [ ! -f .env ]; then \
cp .env.example .env; \
echo "✅ Created .env from .env.example"; \
else \
echo "⚠️  .env already exists"; \
fi

validate:
@echo "✅ Validating docker-compose.yml..."
@docker-compose config > /dev/null && echo "✅ Configuration is valid!"

clean:
@echo "🧹 Cleaning up containers and volumes..."
@docker-compose down -v
@docker system prune -f
@echo "✅ Cleanup complete!"

push:
@echo "📤 Pushing to GitHub..."
git add .
git commit -m "feat: Docker Compose com 3 serviços completos"
git push
