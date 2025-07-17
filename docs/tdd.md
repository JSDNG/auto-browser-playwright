# Test Driven Development (TDD) - Playwright Server for n8n Integration

## 1. Tổng quan

Xây dựng Playwright server để:

-   **n8n Integration**: Nhận HTTP requests từ n8n workflows
-   **Default Configuration**: Sử dụng config mặc định (Amazon product search)
-   **Data Extraction**: Tự động lấy thông tin từ trang web
-   **Stealth Mode**: Tránh detection với anti-bot features
-   **JSON Output**: Trả về structured data cho n8n

## 1.1. Server Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│      n8n        │─────▶│  FastAPI Server │─────▶│   Target Site   │
│   Workflow      │ HTTP │  (Port 8000)    │      │   (Amazon)      │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                 │                         │
                                 ▼                         ▼
                         ┌─────────────────┐      ┌─────────────────┐
                         │  Default Config │      │  Data Extraction│
                         │ (Amazon Search) │      │   (Products)    │
                         └─────────────────┘      └─────────────────┘
                                 │                         │
                                 ▼                         ▼
                         ┌─────────────────┐      ┌─────────────────┐
                         │  Stealth Mode   │◀─────│  JSON Response  │
                         │   Playwright    │      │   to n8n        │
                         └─────────────────┘      └─────────────────┘
```

## 1.2. Project Structure

```
playwright/
├── src/                          # Source code
│   ├── __init__.py
│   ├── app/
│   │   ├── server.py             # FastAPI server for n8n
│   │   ├── main.py               # CLI tool (legacy)
│   ├── core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── automation.py         # Stealth mode Playwright engine
│   │   ├── actions.py            # Action executor with data extraction
│   │   └── extractor.py          # Data extraction utilities
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── input.py              # Request/Action validation
│   │   └── output.py             # Response format models
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── validators.py         # Input validators
│       ├── formatters.py         # Output formatters
│       └── logger.py             # Logging utilities
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py
│   │   ├── test_server.py        # Server endpoint tests
│   │   ├── test_automation.py    # Automation engine tests
│   │   ├── test_actions.py       # Action executor tests
│   │   └── test_extraction.py    # Data extraction tests
│   ├── integration/              # Integration tests
│   │   ├── __init__.py
│   │   ├── test_n8n_integration.py  # n8n workflow tests
│   │   └── test_amazon_scraping.py # Amazon scraping tests
│   └── fixtures/                 # Test fixtures
│       ├── __init__.py
│       ├── n8n_requests.json     # Sample n8n requests
│       └── amazon_responses.json # Sample Amazon responses
├── docker/                       # Docker configurations
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                         # Documentation
│   ├── tdd.md                    # This file
│   ├── implement.md              # Implementation guide
│   └── tasks.md                  # Task breakdown
└── examples/                     # Usage examples
    ├── n8n_workflow.json         # Sample n8n workflow
    ├── server_test.py            # Server testing script
    └── curl_examples.sh          # API testing examples
```

## 1.3. n8n Integration Setup

### 1.3.1. Server Startup

```bash
# Start the server
python src/app/server.py

# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 1.3.2. n8n HTTP Request Node Configuration

```json
{
    "method": "POST",
    "url": "http://localhost:8000/automation",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": {
        "url": "https://www.amazon.com/",
        "extract_data": true
    }
}
```

### 1.3.3. Default Configuration

**Server sử dụng config mặc định cho Amazon product search:**

```python
def get_default_config():
    return {
        "url": "https://www.amazon.com/",
        "actions": [
            # Search for "laptop"
            {"type": "click", "selector": "#twotabsearchtextbox"},
            {"type": "fill", "selector": "#twotabsearchtextbox", "value": "laptop"},
            {"type": "click", "selector": "#nav-search-submit-button"},
            # Extract product data
            {"type": "get_all_text", "selector": "[data-component-type='s-search-result'] h2 a span", "extract_name": "product_titles"},
            {"type": "get_all_text", "selector": "[data-component-type='s-search-result'] .a-price-whole", "extract_name": "product_prices"},
            {"type": "get_all_attributes", "selector": "[data-component-type='s-search-result'] h2 a", "attribute": "href", "extract_name": "product_links"},
            {"type": "get_all_attributes", "selector": "[data-component-type='s-search-result'] img", "attribute": "src", "extract_name": "product_images"}
        ]
    }
```

## 2. User Stories & Test Cases

### 2.1. User Story: n8n Integration

**As a** n8n user  
**I want to** call Playwright server from n8n workflow  
**So that** I can extract product data from Amazon automatically

**Test Cases:**

