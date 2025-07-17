#!/bin/bash

# Curl examples for testing Playwright Automation Server
# Usage: ./curl_examples.sh

echo "🚀 Playwright Automation Server - API Testing Examples"
echo "======================================================"

# Server URL
SERVER_URL="http://localhost:8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if server is running
check_server() {
    echo -e "${YELLOW}Checking server status...${NC}"
    
    if curl -s -f "$SERVER_URL/health" > /dev/null; then
        echo -e "${GREEN}✅ Server is running!${NC}"
        return 0
    else
        echo -e "${RED}❌ Server is not responding. Please start the server first:${NC}"
        echo "   python src/app/server.py"
        return 1
    fi
}

# Function to test health endpoint
test_health() {
    echo -e "\n${BLUE}📊 Testing Health Endpoint${NC}"
    echo "================================"
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
        "$SERVER_URL/health")
    
    echo "$response"
}

# Function to test main automation endpoint
test_automation() {
    echo -e "\n${BLUE}🤖 Testing Main Automation Endpoint (with actions)${NC}"
    echo "================================================="
    
    echo "Request: POST /automation (requires actions)"
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "url": "https://www.amazon.com/",
            "actions": [
                {
                    "type": "click",
                    "selector": "#twotabsearchtextbox",
                    "timeout": 10000
                },
                {
                    "type": "fill",
                    "selector": "#twotabsearchtextbox",
                    "value": "laptop",
                    "timeout": 10000
                },
                {
                    "type": "get_all_text",
                    "selector": "h2 a span",
                    "extract_name": "product_titles",
                    "timeout": 10000
                }
            ]
        }' \
        "$SERVER_URL/automation")
    
    echo "$response"
}

# Function to test default automation endpoint
test_automation_default() {
    echo -e "\n${BLUE}🛍️ Testing Default Automation Endpoint${NC}"
    echo "========================================"
    
    echo "Request: POST /automation/default (no actions required)"
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
        -X POST \
        -H "Content-Type: application/json" \
        "$SERVER_URL/automation/default")
    
    echo "$response"
}

# Function to test custom automation endpoint
test_custom_automation() {
    echo -e "\n${BLUE}⚙️ Testing Custom Automation Endpoint${NC}"
    echo "======================================"
    
    echo "Request: POST /automation/custom (full configuration)"
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "url": "https://www.amazon.com/",
            "headless": true,
            "timeout": 30000,
            "actions": [
                {
                    "type": "click",
                    "selector": "#twotabsearchtextbox",
                    "timeout": 10000
                },
                {
                    "type": "fill",
                    "selector": "#twotabsearchtextbox", 
                    "value": "smartphone",
                    "timeout": 10000
                },
                {
                    "type": "click",
                    "selector": "#nav-search-submit-button",
                    "timeout": 10000
                },
                {
                    "type": "get_all_text",
                    "selector": "h2 a span",
                    "extract_name": "phone_titles",
                    "timeout": 15000
                }
            ]
        }' \
        "$SERVER_URL/automation/custom")
    
    echo "$response"
}

# Function to test get default config
test_default_config() {
    echo -e "\n${BLUE}📋 Testing Default Configuration Endpoint${NC}"
    echo "========================================="
    
    echo "Request: GET /config/default"
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
        "$SERVER_URL/config/default")
    
    echo "$response"
}

# Function to test error handling
test_error_handling() {
    echo -e "\n${BLUE}🚨 Testing Error Handling${NC}"
    echo "=========================="
    
    echo "Request: POST /automation (without actions - should fail)"
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "url": "https://www.amazon.com/"
        }' \
        "$SERVER_URL/automation")
    
    echo "$response"
    
    echo -e "\n${BLUE}🚨 Testing Error Handling - Empty Actions${NC}"
    echo "==========================================="
    
    echo "Request: POST /automation (with empty actions - should fail)"
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "url": "https://www.amazon.com/",
            "actions": []
        }' \
        "$SERVER_URL/automation")
    
    echo "$response"
}

# Function to test with minimal data extraction
test_minimal_extraction() {
    echo -e "\n${BLUE}📝 Testing Minimal Data Extraction${NC}"
    echo "==================================="
    
    echo "Request: POST /automation/custom (minimal extraction)"
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "url": "https://example.com",
            "headless": true,
            "timeout": 15000,
            "actions": [
                {
                    "type": "get_text",
                    "selector": "h1",
                    "extract_name": "page_title",
                    "timeout": 10000
                },
                {
                    "type": "get_all_text",
                    "selector": "p",
                    "extract_name": "paragraphs",
                    "timeout": 10000
                }
            ]
        }' \
        "$SERVER_URL/automation/custom")
    
    echo "$response"
}

# Function to run performance test
test_performance() {
    echo -e "\n${BLUE}⚡ Performance Test${NC}"
    echo "==================="
    
    echo "Running 3 concurrent requests to test performance..."
    
    for i in {1..3}; do
        {
            echo "Request $i starting..."
            time curl -s -X POST \
                -H "Content-Type: application/json" \
                "$SERVER_URL/automation/default" > /dev/null
            echo "Request $i completed!"
        } &
    done
    
    wait
    echo "All requests completed!"
}

# Function to show help
show_help() {
    echo -e "\n${YELLOW}Available test functions:${NC}"
    echo "  health         - Test health endpoint"
    echo "  automation     - Test main automation endpoint (requires actions)"
    echo "  default        - Test default automation endpoint (no actions needed)"
    echo "  custom         - Test custom automation endpoint"
    echo "  config         - Test default configuration endpoint"
    echo "  error          - Test error handling (missing actions)"
    echo "  minimal        - Test minimal data extraction"
    echo "  performance    - Run performance test"
    echo "  all            - Run all tests"
    echo ""
    echo "Usage: $0 [test_name]"
    echo "Example: $0 health"
}

# Main function
main() {
    # Check if server is running
    if ! check_server; then
        exit 1
    fi
    
    # Check command line argument
    case "$1" in
        health)
            test_health
            ;;
        automation)
            test_automation
            ;;
        default)
            test_automation_default
            ;;
        custom)
            test_custom_automation
            ;;
        config)
            test_default_config
            ;;
        error)
            test_error_handling
            ;;
        minimal)
            test_minimal_extraction
            ;;
        performance)
            test_performance
            ;;
        all)
            test_health
            test_automation
            test_automation_default
            test_custom_automation
            test_default_config
            test_minimal_extraction
            test_error_handling
            test_performance
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            echo -e "${YELLOW}No test specified. Running basic tests...${NC}"
            test_health
            test_automation_default
            ;;
        *)
            echo -e "${RED}Unknown test: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

echo -e "\n${GREEN}🎉 Testing completed!${NC}"
echo "======================================================" 