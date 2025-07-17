# Implementation Plan - Playwright Server for n8n Integration

## 1. Kiến trúc hệ thống

### 1.1. n8n Server Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│      n8n        │─────▶│  FastAPI Server │─────▶│   Amazon.com    │
│   HTTP Request  │ POST │  (Port 8000)    │      │  Product Search │
│     Node        │      │                 │      │                 │
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

### 1.2. Core Components

#### FastAPI Server (src/app/server.py)

-   **Technology**: FastAPI + Uvicorn
-   **Purpose**: HTTP endpoint cho n8n workflows
-   **Input**: HTTP POST requests (optional JSON body)
-   **Output**: JSON response với extracted data
-   **Port**: 8000 (default)

#### Default Configuration

-   **Target**: Amazon.com product search
-   **Actions**: Search "laptop", extract products
-   **Data**: Product titles, prices, links, images
-   **Stealth**: Anti-detection browser settings

#### Data Extraction Engine

-   **Single Element**: get_text, get_href, get_src, get_attribute
-   **Multiple Elements**: get_all_text, get_all_attributes
-   **Structured Output**: JSON format cho n8n
-   **Error Handling**: Continue on failures

## 2. Technology Stack

### 2.1. Dependencies

```ini
# requirements.txt
playwright==1.40.0
pydantic==2.5.0
python-dotenv==1.0.0
fastapi==0.104.1
uvicorn==0.24.0
```

### 2.2. Server Configuration

```python
# FastAPI server setup
app = FastAPI(
    title="Playwright Automation Server",
    description="Server for n8n integration with Playwright automation",
    version="1.0.0"
)

# Start server
uvicorn.run(
    "src.app.server:app",
    host="0.0.0.0",
    port=8000,
    reload=True
)
```

## 3. Implementation Details

### 3.1. Project Structure

```
playwright/
├── src/                          # Source code
│   ├── __init__.py
│   ├── app/
│   │   ├── server.py             # FastAPI server for n8n
│   │   └── main.py               # CLI tool (legacy)
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
│   ├── unit/                     # Unit tests
│   │   ├── test_server.py        # Server endpoint tests
│   │   ├── test_automation.py    # Automation engine tests
│   │   └── test_actions.py       # Action executor tests
│   ├── integration/              # Integration tests
│   │   ├── test_n8n_integration.py  # n8n workflow tests
│   │   └── test_amazon_scraping.py # Amazon scraping tests
│   └── fixtures/                 # Test fixtures
│       ├── n8n_requests.json     # Sample n8n requests
│       └── amazon_responses.json # Sample Amazon responses
├── docker/                       # Docker configurations
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                         # Documentation
│   ├── tdd.md                    # Test driven development
│   ├── implement.md              # This file
│   └── tasks.md                  # Task breakdown
└── examples/                     # Usage examples
    ├── n8n_workflow.json         # Sample n8n workflow
    ├── server_test.py            # Server testing script
    └── curl_examples.sh          # API testing examples
```

### 3.2. FastAPI Server Implementation

#### Main Endpoint (POST /automation)

```python
@app.post("/automation")
async def run_automation(request: AutomationRequest = None):
    """
    Main automation endpoint for n8n integration.

    - Uses default configuration if no request body provided
    - Returns extracted data from the automation process
    - Supports custom URL and actions override
    """
    start_time = time.time()

    try:
        # Get default configuration
        automation_config = get_default_config()

        # Override with request data if provided
        if request:
            if request.url:
                automation_config.url = request.url
            if request.actions:
                automation_config.actions = request.actions

        # Run automation
        automation = PlaywrightAutomation(
            headless=automation_config.headless,
            timeout=automation_config.timeout,
            viewport=automation_config.viewport
        )

        await automation.launch()
        await automation.navigate(str(automation_config.url))

        # Execute actions
        action_executor = ActionExecutor(automation.page)
        for action in automation_config.actions:
            await action_executor.execute(action)

        # Get extracted data
        extracted_data = action_executor.get_extracted_data()

        # Add page metadata
        extracted_data["page_url"] = str(automation_config.url)
        extracted_data["page_title"] = await automation.get_page_title()
        extracted_data["extraction_timestamp"] = time.time()

        # Close browser
        await automation.close()

        # Calculate execution time
        execution_time = time.time() - start_time

        # Create success response
        response = create_success_response(
            data=extracted_data,
            execution_time=execution_time
        )

        return response.model_dump()

    except Exception as e:
        # Handle errors gracefully
        response = create_error_response(
            error=str(e),
            error_type="automation"
        )

        raise HTTPException(
            status_code=500,
            detail=response.model_dump()
        )
```