-   TC_001: n8n sends HTTP POST to /automation endpoint
-   TC_002: Server returns JSON with extracted product data
-   TC_003: Server handles errors gracefully
-   TC_004: n8n receives structured data for further processing

### 2.2. User Story: Default Configuration

**As a** server  
**I want to** use default Amazon search configuration  
**So that** n8n doesn't need to provide complex setup

**Test Cases:**

-   TC_005: Server uses default URL (Amazon)
-   TC_006: Server executes default actions (search laptop)
-   TC_007: Server extracts default data (products)
-   TC_008: Server returns metadata (page title, timestamp)

### 2.3. User Story: Data Extraction

**As a** n8n workflow  
**I want to** receive extracted product information  
**So that** I can process and store the data

**Test Cases:**

-   TC_009: Extract product titles from search results
-   TC_010: Extract product prices from search results
-   TC_011: Extract product links from search results
-   TC_012: Extract product images from search results
-   TC_013: Return structured JSON response

### 2.4. User Story: Stealth Mode

**As a** automation server  
**I want to** avoid Amazon's bot detection  
**So that** scraping works reliably

**Test Cases:**

-   TC_014: Use stealth browser configuration
-   TC_015: Pass Amazon's anti-bot measures
-   TC_016: Handle CAPTCHAs gracefully
-   TC_017: Maintain consistent success rate

## 3. API Endpoints

### 3.1. Main Automation Endpoint

**POST** `/automation`

**Request Body (Optional):**

```json
{
  "url": "https://www.amazon.com/",
  "actions": [...],
  "extract_data": true
}
```

**Response:**

```json
{
    "success": true,
    "data": {
        "product_titles": ["Laptop 1", "Laptop 2", "..."],
        "product_prices": ["$999", "$1299", "..."],
        "product_links": ["https://amazon.com/product1", "..."],
        "product_images": ["https://images.amazon.com/img1.jpg", "..."],
        "page_url": "https://www.amazon.com/",
        "page_title": "Amazon.com: laptop",
        "extraction_timestamp": 1703123456.789
    },
    "error": null,
    "timestamp": "2024-01-01T00:00:00Z",
    "execution_time": 15.3
}
```

### 3.2. Custom Configuration Endpoint

**POST** `/automation/custom`

**Request Body:**

```json
{
    "url": "https://www.amazon.com/",
    "actions": [
        { "type": "click", "selector": "#twotabsearchtextbox" },
        { "type": "fill", "selector": "#twotabsearchtextbox", "value": "smartphone" },
        { "type": "click", "selector": "#nav-search-submit-button" },
        { "type": "get_all_text", "selector": "h2 a span", "extract_name": "phone_titles" }
    ],
    "headless": false,
    "timeout": 30000
}
```

### 3.3. Health Check Endpoint

**GET** `/health`

**Response:**

```json
{
    "status": "healthy",
    "timestamp": 1703123456.789,
    "service": "playwright-automation-server"
}
```

## 4. Test Requirements

### 4.1. Server Integration Tests

**Mô tả:** Test server endpoints và n8n integration

**Test Scenarios:**

-   Server startup và shutdown
-   HTTP request handling
-   JSON response validation
-   Error handling và status codes

**Expected Behavior:**

-   Server responds within 30 seconds
-   JSON response matches schema
-   Errors return appropriate HTTP status
-   Health check always returns 200

### 4.2. Data Extraction Tests

**Mô tả:** Test data extraction accuracy

**Test Scenarios:**

-   Amazon product title extraction
-   Price extraction với currency handling
-   Link extraction với absolute URLs
-   Image extraction với valid URLs

**Expected Behavior:**

-   Extract at least 10 products per search
-   95% accuracy for product titles
-   Valid URLs for all links
-   No broken image URLs

### 4.3. Stealth Mode Tests

**Mô tả:** Test Amazon bot detection avoidance

**Test Scenarios:**

-   Multiple requests without blocking
-   CAPTCHA handling
-   Rate limiting detection
-   Success rate monitoring

**Expected Behavior:**

-   90% success rate over 100 requests
-   No permanent IP blocking
-   Graceful CAPTCHA handling
-   Consistent response times

### 4.4. n8n Workflow Tests

**Mô tả:** Test actual n8n integration

**Test Scenarios:**

-   n8n HTTP Request node configuration
-   Data flow through n8n workflow
-   Error handling in n8n
-   Performance benchmarks

**Expected Behavior:**

-   n8n receives properly formatted JSON
-   Data flows to subsequent nodes
-   Errors don't break workflow
-   Complete workflow < 60 seconds

