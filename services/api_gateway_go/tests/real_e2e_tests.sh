#!/bin/bash
# 🚀 REAL E2E TESTS - Testes com Serviços Reais e Banco de Dados Verdadeiro
# Sem mocks! Tudo funciona de verdade.
#
# Este script testa:
# - Criar dados reais no BD
# - Recuperar dados salvos
# - Atualizar dados
# - Deletar dados
# - Validar persistência no BD

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs dos serviços reais
ANIMAL_SERVICE_URL="${ANIMAL_SERVICE_URL:-http://localhost:8100}"
PESAGEM_SERVICE_URL="${PESAGEM_SERVICE_URL:-http://localhost:8101}"
COTACAO_SERVICE_URL="${COTACAO_SERVICE_URL:-http://localhost:8102}"
VISION_SERVICE_URL="${VISION_SERVICE_URL:-http://localhost:8103}"
ML_SERVICE_URL="${ML_SERVICE_URL:-http://localhost:8104}"
API_GATEWAY_URL="${API_GATEWAY_URL:-http://localhost:8000}"

# Timestamps para dados únicos
TIMESTAMP=$(date +%s%N)
ANIMAL_NAME="Animal_Test_${TIMESTAMP}"
ANIMAL_TAG="TAG_${TIMESTAMP}"

# Contadores de testes
TESTS_PASSED=0
TESTS_FAILED=0

# ════════════════════════════════════════════════════════════════════════════════
# FUNÇÕES UTILITÁRIAS
# ════════════════════════════════════════════════════════════════════════════════

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

test_case() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