#### Default Configuration

```python
def get_default_config() -> AutomationInput:
    """Get default automation configuration."""
    return AutomationInput(
        url="https://www.amazon.com/",
        headless=False,
        timeout=300000,
        viewport={"width": 1280, "height": 720},
        actions=[
            # Default Amazon product search workflow
            {
                "type": "wait",
                "selector": "body",
                "timeout": 10000
            },
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
                "type": "click",
                "selector": "#nav-search-submit-button",
                "timeout": 10000
            },
            {
                "type": "wait",
                "selector": "[data-component-type='s-search-result']",
                "timeout": 15000
            },
            # Extract product information
            {
                "type": "get_all_text",
                "selector": "[data-component-type='s-search-result'] h2 a span",
                "extract_name": "product_titles"
            },
            {
                "type": "get_all_text",
                "selector": "[data-component-type='s-search-result'] .a-price-whole",
                "extract_name": "product_prices"
            },
            {
                "type": "get_all_attributes",
                "selector": "[data-component-type='s-search-result'] h2 a",
                "attribute": "href",
                "extract_name": "product_links"
            },
            {
                "type": "get_all_attributes",
                "selector": "[data-component-type='s-search-result'] img",
                "attribute": "src",
                "extract_name": "product_images"
            }
        ],
        extract=[]
    )
```

### 3.3. Data Extraction Actions

#### Single Element Extraction

```python
# Extract page title
{"type": "get_text", "selector": "h1", "extract_name": "page_title"}

# Extract specific attribute
{"type": "get_attribute", "selector": "body", "attribute": "class", "extract_name": "body_classes"}

# Extract link href
{"type": "get_href", "selector": "a.main-link", "extract_name": "main_link"}

# Extract image src
{"type": "get_src", "selector": "img.hero-image", "extract_name": "hero_image"}
```

#### Multiple Elements Extraction

```python
# Extract all product titles
{"type": "get_all_text", "selector": ".product-title", "extract_name": "product_titles"}

# Extract all product links
{"type": "get_all_attributes", "selector": ".product-link", "attribute": "href", "extract_name": "product_links"}

# Extract all product images
{"type": "get_all_attributes", "selector": ".product-image", "attribute": "src", "extract_name": "product_images"}
```

### 3.4. n8n Integration

#### n8n HTTP Request Node Configuration

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

#### n8n Response Processing

```json
{
    "success": true,
    "data": {
        "product_titles": ["Dell Laptop", "HP Laptop", "Lenovo Laptop"],
        "product_prices": ["$999", "$1299", "$899"],
        "product_links": ["https://amazon.com/dp/B08N5WRWNW", "..."],
        "product_images": ["https://images-na.ssl-images-amazon.com/images/I/...", "..."],
        "page_url": "https://www.amazon.com/",
        "page_title": "Amazon.com: laptop",
        "extraction_timestamp": 1703123456.789
    },
    "error": null,
    "timestamp": "2024-01-01T00:00:00Z",
    "execution_time": 15.3
}
```

## 4. Development Workflow

### 4.1. Server Development

#### Step 1: Start Development Server

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Start server
python src/app/server.py

# Server accessible at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

#### Step 2: Test Endpoints

