# Playwright Server for n8n Integration

A FastAPI server using Playwright to provide web automation capabilities for n8n workflows. Features stealth mode browser automation with default Amazon product search configuration.

## Overview

This server provides HTTP endpoints for n8n workflows to perform web automation and data extraction. It includes a default configuration for Amazon product search and supports custom automation workflows.

## Features

-   **🔄 n8n Integration**: HTTP endpoints for seamless n8n workflow integration
-   **🛒 Default Amazon Search**: Pre-configured product search automation
-   **🥷 Stealth Mode**: Advanced anti-detection to bypass website security
-   **📊 Data Extraction**: 8 comprehensive extraction action types
-   **🤖 Human-like Behavior**: Realistic typing speeds, mouse movements, and delays
-   **🛡️ Error Resilience**: Continues automation even if some actions fail
-   **⚡ FastAPI**: Modern async API framework with auto-documentation
-   **🐳 Docker Support**: Container deployment ready

## Requirements

-   Python 3.11+
-   Playwright with Chromium browser
-   FastAPI and dependencies

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd playwright

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Start Server

```bash
# Run FastAPI server
python src/app/server_playwright.py

# Server will start on http://localhost:5765
# API docs available at http://localhost:5765/docs
```

### 3. Test with curl

```bash
# Test health endpoint
curl http://localhost:5765/health

# Run automation with default config (Amazon search)
curl -X POST http://localhost:5765/automation

# Test with custom URL
curl -X POST http://localhost:5765/automation \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/"}'
```

## n8n Integration

### HTTP Request Node Configuration

```json
{
    "method": "POST",
    "url": "http://localhost:5765/automation",
    "headers": { "Content-Type": "application/json" },
    "body": {
        "url": "https://www.amazon.com/",
        "headless": false,
        "actions": [{ "type": "get_all_text", "selector": "h1", "extract_name": "page_titles" }]
    }
}
```

### Sample n8n Workflow

Import the provided workflow:

```bash
# Use the example workflow
examples/n8n_workflow.json
```

The workflow includes:

1. HTTP Request to Playwright server
2. Data processing and formatting
3. Notion database integration
4. Telegram notification

## API Endpoints

### POST `/automation`

Main automation endpoint with validation - actions are required.

**Request Body:**

```json
{
    "url": "https://www.amazon.com/",
    "headless": false,
    "timeout": 300000,
    "viewport": { "width": 1280, "height": 720 },
    "wait_for_selector": "body",
    "actions": [
        { "type": "wait", "selector": "body", "timeout": 10000 },
        { "type": "click", "selector": "#twotabsearchtextbox", "timeout": 20000 },
        { "type": "fill", "selector": "#twotabsearchtextbox", "value": "t-shirt", "timeout": 10000 },
        { "type": "click", "selector": "#nav-search-submit-button", "timeout": 10000 },
        { "type": "wait", "selector": "body", "timeout": 20000 },
        { "type": "get_text", "selector": "h1.a-size-base.s-desktop-toolbar", "timeout": 10000 }
    ],
    "extract": [
        { "name": "search_results", "selector": "[data-component-type='s-search-result'] h2 a span", "multiple": true },
        {
            "name": "search_results_links",
            "selector": "[data-component-type='s-search-result'] h2 a",
            "attribute": "href",
            "multiple": true
        },
        { "name": "search_count", "selector": "span.a-size-base.a-color-base", "multiple": false }
    ]
}
```

**Response:**

```json
{
    "success": true,
    "session_id": "uuid-string",
    "automation_result": {
        "success": true,
        "data": {
            "search_results": ["Product 1", "Product 2"],
            "search_results_links": ["https://amazon.com/dp/...", "..."],
            "#twotabsearchtextbox": "search text content"
        },
        "execution_time": 15.3,
        "page_title": "Amazon.com: t-shirt",
        "final_url": "https://www.amazon.com/s?k=t-shirt"
    },
    "headless": false,
    "message": "Browser session created: uuid-string"
}
```


## Default Configuration

The server uses a default Amazon product search configuration:

```python
{
    "url": "https://www.amazon.com/",
    "actions": [
        # Search for "laptop"
        {"type": "click", "selector": "#twotabsearchtextbox"},
        {"type": "fill", "selector": "#twotabsearchtextbox", "value": "laptop"},
        {"type": "click", "selector": "#nav-search-submit-button"},
        {"type": "wait", "selector": "[data-component-type='s-search-result']"},

        # Extract product data
        {"type": "get_all_text", "selector": "h2 a span", "extract_name": "product_titles"},
        {"type": "get_all_text", "selector": ".a-price-whole", "extract_name": "product_prices"},
        {"type": "get_all_attributes", "selector": "h2 a", "attribute": "href", "extract_name": "product_links"},
        {"type": "get_all_attributes", "selector": "img", "attribute": "src", "extract_name": "product_images"}
    ]
}
```

