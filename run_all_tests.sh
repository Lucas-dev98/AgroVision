#!/bin/bash
# Script para executar todos os testes dos 4 serviços
set -e

VENV="/home/lucasbastos/AgroVision/venv/bin/python"
ROOT="/home/lucasbastos/AgroVision"

echo "════════════════════════════════════════════════════════════"
echo "🧪 EXECUÇÃO DE TESTES - AgroVision Stack"
echo "════════════════════════════════════════════════════════════"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
TOTAL_TESTS=0
TOTAL_FAILED=0
declare -a RESULTS

# Função para executar testes de um serviço
run_tests() {
    local service=$1
    local service_name=$2
    local service_path="$ROOT/services/$service"
    
    echo -e "${BLUE}📦 Testando ${service_name}...${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    cd "$service_path"
    
    if output=$($VENV -m pytest -v --tb=short 2>&1); then
        # Extrair número de testes
        test_count=$(echo "$output" | grep -oP '\d+(?= passed)' || echo "0")
        
        echo -e "${GREEN}✅ $service_name: $test_count testes passando${NC}"
        RESULTS+=("${service_name}: ${test_count} ✅")
        TOTAL_TESTS=$((TOTAL_TESTS + test_count))
        
        # Mostrar resumo
        echo "$output" | tail -15
    else
        echo -e "${RED}❌ $service_name: FALHOU${NC}"
        RESULTS+=("${service_name}: FALHOU ❌")
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        echo "$output" | tail -30
    fi
    
    echo ""
}

# Executar testes de cada serviço
run_tests "animal_service" "🐄 Animal Service"
run_tests "pesagem_service" "⚖️  Pesagem Service"
run_tests "cotacao_service" "💰 Cotacao Service"
run_tests "api_gateway" "🔐 API Gateway"

# Resumo final
echo "════════════════════════════════════════════════════════════"
echo "📊 RESUMO DE TESTES"
echo "════════════════════════════════════════════════════════════"

for result in "${RESULTS[@]}"; do
    echo "  $result"
done

echo ""
echo "📈 Total de Testes Passando: ${GREEN}${TOTAL_TESTS}${NC}"

if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ TODOS OS TESTES PASSANDO!${NC}"
    echo "════════════════════════════════════════════════════════════"
    exit 0
else
    echo -e "${RED}❌ $TOTAL_FAILED serviço(s) com falha${NC}"
    echo "════════════════════════════════════════════════════════════"
    exit 1
fi
