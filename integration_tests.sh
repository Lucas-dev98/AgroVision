#!/bin/bash

# Integration Test Suite for AgroVision Go Backend
# Tests all API endpoints with authentication and validates system integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="http://localhost:9000/api/v1"
AUTH_TOKEN="test-token-12345"
BEARER_AUTH="Authorization: Bearer ${AUTH_TOKEN}"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((TESTS_FAILED++))
}

log_test_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}"
}

test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local data=$4
    local description=$5
    
    ((TESTS_RUN++))
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            "${API_BASE_URL}${endpoint}" \
            -H "$BEARER_AUTH" \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            "${API_BASE_URL}${endpoint}" \
            -H "$BEARER_AUTH" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # Extract HTTP status code (last line)
    http_code=$(echo "$response" | tail -n1)
    # Extract response body (all lines except last)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "$expected_status" ]; then
        log_success "$description (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
        return 0
    else
        log_error "$description - Expected HTTP $expected_status, got HTTP $http_code"
        echo "Response: $body"
        return 1
    fi
}

# ============================================================
# TEST SUITE
# ============================================================

log_info "Starting Integration Tests for AgroVision"
log_info "API Base URL: $API_BASE_URL"
log_info "Using test auth token: $AUTH_TOKEN"
sleep 2

# Test 1: Health Check (no auth required)
log_test_header "Health Check Endpoint"
health_response=$(curl -s http://localhost:9000/health)
if echo "$health_response" | grep -q "api-gateway"; then
    log_success "API Gateway health check passed"
    echo "$health_response" | jq .
else
    log_error "API Gateway health check failed"
    echo "$health_response"
fi

# Test 2: Unauthorized Access (no token)
log_test_header "Unauthorized Access Tests"
((TESTS_RUN++))
unauth_response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE_URL}/animals")
unauth_code=$(echo "$unauth_response" | tail -n1)
if [ "$unauth_code" = "401" ]; then
    log_success "Unauthorized request properly rejected (HTTP 401)"
else
    log_error "Unauthorized request not properly rejected - got HTTP $unauth_code"
fi

# Test 3: Animal Service - GET all (empty initially)
log_test_header "Animal Service - GET All"
test_endpoint "GET" "/animals" "200" "" "Fetch all animals (should be empty or valid list)"

# Test 4: Animal Service - CREATE
log_test_header "Animal Service - CREATE Animal"
create_animal_data='{
  "ear_tag": "TEST-001",
  "rfid": "RF-TEST-001",
  "name": "Test Animal",
  "species": "Bovino",
  "breed": "Nelore",
  "weight_kg": 450,
  "birth_date": "2020-01-15",
  "status": "healthy"
}'
test_endpoint "POST" "/animals" "201" "$create_animal_data" "Create new animal"

# Test 5: Animal Service - GET specific
log_test_header "Animal Service - GET Specific"
test_endpoint "GET" "/animals/1" "200" "" "Get animal by ID"

# Test 6: Pesagem Service - GET all
log_test_header "Pesagem Service - GET All"
test_endpoint "GET" "/pesagens" "200" "" "Fetch all weighing records"

# Test 7: Pesagem Service - CREATE
log_test_header "Pesagem Service - CREATE Weighing Record"
create_pesagem_data='{
  "animal_id": 1,
  "weight_kg": 455,
  "measurement_date": "2026-05-04",
  "location": "Corral A",
  "notes": "Routine weighing"
}'
test_endpoint "POST" "/pesagens" "201" "$create_pesagem_data" "Create weighing record"

# Test 8: Cotacao Service - GET all
log_test_header "Cotacao Service - GET All"
test_endpoint "GET" "/cotacoes" "200" "" "Fetch all quotations"

# Test 9: Cotacao Service - CREATE
log_test_header "Cotacao Service - CREATE Quotation"
create_cotacao_data='{
  "animal_id": 1,
  "price_per_kg": 18.50,
  "total_price": 8417.50,
  "market_date": "2026-05-04",
  "notes": "Market quotation",
  "status": "active"
}'
test_endpoint "POST" "/cotacoes" "201" "$create_cotacao_data" "Create quotation"

# Test 10: Frontend API Configuration Check
log_test_header "Frontend Configuration Check"
if [ -f "/home/lucasbastos/AgroVision/frontend/.env.local" ]; then
    api_url=$(grep "VITE_API_URL=" /home/lucasbastos/AgroVision/frontend/.env.local)
    if echo "$api_url" | grep -q "9000"; then
        log_success "Frontend API URL correctly configured for port 9000"
        echo "$api_url"
    else
        log_error "Frontend API URL not configured for port 9000"
        echo "$api_url"
    fi
else
    log_error "Frontend .env.local file not found"
fi

# ============================================================
# Test Summary
# ============================================================
echo -e "\n${YELLOW}=== Test Summary ===${NC}"
echo -e "Total Tests Run: ${BLUE}$TESTS_RUN${NC}"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All integration tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
