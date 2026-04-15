#!/bin/bash
# Script para rodar testes facilmente

echo "🧪 Executando Testes com TDD..."
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

case "$1" in
  "all")
    echo -e "${YELLOW}Rodando TODOS os testes...${NC}"
    pytest -v --tb=short
    ;;
  "animal")
    echo -e "${YELLOW}Rodando testes do Animal Repository...${NC}"
    pytest services/animal-service/test_animal_repository.py -v --tb=short
    ;;
  "converter")
    echo -e "${YELLOW}Rodando testes dos Converters...${NC}"
    pytest shared/test_converters.py -v --tb=short
    ;;
  "coverage")
    echo -e "${YELLOW}Rodando testes com cobertura...${NC}"
    pytest --cov=services --cov=shared --cov-report=html --cov-report=term-missing
    echo -e "${GREEN}✅ Relatório HTML gerado em htmlcov/index.html${NC}"
    ;;
  "watch")
    echo -e "${YELLOW}Modo watch (rerun on changes)...${NC}"
    pytest-watch -- -v
    ;;
  "quick")
    echo -e "${YELLOW}Teste rápido (sem cobertura)...${NC}"
    pytest -x  # Para no primeiro erro
    ;;
  *)
    echo "Uso: $0 {all|animal|converter|coverage|quick|watch}"
    echo ""
    echo "Exemplos:"
    echo "  ./run_tests.sh all          # Todos os testes"
    echo "  ./run_tests.sh animal       # Apenas Animal Service"
    echo "  ./run_tests.sh converter    # Apenas Converters"
    echo "  ./run_tests.sh coverage     # Com relatório de cobertura"
    echo "  ./run_tests.sh quick        # Teste rápido (para no primeiro erro)"
    exit 1
    ;;
esac