```bash
# Test health check
curl http://localhost:8000/health

# Test automation endpoint
curl -X POST http://localhost:8000/automation \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/", "extract_data": true}'

# Test custom configuration
curl -X POST http://localhost:8000/automation/custom \
  -H "Content-Type: application/json" \
  -d @examples/custom_config.json
```

#### Step 3: n8n Integration

```bash
# Start n8n (if installed)
n8n start

# Import workflow
n8n import:workflow examples/n8n_workflow.json

# Test workflow
n8n execute:workflow --id=1
```

### 4.2. Testing Strategy

#### Unit Tests

```bash
# Test server endpoints
pytest tests/unit/test_server.py -v

# Test automation engine
pytest tests/unit/test_automation.py -v

# Test action executor
pytest tests/unit/test_actions.py -v
```

#### Integration Tests

```bash
# Test n8n integration
pytest tests/integration/test_n8n_integration.py -v

# Test Amazon scraping
pytest tests/integration/test_amazon_scraping.py -v
```

#### Performance Tests

```bash
# Load testing
pytest tests/performance/test_load.py -v

# Concurrent requests
pytest tests/performance/test_concurrent.py -v
```

### 4.3. Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium

# Copy application
COPY src/ /app/src/
WORKDIR /app

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "src/app/server.py"]
```

#### Docker Compose

```yaml
version: "3.8"
services:
    playwright-server:
        build: .
        ports:
            - "8000:8000"
        environment:
            - HEADLESS=true
            - TIMEOUT=30000
        healthcheck:
            test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
            interval: 30s
            timeout: 10s
            retries: 3
