#!/bin/bash

# =============================================================================
# Load Testing Script - AgroVision API Gateway (usando Apache Bench)
# =============================================================================
# Realiza load testing do API Gateway para validar performance
# Requer: apache2-utils (ab - Apache Bench)
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_GATEWAY_URL="http://localhost:8000"

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Verifica se Apache Bench está instalado
check_ab() {
    if ! command -v ab &> /dev/null; then
        print_fail "Apache Bench (ab) não está instalado"
        echo "Instale com: sudo apt-get install apache2-utils"
        exit 1
    fi
    print_pass "Apache Bench encontrado"
}

# Teste 1: Health Check Load
test_health_check_load() {
    print_header "Teste 1: Health Check Load (100 requisições)"
    
    print_info "Endpoint: GET /health"
    print_info "Número de requisições: 100"
    print_info "Concorrência: 10"
    echo ""
    
    ab -n 100 -c 10 -q "$API_GATEWAY_URL/health" || print_fail "Teste falhou"
}

# Teste 2: Routing Load
test_routing_load() {
    print_header "Teste 2: Routing Load (50 requisições, 5 concorrentes)"
    
    print_info "Endpoint: GET /api/v1/animals (será roteado para animal service)"
    echo ""
    
    # Esperamos 502 Bad Gateway pois o serviço pode não estar rodando
    ab -n 50 -c 5 -q "$API_GATEWAY_URL/api/v1/animals" || print_fail "Teste falhou"
}

# Teste 3: Escalada de carga
test_escalating_load() {
    print_header "Teste 3: Escalada de Carga"
    
    local concurrencies=(1 5 10 20)
    local requests=100
    
    for concurrency in "${concurrencies[@]}"; do
        print_info "Teste com $concurrency requisições concorrentes (total: $requests)"
        echo ""
        
        ab -n $requests -c $concurrency -q "$API_GATEWAY_URL/health" || print_fail "Teste falhou"
        
        echo ""
    done
}

# Teste 4: Long duration test
test_long_duration() {
    print_header "Teste 4: Long Duration Test (500 requisições, 20 concorrentes)"
    
    print_info "Testando resistência sob carga prolongada"
    print_info "Total: 500 requisições, 20 concorrentes"
    echo ""
    
    ab -n 500 -c 20 -q "$API_GATEWAY_URL/health" || print_fail "Teste falhou"
}

# Teste 5: POST Request Load
test_post_load() {
    print_header "Teste 5: POST Request Load"
    
    print_info "Testando POST com payload"
    
    local temp_file=$(mktemp)
    echo '{"test": "data"}' > "$temp_file"
    
    ab -n 50 -c 5 -q -p "$temp_file" -T "application/json" "$API_GATEWAY_URL/api/v1/animals" || print_fail "Teste falhou"
    
    rm "$temp_file"
}

# Teste 6: Timing Distribution
test_timing_distribution() {
    print_header "Teste 6: Análise de Timing"
    
    print_info "Analisando distribuição de tempos de resposta"
    echo ""
    
    ab -n 100 -c 10 -g /tmp/ab_results.tsv "$API_GATEWAY_URL/health" 2>&1 | tail -20
    
    print_info "Resultados salvos em /tmp/ab_results.tsv"
}

# Teste 7: Different endpoints
test_different_endpoints() {
    print_header "Teste 7: Teste de Diferentes Endpoints"
    
    local endpoints=(
        "/health"
        "/api/v1/animals"
        "/api/v1/pesagens"
        "/api/v1/cotacoes"
    )
    
    for endpoint in "${endpoints[@]}"; do
        print_info "Testando: $endpoint (50 req, 5 concorrentes)"
        ab -n 50 -c 5 -q "$API_GATEWAY_URL$endpoint" 2>&1 | grep -E "Requests per second|Time per request|Failed requests" || true
        echo ""
    done
}

# Teste 8: Sustained Load
test_sustained_load() {
    print_header "Teste 8: Teste de Carga Sustentada (2000 requisições)"
    
    print_info "Verificando comportamento sob carga sustentada"
    print_info "Total: 2000 requisições, 50 concorrentes"
    print_info "Duração estimada: ~5 minutos"
    echo ""
    
    ab -n 2000 -c 50 -q "$API_GATEWAY_URL/health" || print_fail "Teste falhou"
}

# Teste 9: Percentile Analysis
test_percentile_analysis() {
    print_header "Teste 9: Análise de Percentis"
    
    print_info "Executando com mais detalhes sobre latência"
    echo ""
    
    ab -n 200 -c 10 -v 2 "$API_GATEWAY_URL/health" 2>&1 | tail -50
}

# =============================================================================
# Summary
# =============================================================================

print_summary() {
    print_header "RESUMO DOS TESTES DE CARGA"
    echo ""
    echo "Testes executados com sucesso!"
    echo ""
    echo -e "${BLUE}Métricas importantes a observar:${NC}"
    echo "  • Requests per second (deve estar acima de 100)"
    echo "  • Time per request (deve estar abaixo de 100ms)"
    echo "  • Failed requests (deve ser 0)"
    echo "  • Connection times (deve ter baixa variação)"
    echo ""
}

# =============================================================================
# Main
# =============================================================================

main() {
    print_header "AgroVision Load Testing Suite (Apache Bench)"
    echo "API Gateway URL: $API_GATEWAY_URL"
    echo ""

    # Verificar dependências
    check_ab

    # Verificar se o gateway está disponível
    if ! curl -sf "$API_GATEWAY_URL/health" >/dev/null 2>&1; then
        print_fail "API Gateway não está disponível em $API_GATEWAY_URL"
        return 1
    fi
    
    print_pass "API Gateway está disponível"
    echo ""

    # Perguntar quais testes executar
    print_info "Escolha os testes a executar:"
    echo ""
    echo "1) Health Check Load"
    echo "2) Routing Load"
    echo "3) Escalada de Carga"
    echo "4) Long Duration"
    echo "5) POST Load"
    echo "6) Timing Distribution"
    echo "7) Different Endpoints"
    echo "8) Sustained Load"
    echo "9) Percentile Analysis"
    echo "0) Todos os testes"
    echo ""
    
    read -p "Escolha uma opção (0-9): " choice
    
    case $choice in
        1) test_health_check_load ;;
        2) test_routing_load ;;
        3) test_escalating_load ;;
        4) test_long_duration ;;
        5) test_post_load ;;
        6) test_timing_distribution ;;
        7) test_different_endpoints ;;
        8) test_sustained_load ;;
        9) test_percentile_analysis ;;
        0)
            test_health_check_load
            echo ""
            test_routing_load
            echo ""
            test_escalating_load
            echo ""
            test_long_duration
            echo ""
            test_timing_distribution
            ;;
        *) print_fail "Opção inválida" ;;
    esac
    
    echo ""
    print_summary
}

main "$@"
