#!/usr/bin/env make

.PHONY: help install test test-animal test-converter test-coverage db-up db-down db-reset run clean

# Variáveis
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help:
	@echo "🐄 Sistema de Gestão de Rebanho - Makefile"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make install           - Instalar dependências"
	@echo "  make test              - Rodar todos os testes"
	@echo "  make test-animal       - Rodar testes do Animal Service"
	@echo "  make test-converter    - Rodar testes dos Converters"
	@echo "  make test-coverage     - Rodar testes com cobertura"
	@echo "  make db-up             - Iniciar bancos (Docker)"
	@echo "  make db-down           - Parar bancos"
	@echo "  make db-reset          - Resetar bancos (CUIDADO!)"
	@echo "  make run               - Rodar Animal Service"
	@echo "  make clean             - Limpar arquivos temporários"
	@echo ""

install:
	@echo "📦 Instalando dependências..."
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r shared/requirements.txt
	$(PIP) install -r services/animal-service/requirements.txt
	@echo "✅ Dependências instaladas!"

test:
	@echo "🧪 Rodando TODOS os testes..."
	$(PYTHON) -m pytest -v --tb=short

test-animal:
	@echo "🧪 Rodando testes do Animal Service..."
	$(PYTHON) -m pytest services/animal-service/test_animal_repository.py -v --tb=short

test-converter:
	@echo "🧪 Rodando testes dos Converters..."
	$(PYTHON) -m pytest shared/test_converters.py -v --tb=short

test-coverage:
	@echo "🧪 Rodando testes com cobertura..."
	$(PYTHON) -m pytest --cov=services --cov=shared --cov-report=html --cov-report=term-missing
	@echo "✅ Relatório HTML gerado em htmlcov/index.html"

db-up:
	@echo "🐘 Iniciando bancos de dados..."
	docker-compose up -d
	@echo "✅ Bancos iniciados!"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  MongoDB: localhost:27017"
	@echo "  Redis: localhost:6379"

db-down:
	@echo "🛑 Parando bancos de dados..."
	docker-compose down
	@echo "✅ Bancos parados!"

db-reset:
	@echo "⚠️  RESETANDO BANCOS (deletará todos os dados!)..."
	docker-compose down -v
	docker-compose up -d
	@echo "✅ Bancos resetados!"

db-logs:
	@echo "📋 Logs do PostgreSQL..."
	docker-compose logs postgres

run:
	@echo "🚀 Iniciando Animal Service..."
	$(PYTHON) services/animal-service/main.py

clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "✅ Limpeza concluída!"

# Targets compostos
setup: install db-up
	@echo "✅ Setup completo! Agora execute: make test"

check: test-coverage
	@echo "✅ Verificação concluída!"

dev: db-up run
	@echo "🚀 Ambiente de desenvolvimento ativo!"

# ==================== DOCKER COMPOSE ====================
.PHONY: docker-up docker-down docker-build docker-logs docker-ps docker-test

docker-build:
@echo "🔨 Building Docker images..."
docker-compose build

docker-up:
@echo "🚀 Starting all services with Docker Compose..."
docker-compose up -d
@echo "✅ Services started!"
@echo ""
@echo "📍 Endpoints:"
@echo "  - Animal Service:  http://localhost:8000"
@echo "  - Pesagem Service: http://localhost:8001"
@echo "  - Cotacao Service: http://localhost:8002"
@echo "  - PostgreSQL:      localhost:5432"
@echo "  - Redis:           localhost:6379"
@echo ""
@sleep 2
@make docker-health

docker-down:
@echo "⬇️  Stopping all services..."
docker-compose down

docker-logs:
@echo "📜 Following logs from all services..."
docker-compose logs -f

docker-logs-service:
@echo "📜 Logs for service: $(SERVICE)"
docker-compose logs -f $(SERVICE)

docker-ps:
@echo "📋 Active containers:"
docker-compose ps

docker-health:
@echo "🏥 Health check:"
@docker-compose ps --services | while read service; do \
echo -n "  $$service: "; \
docker-compose ps $$service | tail -1 | grep -q "healthy" && echo "✅ healthy" || echo "⏳ starting"; \
done

docker-test:
@echo "🧪 Running tests in Docker..."
docker-compose exec animal-service pytest tests/ -v --tb=short
docker-compose exec pesagem-service pytest tests/ -v --tb=short
docker-compose exec cotacao-service pytest tests/ -v --tb=short

docker-shell:
@echo "🐚 Opening shell in $(SERVICE) container..."
docker-compose exec $(SERVICE) /bin/bash

docker-db-shell:
@echo "🐘 Opening PostgreSQL shell..."
docker-compose exec db psql -U agrovision -d agrovision

docker-redis-shell:
@echo "📍 Opening Redis shell..."
docker-compose exec redis redis-cli

docker-migrate:
@echo "🔄 Running Alembic migrations..."
docker-compose exec animal-service alembic upgrade head
@echo "✅ Migrations completed!"

docker-clean:
@echo "🧹 Cleaning up Docker resources..."
docker-compose down -v
@echo "✅ Cleanup completed!"

docker-rebuild:
@echo "🔄 Rebuilding and restarting all services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d
@make docker-health