## 5. Acceptance Criteria

### 5.1. Server Requirements

**AC_001:** Server must start on port 8000  
**AC_002:** Must respond to /automation endpoint  
**AC_003:** Must return JSON with extracted data  
**AC_004:** Must handle errors gracefully  
**AC_005:** Must provide health check endpoint

### 5.2. Data Extraction Requirements

**AC_006:** Must extract product titles from Amazon  
**AC_007:** Must extract product prices  
**AC_008:** Must extract product links  
**AC_009:** Must extract product images  
**AC_010:** Must return structured JSON response

### 5.3. n8n Integration Requirements

**AC_011:** Must accept HTTP POST requests from n8n  
**AC_012:** Must return data in n8n-compatible format  
**AC_013:** Must handle n8n timeout requirements  
**AC_014:** Must provide clear error messages  
**AC_015:** Must support workflow debugging

### 5.4. Performance Requirements

**AC_016:** Response time < 30 seconds  
**AC_017:** Success rate > 90%  
**AC_018:** Memory usage < 500MB  
**AC_019:** CPU usage < 80%  
**AC_020:** Concurrent requests support

## 6. Test Coverage Requirements

### 6.1. Unit Tests Coverage

**Target:** 90% code coverage for server components

-   `src/app/server.py`: FastAPI endpoints
-   `src/core/actions.py`: Data extraction actions
-   `src/core/automation.py`: Stealth mode engine
-   `src/models/`: Request/response models

### 6.2. Integration Tests Coverage

**Target:** Key integration scenarios

-   n8n HTTP request integration
-   Amazon scraping workflow
-   Data extraction pipeline
-   Error handling scenarios

### 6.3. End-to-End Tests Coverage

**Target:** Real-world usage scenarios

-   Complete n8n workflow execution
-   Amazon product data extraction
-   Multiple concurrent requests
-   Performance benchmarks

## 7. Development Workflow

### 7.1. Server Development

1. **Start Development Server**

```bash
# Terminal 1: Start server
python src/app/server.py

# Terminal 2: Test endpoints
curl -X POST http://localhost:8000/automation
```

2. **Test with n8n**

```bash
# Import n8n workflow
n8n import:workflow examples/n8n_workflow.json

# Execute workflow
n8n execute:workflow --id=1
```

### 7.2. Testing Workflow

1. **Unit Tests**

```bash
pytest tests/unit/ -v
```

2. **Integration Tests**

```bash
pytest tests/integration/ -v
```

3. **Performance Tests**

```bash
pytest tests/performance/ -v
```

### 7.3. Deployment Workflow

1. **Docker Build**

```bash
docker build -t playwright-server .
```

2. **Docker Run**

```bash
docker run -p 8000:8000 playwright-server
```

3. **Health Check**

```bash
curl http://localhost:8000/health
```

## 8. Quality Assurance

### 8.1. Code Quality Standards

-   **Type Hints**: Full type annotation for all functions
-   **Documentation**: Comprehensive docstrings
-   **Error Handling**: Graceful error recovery
-   **Logging**: Structured logging for debugging

### 8.2. Performance Standards

-   **Response Time**: < 30 seconds per request
-   **Memory Usage**: < 500MB per instance
-   **Success Rate**: > 90% for Amazon scraping
-   **Concurrent Users**: Support 10 concurrent requests

### 8.3. Security Standards

-   **Input Validation**: Validate all user inputs
-   **Rate Limiting**: Prevent abuse
-   **Error Sanitization**: Don't expose internal errors
-   **HTTPS Support**: Support secure connections

## 9. Monitoring & Maintenance

### 9.1. Health Monitoring

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "playwright-automation-server"
    }
```

### 9.2. Performance Monitoring

```python
# Performance metrics
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    execution_time = time.time() - start_time
    response.headers["X-Execution-Time"] = str(execution_time)
    return response
```

### 9.3. Error Monitoring

```python
# Error tracking
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )
```

## 10. Success Metrics

### 10.1. Technical Metrics

-   **Server Uptime**: 99.9%
-   **Response Time**: < 30 seconds average
-   **Success Rate**: > 90% for data extraction
-   **Memory Usage**: < 500MB steady state

### 10.2. Business Metrics

-   **n8n Integration**: Seamless workflow execution
-   **Data Quality**: Accurate product information
-   **Reliability**: Consistent performance
-   **Scalability**: Support multiple concurrent users

### 10.3. User Experience Metrics

-   **Ease of Use**: Simple n8n node configuration
-   **Error Handling**: Clear error messages
-   **Documentation**: Comprehensive API docs
-   **Support**: Quick issue resolution
