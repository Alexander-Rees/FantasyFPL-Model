#!/bin/bash

# System Verification Script
# Tests all services and endpoints to ensure everything works

set -e

echo "🔍 FPL Optimization System - Verification Script"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for results
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    
    if response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n1)
        if [ "$http_code" -eq "$expected_status" ]; then
            echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
            ((PASSED++))
            return 0
        else
            echo -e "${RED}✗ FAILED${NC} (Expected HTTP $expected_status, got $http_code)"
            ((FAILED++))
            return 1
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (Connection error)"
        ((FAILED++))
        return 1
    fi
}

echo "📋 Service Health Checks"
echo "------------------------"

# Test Flask API
test_endpoint "Flask API Health" "http://localhost:5001/health" 200

# Test Spring Boot Actuator
test_endpoint "Spring Boot Actuator Health" "http://localhost:8081/actuator/health" 200

echo ""
echo "📋 API Endpoints"
echo "----------------"

# Test Player API
test_endpoint "Player API (v1)" "http://localhost:8081/api/v1/players?page=0&size=5" 200

# Test Legacy Player API
test_endpoint "Player API (legacy)" "http://localhost:8081/api/players?page=0&size=5" 200

echo ""
echo "📋 Monitoring Endpoints"
echo "----------------------"

# Test Prometheus metrics
test_endpoint "Prometheus Metrics" "http://localhost:8081/actuator/prometheus" 200

# Test Flask metrics
test_endpoint "Flask Metrics" "http://localhost:5001/metrics" 200

echo ""
echo "📋 Documentation"
echo "----------------"

# Test Swagger UI
test_endpoint "Swagger UI" "http://localhost:8081/swagger-ui.html" 200

# Test OpenAPI docs
test_endpoint "OpenAPI Docs" "http://localhost:8081/v3/api-docs" 200

echo ""
echo "================================================"
echo "📊 Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! System is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the services.${NC}"
    exit 1
fi

