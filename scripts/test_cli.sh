#!/bin/bash

# Test script for Playwright Backend Service CLI
# This script tests various CLI scenarios and validates outputs

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit_code="${3:-0}"
    
    print_status "Running test: $test_name"
    ((TESTS_RUN++))
    
    # Create temporary file for output
    local temp_output=$(mktemp)
    local exit_code=0
    
    # Run command and capture output
    eval "$test_command" > "$temp_output" 2>&1 || exit_code=$?
    
    # Check exit code
    if [ $exit_code -eq $expected_exit_code ]; then
        print_success "$test_name"
        ((TESTS_PASSED++))
        
        # Display output for successful tests
        if [ -s "$temp_output" ]; then
            echo "Output:"
            cat "$temp_output" | head -5
            echo "---"
        fi
    else
        print_error "$test_name (exit code: $exit_code, expected: $expected_exit_code)"
        ((TESTS_FAILED++))
        
        # Display error output
        if [ -s "$temp_output" ]; then
            echo "Error output:"
            cat "$temp_output" | head -10
            echo "---"
        fi
    fi
    
    # Cleanup
    rm -f "$temp_output"
    echo
}

# Function to test JSON output validity
test_json_output() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Running JSON validation test: $test_name"
    ((TESTS_RUN++))
    
    # Create temporary file for output
    local temp_output=$(mktemp)
    local exit_code=0
    
    # Run command and capture output
    eval "$test_command" > "$temp_output" 2>&1 || exit_code=$?
    
    # Check if output is valid JSON
    if python3 -m json.tool < "$temp_output" > /dev/null 2>&1; then
        print_success "$test_name (valid JSON)"
        ((TESTS_PASSED++))
        
        # Display parsed JSON
        echo "Parsed JSON:"
        python3 -c "import json; print(json.dumps(json.load(open('$temp_output')), indent=2))" | head -10
        echo "---"
    else
        print_error "$test_name (invalid JSON)"
        ((TESTS_FAILED++))
        
        # Display raw output
        echo "Raw output:"
        cat "$temp_output" | head -10
        echo "---"
    fi
    
    # Cleanup
    rm -f "$temp_output"
    echo
}

echo "Starting CLI Tests for Playwright Backend Service"
echo "=================================================="
echo

# Test 1: Basic help/version
run_test "Help/Version Test" "python3 -m src.cli --help || python3 -m src.cli" 1

# Test 2: Basic navigation test
test_json_output "Basic Navigation Test" "python3 -m src.cli '{\"url\": \"https://example.com\", \"extract\": [{\"name\": \"title\", \"selector\": \"h1\"}]}'"

# Test 3: Invalid JSON input
run_test "Invalid JSON Test" "python3 -m src.cli '{invalid-json}'" 1

# Test 4: Invalid URL test
run_test "Invalid URL Test" "python3 -m src.cli '{\"url\": \"invalid-url\"}'" 1

# Test 5: Missing required fields
run_test "Missing URL Test" "python3 -m src.cli '{\"extract\": [{\"name\": \"title\", \"selector\": \"h1\"}]}'" 1

# Test 6: Empty input test
run_test "Empty Input Test" "python3 -m src.cli '{}'" 1

# Test 7: Minimal valid input
test_json_output "Minimal Valid Input Test" "python3 -m src.cli '{\"url\": \"https://example.com\"}'"

# Test 8: Multiple extraction test
test_json_output "Multiple Extraction Test" "python3 -m src.cli '{\"url\": \"https://example.com\", \"extract\": [{\"name\": \"title\", \"selector\": \"h1\"}, {\"name\": \"links\", \"selector\": \"a\", \"attribute\": \"href\", \"multiple\": true}]}'"

# Test 9: Custom viewport test
test_json_output "Custom Viewport Test" "python3 -m src.cli '{\"url\": \"https://example.com\", \"viewport\": {\"width\": 800, \"height\": 600}, \"extract\": [{\"name\": \"title\", \"selector\": \"h1\"}]}'"

# Test 10: Action test (if httpbin is available)
test_json_output "Action Test" "python3 -m src.cli '{\"url\": \"https://httpbin.org/forms/post\", \"actions\": [{\"type\": \"fill\", \"selector\": \"input[name=\\\"custname\\\"]\", \"value\": \"Test User\"}], \"extract\": [{\"name\": \"form_title\", \"selector\": \"h1\"}]}'"

# Test 11: Timeout test with fast timeout
run_test "Timeout Test" "python3 -m src.cli '{\"url\": \"https://httpbin.org/delay/10\", \"timeout\": 1000}'" 1

# Test 12: Security test - blocked domain
run_test "Security Test (Blocked Domain)" "python3 -m src.cli '{\"url\": \"http://localhost:8080\"}'" 1

# Test 13: Large data extraction
test_json_output "Large Data Test" "python3 -m src.cli '{\"url\": \"https://quotes.toscrape.com/\", \"extract\": [{\"name\": \"quotes\", \"selector\": \".quote .text\", \"multiple\": true}, {\"name\": \"authors\", \"selector\": \".quote .author\", \"multiple\": true}]}'"

# Test 14: Stdin input test
print_status "Testing stdin input"
((TESTS_RUN++))
echo '{"url": "https://example.com", "extract": [{"name": "title", "selector": "h1"}]}' | python3 -m src.cli
if [ $? -eq 0 ]; then
    print_success "Stdin Input Test"
    ((TESTS_PASSED++))
else
    print_error "Stdin Input Test"
    ((TESTS_FAILED++))
fi
echo

# Test 15: Performance test
print_status "Performance Test (should complete within 10 seconds)"
((TESTS_RUN++))
start_time=$(date +%s)
python3 -m src.cli '{"url": "https://example.com", "extract": [{"name": "title", "selector": "h1"}]}' > /dev/null 2>&1
end_time=$(date +%s)
duration=$((end_time - start_time))

if [ $duration -le 10 ]; then
    print_success "Performance Test (completed in ${duration}s)"
    ((TESTS_PASSED++))
else
    print_error "Performance Test (took ${duration}s, expected ≤10s)"
    ((TESTS_FAILED++))
fi
echo

# Summary
echo "Test Results Summary"
echo "===================="
echo "Total tests run: $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo

if [ $TESTS_FAILED -eq 0 ]; then
    print_success "All tests passed! 🎉"
    exit 0
else
    print_error "Some tests failed. Please review the output above."
    exit 1
fi 