```

## 5. API Documentation

### 5.1. Endpoints

#### GET /

-   **Description**: API information
-   **Response**: Basic info about the server

#### GET /health

-   **Description**: Health check endpoint
-   **Response**: Server status and timestamp

#### POST /automation

-   **Description**: Main automation endpoint
-   **Request Body**: Optional AutomationRequest
-   **Response**: Extracted data in JSON format

#### POST /automation/custom

-   **Description**: Custom configuration endpoint
-   **Request Body**: Full AutomationInput configuration
-   **Response**: Extracted data in JSON format

#### GET /config/default

-   **Description**: Get default configuration
-   **Response**: Default automation configuration

### 5.2. Response Format

#### Success Response

```json
{
    "success": true,
    "data": {
        "product_titles": ["..."],
        "product_prices": ["..."],
        "product_links": ["..."],
        "product_images": ["..."],
        "page_url": "https://www.amazon.com/",
        "page_title": "Amazon.com: laptop",
        "extraction_timestamp": 1703123456.789
    },
    "error": null,
    "timestamp": "2024-01-01T00:00:00Z",
    "execution_time": 15.3
}
```

#### Error Response

```json
{
    "success": false,
    "data": {},
    "error": "Element not found: .product-title",
    "error_type": "automation",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## 6. Performance Optimization

### 6.1. Server Performance

```python
# Async request handling
@app.post("/automation")
async def run_automation(request: AutomationRequest = None):
    # Async automation execution
    await automation.launch()
    await automation.navigate(url)

    # Parallel data extraction
    tasks = []
    for action in actions:
        task = asyncio.create_task(action_executor.execute(action))
        tasks.append(task)

    await asyncio.gather(*tasks)
```

### 6.2. Browser Optimization

```python
# Optimized browser configuration
browser = await playwright.chromium.launch(
    headless=True,  # Faster execution
    args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-web-security"
    ]
)
```

### 6.3. Memory Management

```python
# Proper resource cleanup
try:
    # Run automation
    result = await run_automation()
    return result
finally:
    # Always cleanup
    await automation.close()
```

## 7. Security Considerations

### 7.1. Input Validation

```python
# Validate all inputs
class AutomationRequest(BaseModel):
    url: Optional[str] = Field(default=None)
    actions: Optional[list] = Field(default=None)
    extract_data: Optional[bool] = Field(default=True)

    @validator("url")
    def validate_url(cls, v):
        if v and not v.startswith("https://"):
            raise ValueError("Only HTTPS URLs allowed")
        return v
```

### 7.2. Rate Limiting

```python
# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host

    # Check rate limit
    if is_rate_limited(client_ip):
        raise HTTPException(429, "Rate limit exceeded")

    response = await call_next(request)
    return response
```

### 7.3. Error Sanitization

```python
# Sanitize error responses
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    # Don't expose internal errors
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "type": "server_error"}
    )
```

## 8. Monitoring & Logging

### 8.1. Structured Logging

```python
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log automation events
@app.post("/automation")
async def run_automation(request: AutomationRequest = None):
    logger.info(f"Automation request received: {request}")

    try:
        result = await execute_automation(request)
        logger.info(f"Automation completed successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Automation failed: {e}")
        raise
```

### 8.2. Performance Monitoring

```python
# Performance metrics
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    execution_time = time.time() - start_time
    response.headers["X-Execution-Time"] = str(execution_time)

    # Log performance metrics
    logger.info(f"Request processed in {execution_time:.2f}s")

    return response
```

### 8.3. Health Monitoring

```python
# Health check with detailed status
@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "playwright-automation-server",
        "version": "1.0.0",
        "checks": {
            "database": "healthy",
            "browser": "healthy",
            "memory": "healthy"
        }
    }

    return health_status
```

## 9. Deployment Guide

### 9.1. Production Deployment

```bash
# Build Docker image
docker build -t playwright-server:latest .

# Run container
docker run -d \
  --name playwright-server \
  -p 8000:8000 \
  -e HEADLESS=true \
  -e TIMEOUT=30000 \
  playwright-server:latest

# Check health
curl http://localhost:8000/health
```

### 9.2. Environment Configuration

```env
# .env file
HEADLESS=true
TIMEOUT=30000
PORT=8000
LOG_LEVEL=INFO
RATE_LIMIT=100
```

### 9.3. Production Monitoring

```bash
# Monitor server logs
docker logs -f playwright-server

# Monitor resource usage
docker stats playwright-server

# Health check
curl http://localhost:8000/health
```

## 10. Troubleshooting

### 10.1. Common Issues

#### Server Won't Start

```bash
# Check port availability
lsof -i :8000

# Check logs
docker logs playwright-server

# Restart container
docker restart playwright-server
```

#### Browser Issues

```bash
# Check browser installation
playwright install chromium

# Check browser permissions
docker run --rm playwright-server playwright list

# Test browser manually
docker run --rm playwright-server python -c "import playwright; print('OK')"
```

#### Performance Issues

```bash
# Monitor memory usage
docker stats playwright-server

# Check concurrent requests
curl -w "@curl-format.txt" http://localhost:8000/automation

# Optimize configuration
export HEADLESS=true
export TIMEOUT=15000
```

### 10.2. Debug Mode

```python
# Enable debug mode
import os
os.environ["DEBUG"] = "true"

# Detailed logging
logging.basicConfig(level=logging.DEBUG)

# Browser debug
browser = await playwright.chromium.launch(
    headless=False,
    devtools=True
)
```

## 11. Future Enhancements

### 11.1. Planned Features

-   **Multi-site Support**: Support for multiple e-commerce sites
-   **Advanced Filtering**: Filter products by price, rating, etc.
-   **Scheduled Execution**: Periodic data extraction
-   **Webhook Integration**: Real-time notifications
-   **Dashboard**: Web UI for monitoring and configuration

### 11.2. Performance Improvements

-   **Connection Pooling**: Reuse browser instances
-   **Caching**: Cache extracted data
-   **Load Balancing**: Multiple server instances
-   **Database Integration**: Store extracted data

### 11.3. Security Enhancements

-   **Authentication**: API key authentication
-   **HTTPS**: SSL/TLS encryption
-   **Input Sanitization**: Enhanced security validation
-   **Audit Logging**: Comprehensive audit trail
