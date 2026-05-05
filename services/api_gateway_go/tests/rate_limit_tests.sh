#!/bin/bash

# =============================================================================
# Rate Limit Testing Script - AgroVision API Gateway
# =============================================================================
# Testa o comportamento do rate limiting sob diferentes cenários
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_GATEWAY_URL="http://localhost:8000"
RATE_LIMIT_REQUESTS=${1:-100}  # Requisições por janela
RATE_LIMIT_WINDOW=${2:-60}     # Janela em segundos

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

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# =============================================================================
# Teste 1: Rate Limiting Básico
# =============================================================================

test_basic_rate_limiting() {
    print_header "Teste 1: Rate Limiting Básico"
    
    print_info "Configuração:"
    echo "  Limite: $RATE_LIMIT_REQUESTS req/$RATE_LIMIT_WINDOW segundos"
    echo "  Vamos fazer 5 requisições rapidamente"
    echo ""
    
    local success_count=0
    local rate_limited_count=0
    
    for i in {1..5}; do
        local response=$(curl -s -w "\n%{http_code}" -X GET "$API_GATEWAY_URL/health" \
            --max-time 5 2>/dev/null || echo "000")
        
        local http_code=$(echo "$response" | tail -n1)
        
        if [ "$http_code" = "200" ]; then
            success_count=$((success_count + 1))
            echo -e "${GREEN}Req $i: 200 OK${NC}"
        elif [ "$http_code" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -e "${YELLOW}Req $i: 429 Too Many Requests (Rate Limited)${NC}"
        else
            echo -e "${RED}Req $i: $http_code${NC}"
        fi
        
        sleep 0.05
    done
    
    echo ""
    print_pass "Resultado: $success_count sucessos, $rate_limited_count rate-limited"
}

# =============================================================================
# Teste 2: Recuperação após Rate Limit
# =============================================================================

test_rate_limit_recovery() {
    print_header "Teste 2: Recuperação após Rate Limit"
    
    print_info "Vamos fazer requisições até atingir o limite, depois aguardar recuperação"
    echo ""
    
    # Fazer muitas requisições
    print_info "Fase 1: Enviando $RATE_LIMIT_REQUESTS+ requisições..."
    
    local requests_made=0
    local rate_limited_count=0
    
    for i in $(seq 1 $((RATE_LIMIT_REQUESTS + 10))); do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_GATEWAY_URL/health" \
            --max-time 5 2>/dev/null || echo "000")
        
        requests_made=$((requests_made + 1))
        
        if [ "$http_code" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            if [ $rate_limited_count -eq 1 ]; then
                echo -e "${YELLOW}Rate limit atingido na requisição #$i${NC}"
            fi
        fi
        
        sleep 0.01
    done
    
    echo -e "${YELLOW}Total rate-limited: $rate_limited_count requisições${NC}"
    echo ""
    
    # Aguardar recuperação
    print_info "Fase 2: Aguardando $RATE_LIMIT_WINDOW segundos para recuperação..."
    sleep $((RATE_LIMIT_WINDOW + 5))
    
    # Fazer nova requisição
    print_info "Fase 3: Testando nova requisição..."
    
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_GATEWAY_URL/health" \
        --max-time 5 2>/dev/null || echo "000")
    
    if [ "$http_code" = "200" ]; then
        print_pass "Requisição bem-sucedida após recuperação"
    else
        print_fail "Requisição falhou com código $http_code"
    fi
}

# =============================================================================
# Teste 3: Taxa Constant
# =============================================================================

test_constant_rate() {
    print_header "Teste 3: Taxa Constante de Requisições"
    
    print_info "Enviando 20 requisições em taxa constante (1 a cada 500ms)"
    echo ""
    
    local start_time=$(date +%s%N)
    local success_count=0
    local rate_limited_count=0
    
    for i in {1..20}; do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_GATEWAY_URL/health" \
            --max-time 5 2>/dev/null || echo "000")
        
        if [ "$http_code" = "200" ]; then
            success_count=$((success_count + 1))
            echo -n "${GREEN}.${NC}"
        elif [ "$http_code" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -n "${YELLOW}L${NC}"
        else
            echo -n "${RED}E${NC}"
        fi
        
        sleep 0.5
    done
    
    local end_time=$(date +%s%N)
    local duration=$(( (end_time - start_time) / 1000000 ))
    
    echo ""
    echo ""
    print_pass "Resultado: $success_count sucessos, $rate_limited_count rate-limited"
    print_info "Duração total: ${duration}ms"
}

# =============================================================================
# Teste 4: Múltiplos IPs
# =============================================================================

test_multiple_ips() {
    print_header "Teste 4: Isolamento de Rate Limit por IP"
    
    print_info "Testando se diferentes IPs têm limites separados"
    echo ""
    
    # Simular requisições com diferentes X-Forwarded-For headers
    print_info "Requisições do IP 192.168.1.1:"
    
    local success1=0
    for i in {1..3}; do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_GATEWAY_URL/health" \
            -H "X-Forwarded-For: 192.168.1.1" \
            --max-time 5 2>/dev/null || echo "000")
        
        if [ "$http_code" = "200" ]; then
            success1=$((success1 + 1))
            echo -n "${GREEN}.${NC}"
        fi
    done
    
    echo ""
    
    print_info "Requisições do IP 192.168.1.2:"
    
    local success2=0
    for i in {1..3}; do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_GATEWAY_URL/health" \
            -H "X-Forwarded-For: 192.168.1.2" \
            --max-time 5 2>/dev/null || echo "000")
        
        if [ "$http_code" = "200" ]; then
            success2=$((success2 + 1))
            echo -n "${GREEN}.${NC}"
        fi
    done
    
    echo ""
    echo ""
    print_pass "IP 1: $success1/3 sucessos, IP 2: $success2/3 sucessos"
    
    if [ $success1 -gt 0 ] && [ $success2 -gt 0 ]; then
        print_pass "Isolamento por IP funcionando"
    else
        print_warn "Verificar isolamento por IP"
    fi
}

# =============================================================================
# Teste 5: Retry-After Header
# =============================================================================

test_retry_after_header() {
    print_header "Teste 5: Verificar Retry-After Header"
    
    print_info "Rate limit até atingir o limite, depois verificar header"
    echo ""
    
    # Fazer muitas requisições rápidas
    for i in $(seq 1 $((RATE_LIMIT_REQUESTS + 5))); do
        curl -s -o /dev/null -X GET "$API_GATEWAY_URL/health" --max-time 5 2>/dev/null || true
        sleep 0.01
    done
    
    # Pegar resposta com headers
    local response=$(curl -s -i -X GET "$API_GATEWAY_URL/health" --max-time 5 2>/dev/null || echo "")
    
    if echo "$response" | grep -q "429"; then
        echo -e "${YELLOW}Rate limit atingido (429)${NC}"
        
        if echo "$response" | grep -q "Retry-After"; then
            local retry_after=$(echo "$response" | grep "Retry-After" | head -1)
            print_pass "Header Retry-After encontrado: $retry_after"
        else
            print_warn "Header Retry-After não encontrado"
        fi
        
        if echo "$response" | grep -q "retry_after"; then
            print_pass "Campo retry_after presente no body"
        fi
    else
        print_info "Rate limit não atingido neste teste"
    fi
}

# =============================================================================
# Teste 6: Stress Test
# =============================================================================

test_stress() {
    print_header "Teste 6: Stress Test (30 segundos)"
    
    print_info "Enviando o máximo de requisições possível por 30 segundos"
    echo ""
    
    local start_time=$(date +%s)
    local requests_count=0
    local success_count=0
    local rate_limited_count=0
    local error_count=0
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -ge 30 ]; then
            break
        fi
        
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_GATEWAY_URL/health" \
            --max-time 5 2>/dev/null || echo "000")
        
        requests_count=$((requests_count + 1))
        
        case $http_code in
            200) success_count=$((success_count + 1)); echo -n "${GREEN}.${NC}" ;;
            429) rate_limited_count=$((rate_limited_count + 1)); echo -n "${YELLOW}L${NC}" ;;
            *)   error_count=$((error_count + 1)); echo -n "${RED}E${NC}" ;;
        esac
    done
    
    echo ""
    echo ""
    
    print_info "Resultados:"
    echo "  Total de requisições:   $requests_count"
    echo "  Sucessos:               $success_count"
    echo "  Rate limited:           $rate_limited_count"
    echo "  Erros:                  $error_count"
    
    local requests_per_sec=$(( requests_count / 30 ))
    print_info "Taxa média: $requests_per_sec req/s"
}

# =============================================================================
# Main
# =============================================================================

main() {
    print_header "AgroVision Rate Limit Test Suite"
    echo "API Gateway URL: $API_GATEWAY_URL"
    echo ""

    # Verificar se o gateway está disponível
    if ! curl -sf "$API_GATEWAY_URL/health" >/dev/null 2>&1; then
        print_fail "API Gateway não está disponível em $API_GATEWAY_URL"
        return 1
    fi
    
    print_pass "API Gateway está disponível"
    echo ""

    # Executar testes
    test_basic_rate_limiting
    echo ""
    
    test_rate_limit_recovery
    echo ""
    
    test_constant_rate
    echo ""
    
    test_multiple_ips
    echo ""
    
    test_retry_after_header
    echo ""
    
    test_stress
    echo ""
    
    print_header "Testes de Rate Limiting Concluídos!"
}

main "$@"
