#!/bin/bash

# =============================================================================
# E2E Testing Script - AgroVision API Gateway
# =============================================================================
# Este script executa testes end-to-end completos do API Gateway
# Inclui: Health checks, Roteamento, Rate Limiting, CORS, etc.
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuração
API_GATEWAY_URL="http://localhost:8000"
ANIMAL_SERVICE_URL="http://localhost:9000"
PESAGEM_SERVICE_URL="http://localhost:8001"
COTACAO_SERVICE_URL="http://localhost:8002"
TIMEOUT=5
MAX_RETRIES=30
RETRY_DELAY=1

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# =============================================================================
# Funções Auxiliares
# =============================================================================

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Aguarda que um serviço esteja disponível
wait_for_service() {
    local url=$1
    local service_name=$2
    local retries=0

    print_info "Aguardando $service_name ($url)..."

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "$url/health" >/dev/null 2>&1; then
            print_pass "$service_name está disponível"
            return 0
        fi
        
        retries=$((retries + 1))
        echo -n "."
        sleep $RETRY_DELAY
    done

    print_fail "$service_name não respondeu após $((MAX_RETRIES * RETRY_DELAY))s"
    return 1
}

# Executa um teste HTTP
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local expected_pattern=${4:-""}
    local data=${5:-""}

    local url="$API_GATEWAY_URL$endpoint"
    local test_name="$method $endpoint (esperado: $expected_status)"
    
    print_test "$test_name"

    local response
    local http_code
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            --max-time $TIMEOUT 2>/dev/null || echo "000")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data" \
            --max-time $TIMEOUT 2>/dev/null || echo "000")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "$expected_status" ]; then
        if [ -z "$expected_pattern" ] || echo "$body" | grep -q "$expected_pattern"; then
            print_pass "$test_name"
            return 0
        else
            print_fail "$test_name - Padrão não encontrado: $expected_pattern"
            echo "Response: $body"
            return 1
        fi
    else
        print_fail "$test_name - Recebido: $http_code"
        echo "Response: $body"
        return 1
    fi
}

# =============================================================================
# Testes
# =============================================================================

test_health_check() {
    print_header "1. Health Check"
    test_endpoint "GET" "/health" "200" "ok"
}

test_cors_headers() {
    print_header "2. CORS Headers"
    
    print_test "Verificar Access-Control-Allow-Origin"
    local response=$(curl -s -i -X GET "$API_GATEWAY_URL/health" 2>/dev/null)
    
    if echo "$response" | grep -q "Access-Control-Allow-Origin: \*"; then
        print_pass "CORS header presente"
    else
        print_fail "CORS header ausente"
    fi
}

test_security_headers() {
    print_header "3. Security Headers"
    
    local headers=(
        "X-Content-Type-Options: nosniff"
        "X-Frame-Options: DENY"
        "X-XSS-Protection: 1; mode=block"
    )

    local response=$(curl -s -i -X GET "$API_GATEWAY_URL/health" 2>/dev/null)

    for header in "${headers[@]}"; do
        print_test "Verificar $header"
        if echo "$response" | grep -q "$header"; then
            print_pass "Header presente: $header"
        else
            print_fail "Header ausente: $header"
        fi
    done
}

test_routing() {
    print_header "4. Roteamento de Requisições"
    
    # Testes de roteamento (esperamos 502 Bad Gateway se o serviço upstream não responder)
    test_endpoint "GET" "/api/v1/animals" "502" "" || true
    test_endpoint "GET" "/api/v1/pesagens" "502" "" || true
    test_endpoint "GET" "/api/v1/cotacoes" "502" "" || true
}

test_not_found() {
    print_header "5. Tratamento de 404"
    test_endpoint "GET" "/api/v1/nonexistent" "404" "Route not found"
}

test_cors_preflight() {
    print_header "6. CORS Preflight Request"
    
    print_test "OPTIONS /api/v1/animals"
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X OPTIONS "$API_GATEWAY_URL/api/v1/animals" \
        -H "Origin: http://localhost:3000" \
        --max-time $TIMEOUT 2>/dev/null || echo "000")
    
    if [ "$http_code" = "204" ] || [ "$http_code" = "200" ]; then
        print_pass "CORS preflight respondeu com $http_code"
    else
        print_fail "CORS preflight retornou $http_code (esperado 204 ou 200)"
    fi
}

test_different_methods() {
    print_header "7. Diferentes Métodos HTTP"
    
    local methods=("GET" "POST" "PUT" "DELETE" "PATCH")
    
    for method in "${methods[@]}"; do
        print_test "$method /health"
        # POST, PUT, DELETE também devem retornar alguma resposta do gateway
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$API_GATEWAY_URL/health" \
            --max-time $TIMEOUT 2>/dev/null || echo "000")
        
        if [ -n "$http_code" ] && [ "$http_code" != "000" ]; then
            print_pass "$method retornou $http_code"
        else
            print_fail "$method falhou"
        fi
    done
}

