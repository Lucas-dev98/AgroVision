#!/bin/bash

# Simple E2E Tests for Real Microservices with Database Persistence
# Without mocks - Everything is REAL!

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Service URLs
ANIMAL_SERVICE_URL="http://localhost:8100"
PESAGEM_SERVICE_URL="http://localhost:8101"
COTACAO_SERVICE_URL="http://localhost:8102"

# Test counters
PASSED=0
FAILED=0

# Helper functions
print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Test 1: Create Animal
test_create_animal() {
    print_header "TEST 1: Create Animal" >&2
    print_test "Creating animal in database" >&2
    
    TIMESTAMP=$(date +%s)
    ANIMAL_NAME="Animal_$TIMESTAMP"
    ANIMAL_RFID="RFID_$TIMESTAMP"
    
    RESPONSE=$(curl -s -X POST "$ANIMAL_SERVICE_URL/api/v1/animals" \
        -H "Content-Type: application/json" \
        -d "{\"nome\":\"$ANIMAL_NAME\",\"raca\":\"Angus\",\"rfid\":\"$ANIMAL_RFID\"}")
    
    ANIMAL_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
    
    if [ -n "$ANIMAL_ID" ]; then
        print_pass "Animal created with ID: $ANIMAL_ID" >&2
        echo "$ANIMAL_ID"
    else
        print_fail "Failed to create animal" >&2
        echo "$RESPONSE" >&2
        return 1
    fi
}

# Test 2: Retrieve Animal
test_retrieve_animal() {
    local animal_id=$1
    print_header "TEST 2: Retrieve Animal" >&2
    print_test "Retrieving animal from database" >&2
    
    RESPONSE=$(curl -s "$ANIMAL_SERVICE_URL/api/v1/animals/$animal_id")
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        print_pass "Animal retrieved successfully" >&2
        echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    else
        print_fail "Failed to retrieve animal" >&2
        echo "$RESPONSE" >&2
        return 1
    fi
}

# Test 3: Update Animal
test_update_animal() {
    local animal_id=$1
    print_header "TEST 3: Update Animal" >&2
    print_test "Updating animal in database" >&2
    
    TIMESTAMP=$(date +%s)
    UPDATED_NAME="Animal_Updated_$TIMESTAMP"
    
    RESPONSE=$(curl -s -X PUT "$ANIMAL_SERVICE_URL/api/v1/animals/$animal_id" \
        -H "Content-Type: application/json" \
        -d "{\"nome\":\"$UPDATED_NAME\",\"raca\":\"Angus\"}")
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        print_pass "Animal updated successfully" >&2
    else
        print_fail "Failed to update animal" >&2
        echo "$RESPONSE" >&2
        return 1
    fi
}

# Test 4: Create Pesagem (Weighing)
test_create_pesagem() {
    local animal_id=$1
    print_header "TEST 4: Create Pesagem (Weighing)" >&2
    print_test "Creating weighing record for animal" >&2
    
    RESPONSE=$(curl -s -X POST "$PESAGEM_SERVICE_URL/api/v1/pesagens" \
        -H "Content-Type: application/json" \
        -d "{\"animal_id\":$animal_id,\"peso_kg\":500.5,\"data\":\"2026-05-04\"}")
    
    PESAGEM_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
    
    if [ -n "$PESAGEM_ID" ]; then
        print_pass "Pesagem created with ID: $PESAGEM_ID" >&2
        echo "$PESAGEM_ID"
    else
        print_fail "Failed to create pesagem" >&2
        echo "$RESPONSE" >&2
        return 1
    fi
}

# Test 5: Retrieve Pesagem
test_retrieve_pesagem() {
    local pesagem_id=$1
    print_header "TEST 5: Retrieve Pesagem" >&2
    print_test "Retrieving pesagem from database" >&2
    
    RESPONSE=$(curl -s "$PESAGEM_SERVICE_URL/api/v1/pesagens/$pesagem_id")
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        print_pass "Pesagem retrieved successfully" >&2
    else
        print_fail "Failed to retrieve pesagem" >&2
        echo "$RESPONSE" >&2
        return 1
    fi
}

# Test 6: Create Cotacao (Quote)
test_create_cotacao() {
    print_header "TEST 6: Create Cotacao (Quote)" >&2
    print_test "Creating price quote" >&2
    
    RESPONSE=$(curl -s -X POST "$COTACAO_SERVICE_URL/api/v1/cotacoes" \
        -H "Content-Type: application/json" \
        -d "{\"preco_arroba\":9200.00,\"data_referencia\":\"2026-05-04\"}")
    
    COTACAO_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
    
    if [ -n "$COTACAO_ID" ]; then
        print_pass "Cotacao created with ID: $COTACAO_ID" >&2
        echo "$COTACAO_ID"
    else
        print_fail "Failed to create cotacao" >&2
        echo "$RESPONSE" >&2
        return 1
    fi
}

# Test 7: Retrieve Cotacao
test_retrieve_cotacao() {
    local cotacao_id=$1
    print_header "TEST 7: Retrieve Cotacao" >&2
    print_test "Retrieving cotacao from database" >&2
    
    RESPONSE=$(curl -s "$COTACAO_SERVICE_URL/api/v1/cotacoes/$cotacao_id")
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        print_pass "Cotacao retrieved successfully" >&2
    else
        print_fail "Failed to retrieve cotacao" >&2
        echo "$RESPONSE" >&2
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  🚀 REAL E2E TESTS - Banco de Dados Verdadeiro 🚀             ║"
    echo "║  Sem mocks! Tudo funciona de verdade com BD real!             ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Run all tests
    ANIMAL_ID=$(test_create_animal) || exit 1
    test_retrieve_animal "$ANIMAL_ID" || exit 1
    test_update_animal "$ANIMAL_ID" || exit 1
    
    PESAGEM_ID=$(test_create_pesagem "$ANIMAL_ID") || exit 1
    test_retrieve_pesagem "$PESAGEM_ID" || exit 1
    
    COTACAO_ID=$(test_create_cotacao) || exit 1
    test_retrieve_cotacao "$COTACAO_ID" || exit 1
    
    # Summary
    print_header "📊 TEST SUMMARY"
    echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
    echo -e "Tests Failed: ${RED}$FAILED${NC}"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
        echo -e "${GREEN}✅ Data was saved to database successfully!${NC}"
        echo -e "${GREEN}✅ Real E2E testing working correctly!${NC}"
        return 0
    else
        echo -e "${RED}❌ SOME TESTS FAILED!${NC}"
        return 1
    fi
}

main "$@"