## Testing

### Using curl Examples

```bash
# Run comprehensive tests
bash examples/curl_examples.sh

# Individual tests
bash examples/curl_examples.sh test_health
bash examples/curl_examples.sh test_automation
bash examples/curl_examples.sh test_validation_error
```

### Using Python Test Script

```bash
python examples/server_test.py
```

## Docker Deployment

### Build and Run

```bash
# Build Docker image
docker build -f docker/Dockerfile -t playwright-server .

# Run container
docker run -p 5765:5765 playwright-server

# Or use docker-compose
docker-compose -f docker/docker-compose.yml up
```

### Environment Variables

```env
HEADLESS=true
TIMEOUT=30000
PORT=5765
LOG_LEVEL=INFO
```

## Development

### Project Structure

```
playwright/
├── src/                          # Source code
│   ├── app/
│   │   ├── server_playwright.py  # FastAPI server_playwright for n8n
│   │   └── main.py               # CLI tool (legacy)
│   ├── core/                     # Core business logic
│   │   ├── automation.py         # Stealth mode Playwright engine
│   │   ├── actions.py            # Action executor with data extraction
│   │   └── extractor.py          # Data extraction utilities
│   ├── models/                   # Data models
│   │   ├── input.py              # Request/Action validation
│   │   └── output.py             # Response format models
│   └── utils/                    # Utilities
├── tests/                        # Test suite
├── docker/                       # Docker configurations
├── docs/                         # Documentation
└── examples/                     # Usage examples
    ├── n8n_workflow.json         # Sample n8n workflow
    ├── curl_examples.sh          # API testing script
    └── server_test.py            # Python testing script
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black src/

# Linting
flake8 src/

# Type checking
mypy src/
```

## Performance

### Benchmarks

-   **Server Startup**: ~2-3 seconds
-   **Amazon Search**: ~15-30 seconds
-   **Data Extraction**: 10-20 products per request
-   **Memory Usage**: ~200-300MB
-   **Success Rate**: 85-90%

### Optimization

```python
# Async request handling
# Stealth mode browser
# Error resilience
# Resource cleanup
```

## Security Features

### Stealth Mode

-   **Browser Arguments**: 25+ anti-detection flags
-   **JavaScript Injection**: Hides webdriver properties
-   **User Agent Spoofing**: Latest Chrome simulation
-   **HTTP Headers**: Natural request patterns

### Input Validation

-   **Pydantic Models**: Request/response validation
-   **Action Validation**: Type and parameter checking
-   **URL Validation**: Security restrictions
-   **Timeout Limits**: Resource protection

## Production Deployment

### Server Configuration

```python
# production.py
import uvicorn
from src.app.server_playwright import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5765,
    )
```

### Monitoring

```bash
# Performance metrics
curl -w "@curl-format.txt" http://localhost:5765/automation

# Logs
tail -f server.log
```

## Troubleshooting

### Common Issues

**Server Won't Start**

```bash
# Check port availability
lsof -i :5765

# Check dependencies
pip list | grep fastapi
```

**Actions Validation Error**

```bash
# Ensure actions are provided
{
  "actions": [
    {"type": "get_text", "selector": "h1", "extract_name": "title"}
  ]
}
```

**Browser Issues**

```bash
# Reinstall browsers
playwright install chromium

# Check system resources
free -h
```

**Amazon Detection**

```bash
# Already implemented stealth mode
# Check selectors if extraction fails
```

## n8n Workflow Examples

### Basic Data Extraction

1. **HTTP Request Node**: Call automation endpoint
2. **Set Node**: Process extracted data
3. **Function Node**: Transform data format

### E-commerce Monitoring

1. **Schedule Trigger**: Run daily
2. **HTTP Request**: Extract product data
3. **Compare Node**: Check price changes
4. **Email Node**: Send notifications

### Multi-site Scraping

1. **Webhook Trigger**: Receive site list
2. **Split Node**: Process each site
3. **HTTP Request**: Extract data
4. **Merge Node**: Combine results

## API Documentation

Full API documentation available at:

-   **Swagger UI**: http://localhost:5765/docs
-   **ReDoc**: http://localhost:5765/redoc

## Support

For issues and questions:

1. Check API documentation
2. Review example workflows
3. Test with curl examples
4. Open GitHub issue

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## Changelog

### v1.0.0

-   FastAPI server implementation
-   n8n integration endpoints
-   Amazon default configuration
-   8 data extraction action types
-   Stealth mode browser automation
-   Docker deployment support