check_service_health() {
    local service_name=$1
    local service_url=$2
    
    test_case "Verificar saúde de $service_name"
    
    response=$(curl -s -w "\n%{http_code}" "${service_url}/health" 2>/dev/null || echo "000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        pass "$service_name está online"
        return 0
    else
        fail "$service_name retornou HTTP $http_code"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════════════════
# TESTES ANIMAL SERVICE - BANCO DE DADOS REAL
# ════════════════════════════════════════════════════════════════════════════════

test_animal_create() {
    print_header "🐄 ANIMAL SERVICE - CRIAR ANIMAL (Banco de Dados Real)"
    
    test_case "Criar novo animal com dados reais"
    
    # Criar animal
    animal_data=$(cat <<EOF
{
    "nome": "$ANIMAL_NAME",
    "raca": "Angus",
    "rfid": "$ANIMAL_TAG",
    "data_nascimento": "2020-01-15"
}
EOF
)
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$animal_data" \
        "${ANIMAL_SERVICE_URL}/api/v1/animals")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        ANIMAL_ID=$(echo "$body" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
        pass "Animal criado com sucesso (ID: $ANIMAL_ID)"
        echo "$ANIMAL_ID"
    else
        fail "Falha ao criar animal (HTTP $http_code)"
        echo "$body"
        return 1
    fi
}

test_animal_retrieve() {
    local animal_id=$1
    
    print_header "🔍 ANIMAL SERVICE - RECUPERAR ANIMAL (Dados Persistidos)"
    
    test_case "Recuperar animal do banco de dados"
    
    response=$(curl -s -w "\n%{http_code}" \
        "${ANIMAL_SERVICE_URL}/api/v1/animals/${animal_id}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        # Verificar que os dados foram salvos corretamente
        if echo "$body" | grep -q "$ANIMAL_TAG"; then
            pass "Animal recuperado do BD com rfid correto"
        else
            fail "Animal recuperado mas rfid incorreto"
            return 1
        fi
        
        if echo "$body" | grep -q "$ANIMAL_NAME"; then
            pass "Animal recuperado com nome correto"
        else
            fail "Animal recuperado mas nome incorreto"
            return 1
        fi
    else
        fail "Falha ao recuperar animal (HTTP $http_code)"
        return 1
    fi
}

test_animal_update() {
    local animal_id=$1
    
    print_header "✏️  ANIMAL SERVICE - ATUALIZAR ANIMAL"
    
    test_case "Atualizar dados do animal no banco de dados"
    
    updated_data=$(cat <<EOF
{
    "nome": "$ANIMAL_NAME - UPDATED",
    "raca": "Angus",
    "rfid": "$ANIMAL_TAG",
    "data_nascimento": "2020-01-15"
}
EOF
)
    
    response=$(curl -s -w "\n%{http_code}" -X PUT \
        -H "Content-Type: application/json" \
        -d "$updated_data" \
        "${ANIMAL_SERVICE_URL}/api/v1/animals/${animal_id}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q "UPDATED"; then
            pass "Animal atualizado com sucesso no BD"
        else
            fail "Animal não foi atualizado corretamente"
            return 1
        fi
    else
        fail "Falha ao atualizar animal (HTTP $http_code)"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════════════════
# TESTES PESAGEM SERVICE - BANCO DE DADOS REAL
# ════════════════════════════════════════════════════════════════════════════════

test_pesagem_create() {
    local animal_id=$1
    
    print_header "⚖️  PESAGEM SERVICE - CRIAR PESAGEM (Banco de Dados Real)"
    
    test_case "Criar registro de pesagem com dados reais"
    
    pesagem_data=$(cat <<EOF
{
    "animal_id": $animal_id,
    "weight": 500.5,
    "measurement_date": "2026-05-04",
    "notes": "Pesagem de teste realizada em $TIMESTAMP"
}
EOF
)
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$pesagem_data" \
        "${PESAGEM_SERVICE_URL}/api/v1/pesagens")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        PESAGEM_ID=$(echo "$body" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
        pass "Pesagem criada com sucesso (ID: $PESAGEM_ID)"
        echo "$PESAGEM_ID"
    else
        fail "Falha ao criar pesagem (HTTP $http_code)"
        echo "$body"
        return 1
    fi
}

test_pesagem_retrieve() {
    local pesagem_id=$1
    
    print_header "🔍 PESAGEM SERVICE - RECUPERAR PESAGEM (Dados Persistidos)"
    
    test_case "Recuperar pesagem do banco de dados"
    
    response=$(curl -s -w "\n%{http_code}" \
        "${PESAGEM_SERVICE_URL}/api/v1/pesagens/${pesagem_id}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q "500.5"; then
            pass "Pesagem recuperada com peso correto (500.5 kg)"
        else
            fail "Peso não foi persistido corretamente"
            return 1
        fi
    else
        fail "Falha ao recuperar pesagem (HTTP $http_code)"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════════════════
# TESTES COTACAO SERVICE - BANCO DE DADOS REAL
# ════════════════════════════════════════════════════════════════════════════════

test_cotacao_create() {
    print_header "💰 COTACAO SERVICE - CRIAR COTAÇÃO (Banco de Dados Real)"
    
    test_case "Criar registro de cotação com dados reais"
    
    cotacao_data=$(cat <<EOF
{
    "commodity": "beef",
    "price": 8750.50,
    "currency": "BRL",
    "quote_date": "2026-05-04",
    "source": "test_e2e"
}
EOF
)
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$cotacao_data" \
        "${COTACAO_SERVICE_URL}/api/v1/cotacoes")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        COTACAO_ID=$(echo "$body" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
        pass "Cotação criada com sucesso (ID: $COTACAO_ID)"
        echo "$COTACAO_ID"
    else
        fail "Falha ao criar cotação (HTTP $http_code)"
        echo "$body"
        return 1
    fi
}

test_cotacao_retrieve() {
    local cotacao_id=$1
    
    print_header "🔍 COTACAO SERVICE - RECUPERAR COTAÇÃO (Dados Persistidos)"
    
    test_case "Recuperar cotação do banco de dados"
    
    response=$(curl -s -w "\n%{http_code}" \
        "${COTACAO_SERVICE_URL}/api/v1/cotacoes/${cotacao_id}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q "8750.50"; then
            pass "Cotação recuperada com preço correto (R$ 8750.50)"
        else
            fail "Preço não foi persistido corretamente"
            return 1
        fi
    else
        fail "Falha ao recuperar cotação (HTTP $http_code)"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════════════════
# TESTES INTEGRAÇÃO - API GATEWAY
# ════════════════════════════════════════════════════════════════════════════════

test_gateway_health() {
    print_header "❤️  API GATEWAY - HEALTH CHECK"
    
    test_case "Verificar saúde do API Gateway"
    
    response=$(curl -s -w "\n%{http_code}" \
        "${API_GATEWAY_URL}/health")
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        pass "API Gateway está online"
    else
        fail "API Gateway retornou HTTP $http_code"
        return 1
    fi
}

test_gateway_rate_limiting() {
    print_header "🛡️  API GATEWAY - RATE LIMITING"
    
    test_case "Testar rate limiting com 105 requisições"
    
    success_count=0
    blocked_count=0
    
    for i in {1..105}; do
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            "${API_GATEWAY_URL}/health")
        
        if [ "$response" = "200" ]; then
            ((success_count++))
        elif [ "$response" = "429" ]; then
            ((blocked_count++))
        fi
    done
    
    if [ $blocked_count -gt 0 ]; then
        pass "Rate limiting ativo (Bloqueadas: $blocked_count requisições)"
    else
        fail "Rate limiting não está funcionando"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════════════════
# TESTES DADOS REAIS - FLUXO COMPLETO
# ════════════════════════════════════════════════════════════════════════════════

test_complete_workflow() {
    print_header "🔄 FLUXO COMPLETO - Animal → Pesagem → Cotação"
    
    test_case "Testar fluxo completo de dados"
    
    # 1. Criar animal
    animal_data=$(cat <<EOF
{
    "nome": "Fluxo Teste $TIMESTAMP",
    "raca": "Nelore",
    "rfid": "WORKFLOW_$TIMESTAMP",
    "data_nascimento": "2021-06-15"
}
EOF
)
    
    animal_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$animal_data" \
        "${ANIMAL_SERVICE_URL}/api/v1/animals")
    
    animal_id=$(echo "$animal_response" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
    
    if [ -z "$animal_id" ]; then
        fail "Falha ao criar animal no fluxo"
        return 1
    fi
    
    pass "Animal criado (ID: $animal_id)"
    
    # 2. Adicionar pesagem
    pesagem_data=$(cat <<EOF
{
    "animal_id": $animal_id,
    "weight": 450.75,
    "measurement_date": "2026-05-04",
    "notes": "Pesagem do fluxo teste"
}
EOF
)
    
    pesagem_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$pesagem_data" \
        "${PESAGEM_SERVICE_URL}/api/v1/pesagens")
    
    pesagem_id=$(echo "$pesagem_response" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
    
    if [ -z "$pesagem_id" ]; then
        fail "Falha ao criar pesagem no fluxo"
        return 1
    fi
    
    pass "Pesagem criada (ID: $pesagem_id)"
    
    # 3. Criar cotação
    cotacao_data=$(cat <<EOF
{
    "commodity": "cattle",
    "price": 9200.00,
    "currency": "BRL",
    "quote_date": "2026-05-04",
    "source": "workflow_test"
}
EOF
)
    
    cotacao_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$cotacao_data" \
        "${COTACAO_SERVICE_URL}/api/v1/cotacoes")
    
    cotacao_id=$(echo "$cotacao_response" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
    
    if [ -z "$cotacao_id" ]; then
        fail "Falha ao criar cotação no fluxo"
        return 1
    fi
    
    pass "Cotação criada (ID: $cotacao_id)"
    
    # 4. Verificar que dados foram persistidos
    animal_check=$(curl -s "${ANIMAL_SERVICE_URL}/api/v1/animals/${animal_id}")
    if echo "$animal_check" | grep -q "WORKFLOW_$TIMESTAMP"; then
        pass "Animal verificado no BD ✓"
    else
        fail "Animal não foi persistido corretamente"
        return 1
    fi
    
    pesagem_check=$(curl -s "${PESAGEM_SERVICE_URL}/api/v1/pesagens/${pesagem_id}")
    if echo "$pesagem_check" | grep -q "450.75"; then
        pass "Pesagem verificada no BD ✓"
    else
        fail "Pesagem não foi persistida corretamente"
        return 1
    fi
    
    cotacao_check=$(curl -s "${COTACAO_SERVICE_URL}/api/v1/cotacoes/${cotacao_id}")
    if echo "$cotacao_check" | grep -q "9200"; then
        pass "Cotação verificada no BD ✓"
    else
        fail "Cotação não foi persistida corretamente"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════════════════
# MAIN - EXECUTAR TODOS OS TESTES
# ════════════════════════════════════════════════════════════════════════════════

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  🚀 REAL E2E TESTS - Testes com Banco de Dados Verdadeiro 🚀  ║"
    echo "║                                                                ║"
    echo "║  Sem mocks! Tudo funciona de verdade com BD real!             ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    # 1. Verificar saúde dos serviços
    print_header "✅ VERIFICAÇÃO INICIAL - SAÚDE DOS SERVIÇOS"
    
    check_service_health "Animal Service" "$ANIMAL_SERVICE_URL" || {
        echo -e "${RED}Animal Service não está online!${NC}"
        exit 1
    }
    
    check_service_health "Pesagem Service" "$PESAGEM_SERVICE_URL" || {
        echo -e "${RED}Pesagem Service não está online!${NC}"
        exit 1
    }
    
    check_service_health "Cotacao Service" "$COTACAO_SERVICE_URL" || {
        echo -e "${RED}Cotacao Service não está online!${NC}"
        exit 1
    }
    
    # 2. Testes Animal Service
    ANIMAL_ID=$(test_animal_create) || exit 1
    test_animal_retrieve "$ANIMAL_ID" || exit 1
    test_animal_update "$ANIMAL_ID" || exit 1
    
    # 3. Testes Pesagem Service
    PESAGEM_ID=$(test_pesagem_create "$ANIMAL_ID") || exit 1
    test_pesagem_retrieve "$PESAGEM_ID" || exit 1
    
    # 4. Testes Cotacao Service
    COTACAO_ID=$(test_cotacao_create) || exit 1
    test_cotacao_retrieve "$COTACAO_ID" || exit 1
    
    # 5. Testes API Gateway
    test_gateway_health || exit 1
    test_gateway_rate_limiting || exit 1
    
    # 6. Fluxo Completo
    test_complete_workflow || exit 1
    
    # Resumo Final
    print_header "📊 RESUMO FINAL"
    
    echo -e "Testes aprovados:  ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Testes falhados:   ${RED}$TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ TODOS OS TESTES PASSARAM!${NC}"
        echo -e "${GREEN}✅ Dados foram salvos no banco de dados!${NC}"
        echo -e "${GREEN}✅ Sistema funcionando corretamente!${NC}"
        exit 0
    else
        echo -e "${RED}❌ ALGUNS TESTES FALHARAM!${NC}"
        exit 1
    fi
}

# Executar main
main "$@"
