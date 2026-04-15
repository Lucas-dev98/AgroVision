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