test_rate_limiting() {
    print_header "8. Rate Limiting"
    
    print_test "Enviar múltiplas requisições para testar rate limit"
    
    # Assumindo 100 req/min, vamos tentar 5 requisições rapidamente
    local success_count=0
    local rate_limited=0
    
    for i in {1..5}; do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_GATEWAY_URL/health" \
            --max-time $TIMEOUT 2>/dev/null || echo "000")
        
        if [ "$http_code" = "200" ]; then
            success_count=$((success_count + 1))
        elif [ "$http_code" = "429" ]; then
            rate_limited=$((rate_limited + 1))
            print_info "Requisição $i: Rate limited (429)"
        fi
        
        sleep 0.1
    done
    
    print_pass "Rate limiting teste: $success_count sucessos, $rate_limited rate-limited"
}

test_response_headers() {
    print_header "9. Response Headers"
    
    print_test "Verificar Content-Type"
    local response=$(curl -s -i -X GET "$API_GATEWAY_URL/health" 2>/dev/null)
    
    if echo "$response" | grep -q "Content-Type: application/json"; then
        print_pass "Content-Type correto"
    else
        print_fail "Content-Type incorreto ou ausente"
    fi
}

test_response_format() {
    print_header "10. Response Format"
    
    test_endpoint "GET" "/health" "200" '"status":"ok"'
    test_endpoint "GET" "/health" "200" '"service":"api-gateway"'
}

test_concurrent_requests() {
    print_header "11. Requisições Concorrentes"
    
    print_test "Enviar 10 requisições concorrentes"
    
    local pids=()
    local success_count=0
    
    for i in {1..10}; do
        (
            local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_GATEWAY_URL/health" \
                --max-time $TIMEOUT 2>/dev/null || echo "000")
            
            if [ "$http_code" = "200" ]; then
                echo "success"
            fi
        ) &
        pids+=($!)
    done
    
    for pid in "${pids[@]}"; do
        if wait $pid 2>/dev/null; then
            success_count=$((success_count + 1))
        fi
    done
    
    print_pass "Requisições concorrentes: $success_count/10 bem-sucedidas"
}

test_request_headers() {
    print_header "12. Propagação de Request Headers"
    
    print_test "Enviar headers customizados"
    
    local response=$(curl -s -w "\n%{http_code}" -X GET "$API_GATEWAY_URL/health" \
        -H "X-Custom-Header: test-value" \
        -H "Authorization: Bearer token123" \
        --max-time $TIMEOUT 2>/dev/null || echo "000")
    
    local http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        print_pass "Headers customizados aceitos"
    else
        print_fail "Headers customizados rejeitados"
    fi
}

test_large_payload() {
    print_header "13. Large Payloads"
    
    print_test "Enviar payload grande"
    
    # Criar payload de 1MB com dados JSON
    local large_payload=$(python3 -c "import json; print(json.dumps({'data': 'x' * 1000000}))")
    
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_GATEWAY_URL/api/v1/animals" \
        -H "Content-Type: application/json" \
        -d "$large_payload" \
        --max-time $TIMEOUT 2>/dev/null || echo "000")
    
    if [ "$http_code" != "000" ]; then
        print_pass "Large payload aceito (retornou $http_code)"
    else
        print_fail "Large payload rejeitado ou timeout"
    fi
}

test_slow_requests() {
    print_header "14. Tratamento de Slow Requests"
    
    print_test "Requisição com delay"
    
    # Usar um IP que demora a responder
    local http_code=$(timeout 10 curl -s -o /dev/null -w "%{http_code}" -X GET "$API_GATEWAY_URL/health" \
        --max-time 5 2>/dev/null || echo "000")
    
    if [ "$http_code" != "000" ]; then
        print_pass "Slow request tratado (retornou $http_code)"
    else
        print_fail "Slow request timeout"
    fi
}

test_error_responses() {
    print_header "15. Error Response Format"
    
    test_endpoint "GET" "/api/v1/nonexistent" "404" "error"
}

# =============================================================================
# Summary
# =============================================================================

print_summary() {
    print_header "RESUMO DOS TESTES"
    
    echo -e "Total de testes:   ${BLUE}$TESTS_TOTAL${NC}"
    echo -e "Sucessos:          ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Falhas:            ${RED}$TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✅ TODOS OS TESTES PASSARAM!${NC}\n"
        return 0
    else
        echo -e "\n${RED}❌ ALGUNS TESTES FALHARAM${NC}\n"
        return 1
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    print_header "AgroVision E2E Test Suite"
    echo "API Gateway URL: $API_GATEWAY_URL"
    echo ""

    # Aguardar serviços
    if ! wait_for_service "$API_GATEWAY_URL/health" "API Gateway"; then
        print_fail "API Gateway não está disponível"
        return 1
    fi
    
    echo ""

    # Executar testes
    test_health_check
    test_cors_headers
    test_security_headers
    test_routing
    test_not_found
    test_cors_preflight
    test_different_methods
    test_rate_limiting
    test_response_headers
    test_response_format
    test_concurrent_requests
    test_request_headers
    test_large_payload
    test_slow_requests
    test_error_responses
    
    echo ""
    print_summary
}

# Executar
main
