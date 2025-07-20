# Test Driven Development (TDD) - Playwright Server for n8n Integration

## 1. Tổng quan

Xây dựng Playwright server để:

-   **n8n Integration**: Nhận HTTP requests từ n8n workflows
-   **Modular Architecture**: Code tách biệt thành modules có thể test riêng
-   **Session Management**: Browser session management với stateful architecture
-   **Default Configuration**: Sử dụng config mặc định (Amazon product search)
-   **Data Extraction**: Tự động lấy thông tin từ trang web
-   **JSON Output**: Trả về structured data cho n8n

## 1.1. Current Server Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│      n8n        │─────▶│  FastAPI Server │─────▶│   Target Site   │
│   Workflow      │ HTTP │  (Port 5765)    │      │   (Amazon)      │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                 │                         │
                                 ▼                         ▼
                         ┌─────────────────┐      ┌─────────────────┐
                         │ Browser Session │      │  Data Extraction│
                         │   Management    │      │   (Products)    │
                         └─────────────────┘      └─────────────────┘
                                 │                         │
                                 ▼                         ▼
                         ┌─────────────────┐      ┌─────────────────┐
                         │  Modular Core   │◀─────│  JSON Response  │
                         │   Components    │      │   to n8n        │
                         └─────────────────┘      └─────────────────┘
```

## 1.2. Current Project Structure

```
playwright/
├── src/                          # Source code
│   ├── __init__.py
│   ├── app/
│   │   ├── server_playwright.py  # ✅ FastAPI server với session management
│   │   └── main.py               # ✅ Core automation logic
│   ├── core/                     # ✅ Modular business logic
│   │   ├── __init__.py
│   │   ├── automation.py         # ✅ PlaywrightAutomation class
│   │   ├── actions.py            # ✅ ActionExecutor class
│   │   └── extractor.py          # ✅ DataExtractor class
│   ├── models/                   # ✅ Pydantic data models
│   │   ├── __init__.py
│   │   ├── input.py              # ✅ ViewportConfig, ActionConfig, ExtractConfig, AutomationInput
│   │   └── output.py             # ✅ AutomationOutput, ErrorResponse
│   └── utils/                    # 🔄 Utilities (future)
├── tests/                        # ⏳ Test suite (need implementation)
│   ├── __init__.py
│   ├── unit/                     # ⏳ Unit tests for modular components
│   │   ├── test_models.py        # Test Pydantic models
│   │   ├── test_automation.py    # Test PlaywrightAutomation class
│   │   ├── test_actions.py       # Test ActionExecutor class
│   │   ├── test_extractor.py     # Test DataExtractor class
│   │   └── test_server.py        # Test FastAPI endpoints
│   ├── integration/              # ⏳ Integration tests
│   │   ├── test_n8n_integration.py  # n8n workflow tests
│   │   └── test_amazon_scraping.py # Amazon scraping tests
│   └── fixtures/                 # ⏳ Test fixtures
└── examples/                     # ⏳ Usage examples
    ├── n8n_workflow.json         # Sample n8n workflow
    └── curl_examples.sh          # API testing examples
```

## 1.3. n8n Integration Setup

### 1.3.1. Server Startup

```bash
# Start the server
python src/app/server_playwright.py

# Server runs on http://localhost:5765
# API docs at http://localhost:5765/docs
```

### 1.3.2. n8n HTTP Request Node Configuration

```json
{
    "method": "POST",
    "url": "http://localhost:5765/automation",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": {
        "url": "https://www.amazon.com/",
        "headless": false,
        "actions": []
    }
}
```

## 2. User Stories & Test Cases

### 2.1. User Story: Modular Architecture Testing

**As a** developer  
**I want to** test each module independently  
**So that** I can ensure code quality và reliability

**Test Cases:**

-   TC_001: Test Pydantic models validation
-   TC_002: Test PlaywrightAutomation class functionality
-   TC_003: Test ActionExecutor class actions
-   TC_004: Test DataExtractor class extraction
-   TC_005: Test server endpoints independently

### 2.2. User Story: Browser Session Management

**As a** n8n user  
**I want to** create và manage browser sessions  
**So that** I can reuse browsers và control lifecycle

**Test Cases:**

-   TC_006: Create browser session với automation
-   TC_007: Get session information
-   TC_008: Navigate browser in session
-   TC_009: Execute JavaScript in session
-   TC_010: Take screenshots in session
-   TC_011: Close specific sessions
-   TC_012: Close all sessions

### 2.3. User Story: n8n Integration

**As a** n8n user  
**I want to** call Playwright server from n8n workflow  
**So that** I can extract product data from Amazon automatically

**Test Cases:**

-   TC_013: n8n sends HTTP POST to /browser/open endpoint
-   TC_014: Server returns JSON với session data và automation results
-   TC_015: Server handles errors gracefully
-   TC_016: n8n receives structured data for further processing

### 2.4. User Story: Data Extraction

**As a** n8n workflow  
**I want to** receive extracted product information  
**So that** I can process and store the data

**Test Cases:**

-   TC_017: Extract search results from Amazon
-   TC_018: Extract product links from search results
-   TC_019: Extract specific elements với selectors
-   TC_020: Return structured JSON response

## 3. Current API Endpoints

### 3.1. Browser Session Management

**POST** `/automation`

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

> **Lưu ý:** Các endpoint như /browser/open, /browser/info/{session_id}, /health, ... hiện chưa implement trong code. Các test case liên quan đến các endpoint này sẽ được thực hiện ở các phase tiếp theo.

## 4. Test Requirements

### 4.1. Unit Tests cho Modular Components

**Mô tả:** Test từng module riêng biệt

#### 4.1.1. Test Models (src/models/)

```python
# tests/unit/test_models.py
import pytest
from pydantic import ValidationError
from src.models.input import ViewportConfig, ActionConfig, ExtractConfig, AutomationInput
from src.models.output import AutomationOutput, ErrorResponse

class TestViewportConfig:
    def test_default_viewport(self):
        config = ViewportConfig()
        assert config.width == 1280
        assert config.height == 720

    def test_custom_viewport(self):
        config = ViewportConfig(width=1920, height=1080)
        assert config.width == 1920
        assert config.height == 1080

class TestActionConfig:
    def test_click_action(self):
        action = ActionConfig(type="click", selector="#button", timeout=5000)
        assert action.type == "click"
        assert action.selector == "#button"
        assert action.timeout == 5000

    def test_fill_action(self):
        action = ActionConfig(type="fill", selector="#input", value="test", timeout=3000)
        assert action.value == "test"

class TestAutomationInput:
    def test_required_url(self):
        with pytest.raises(ValidationError):
            AutomationInput()  # url is required

    def test_valid_input(self):
        input_data = AutomationInput(
            url="https://example.com",
            headless=True,
            timeout=30000
        )
        assert input_data.url == "https://example.com"
        assert input_data.headless == True
```

#### 4.1.2. Test Automation Engine (src/core/automation.py)

```python
# tests/unit/test_automation.py
import pytest
import asyncio
from src.core.automation import PlaywrightAutomation
from src.models.input import ViewportConfig

class TestPlaywrightAutomation:
    @pytest.mark.asyncio
    async def test_automation_launch(self):
        automation = PlaywrightAutomation(headless=True)
        await automation.launch()

        assert automation.playwright is not None
        assert automation.browser is not None
        assert automation.context is not None
        assert automation.page is not None

        await automation.close()

    @pytest.mark.asyncio
    async def test_navigation(self):
        automation = PlaywrightAutomation(headless=True)
        await automation.launch()

        await automation.navigate("https://example.com")

        assert "example.com" in automation.page.url

        await automation.close()

    @pytest.mark.asyncio
    async def test_viewport_config(self):
        viewport = ViewportConfig(width=1920, height=1080)
        automation = PlaywrightAutomation(headless=True, viewport=viewport)
        await automation.launch()

        page_viewport = await automation.page.viewport_size()
        assert page_viewport["width"] == 1920
        assert page_viewport["height"] == 1080

        await automation.close()
```

#### 4.1.3. Test Action Executor (src/core/actions.py)

```python
# tests/unit/test_actions.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.actions import ActionExecutor
from src.models.input import ActionConfig

class TestActionExecutor:
    @pytest.fixture
    def mock_page(self):
        page = AsyncMock()
        return page

    @pytest.mark.asyncio
    async def test_click_action(self, mock_page):
        executor = ActionExecutor(mock_page)
        action = ActionConfig(type="click", selector="#button", timeout=5000)

        await executor.execute(action)

        mock_page.click.assert_called_once_with("#button", timeout=5000)

    @pytest.mark.asyncio
    async def test_fill_action(self, mock_page):
        executor = ActionExecutor(mock_page)
        action = ActionConfig(type="fill", selector="#input", value="test", timeout=3000)

        await executor.execute(action)

        mock_page.fill.assert_called_once_with("#input", "test", timeout=3000)

    @pytest.mark.asyncio
    async def test_wait_action(self, mock_page):
        executor = ActionExecutor(mock_page)
        action = ActionConfig(type="wait", selector="#element", timeout=10000)

        await executor.execute(action)

        mock_page.wait_for_selector.assert_called_once_with("#element", timeout=10000)
```

#### 4.1.4. Test Data Extractor (src/core/extractor.py)

```python
# tests/unit/test_extractor.py
import pytest
from unittest.mock import AsyncMock
from src.core.extractor import DataExtractor
from src.models.input import ExtractConfig

class TestDataExtractor:
    @pytest.fixture
    def mock_page(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_single_element_extraction(self, mock_page):
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "Test Text"
        mock_page.query_selector.return_value = mock_element

        extractor = DataExtractor(mock_page)
        config = ExtractConfig(name="test", selector="h1", multiple=False)

        result = await extractor.extract(config)

        assert result == "Test Text"
        mock_page.query_selector.assert_called_once_with("h1")

    @pytest.mark.asyncio
    async def test_multiple_elements_extraction(self, mock_page):
        mock_elements = [AsyncMock(), AsyncMock()]
        mock_elements[0].text_content.return_value = "Text 1"
        mock_elements[1].text_content.return_value = "Text 2"
        mock_page.query_selector_all.return_value = mock_elements

        extractor = DataExtractor(mock_page)
        config = ExtractConfig(name="test", selector=".item", multiple=True)

        result = await extractor.extract(config)

        assert result == ["Text 1", "Text 2"]
        mock_page.query_selector_all.assert_called_once_with(".item")

    @pytest.mark.asyncio
    async def test_attribute_extraction(self, mock_page):
        mock_element = AsyncMock()
        mock_element.get_attribute.return_value = "https://example.com"
        mock_page.query_selector.return_value = mock_element

        extractor = DataExtractor(mock_page)
        config = ExtractConfig(name="test", selector="a", attribute="href", multiple=False)

        result = await extractor.extract(config)

        assert result == "https://example.com"
        mock_element.get_attribute.assert_called_once_with("href")
```

### 4.2. Integration Tests

**Mô tả:** Test tích hợp giữa các components

#### 4.2.1. Server Integration Tests

```python
# tests/integration/test_server.py
import pytest
from fastapi.testclient import TestClient
from src.app.server_playwright import app

class TestServerIntegration:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_browser_open_endpoint(self, client):
        response = client.post("/browser/open", json={
            "url": "https://example.com",
            "headless": true,
            "run_automation": false
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "session_id" in data

    def test_invalid_session_info(self, client):
        response = client.get("/browser/info/invalid-session-id")
        assert response.status_code == 404
```

#### 4.2.2. Amazon Automation Integration Tests

```python
# tests/integration/test_amazon_scraping.py
import pytest
import asyncio
from src.app.main import get_default_config, run_automation

class TestAmazonAutomation:
    @pytest.mark.asyncio
    async def test_default_config_structure(self):
        config = get_default_config()
        assert config.url == "https://www.amazon.com/"
        assert len(config.actions) > 0
        assert len(config.extract) > 0
        assert config.viewport.width == 1280
        assert config.viewport.height == 720

    @pytest.mark.asyncio
    async def test_amazon_automation_execution(self):
        config = get_default_config()
        result, automation = await run_automation(config)

        try:
            assert result["success"] == True
            assert "data" in result
            assert "execution_time" in result
            assert "page_title" in result

            # Check extracted data
            data = result["data"]
            assert "search_results" in data
            assert isinstance(data["search_results"], list)

        finally:
            if automation:
                await automation.close()

    @pytest.mark.asyncio
    async def test_automation_error_handling(self):
        config = get_default_config()
        config.url = "https://invalid-url-that-does-not-exist.com"

        result, automation = await run_automation(config)

        assert result["success"] == False
        assert "error" in result
        assert "error_type" in result
        assert automation is None
```

### 4.3. n8n Integration Tests

```python
# tests/integration/test_n8n_integration.py
import pytest
import json
from fastapi.testclient import TestClient
from src.app.server_playwright import app

class TestN8nIntegration:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_n8n_workflow_simulation(self, client):
        # Simulate n8n HTTP Request node
        n8n_request = {
            "url": "https://www.amazon.com/",
            "headless": True,
            "run_automation": True,
            "width": 1280,
            "height": 720
        }

        response = client.post("/browser/open", json=n8n_request)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] == True
        assert "session_id" in data
        assert "automation_result" in data

        automation_result = data["automation_result"]
        if automation_result["success"]:
            assert "data" in automation_result
            assert "execution_time" in automation_result
            assert "page_title" in automation_result

    def test_n8n_response_format(self, client):
        response = client.post("/browser/open", json={
            "url": "https://example.com",
            "headless": True,
            "run_automation": False
        })

        data = response.json()

        # Check n8n-compatible response format
        required_fields = ["success", "session_id", "automation_result", "message"]
        for field in required_fields:
            assert field in data

        # Check response is JSON serializable
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        assert parsed == data
```

### 4.4. Performance Tests

```python
# tests/performance/test_performance.py
import pytest
import asyncio
import time
from src.app.main import get_default_config, run_automation

class TestPerformance:
    @pytest.mark.asyncio
    async def test_automation_execution_time(self):
        """Test that automation completes within reasonable time"""
        config = get_default_config()

        start_time = time.time()
        result, automation = await run_automation(config)
        execution_time = time.time() - start_time

        try:
            # Should complete within 60 seconds
            assert execution_time < 60

            if result["success"]:
                # Check reported execution time matches actual
                reported_time = result["execution_time"]
                assert abs(reported_time - execution_time) < 2  # 2 second tolerance

        finally:
            if automation:
                await automation.close()

    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test that automation doesn't consume excessive memory"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        config = get_default_config()
        result, automation = await run_automation(config)

        try:
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = peak_memory - initial_memory

            # Should not use more than 500MB additional memory
            assert memory_increase < 500

        finally:
            if automation:
                await automation.close()
```

## 5. Acceptance Criteria

### 5.1. Modular Architecture Requirements

**AC_001:** Each module must be independently testable  
**AC_002:** Models must validate input/output correctly  
**AC_003:** Core logic must be separated from server logic  
**AC_004:** All modules must have proper error handling  
**AC_005:** Import paths must be consistent và working

### 5.2. Server Requirements

**AC_006:** Server must start on port 8000  
**AC_007:** Must respond to /browser/open endpoint  
**AC_008:** Must return JSON với session data  
**AC_009:** Must handle errors gracefully  
**AC_010:** Must provide session management endpoints

### 5.3. Browser Session Requirements

**AC_011:** Must create browser sessions với unique IDs  
**AC_012:** Must support automation trong sessions  
**AC_013:** Must provide session control endpoints  
**AC_014:** Must handle session cleanup properly  
**AC_015:** Must support concurrent sessions

### 5.4. Data Extraction Requirements

**AC_016:** Must extract data from Amazon search results  
**AC_017:** Must support multiple extraction types  
**AC_018:** Must return structured JSON response  
**AC_019:** Must handle missing elements gracefully  
**AC_020:** Must provide detailed error information

### 5.5. n8n Integration Requirements

**AC_021:** Must accept HTTP POST requests from n8n  
**AC_022:** Must return data trong n8n-compatible format  
**AC_023:** Must handle n8n timeout requirements  
**AC_024:** Must provide clear error messages  
**AC_025:** Must support workflow debugging

## 6. Test Coverage Requirements

### 6.1. Unit Tests Coverage

**Target:** 90% code coverage cho modular components

-   `src/models/`: Pydantic model validation
-   `src/core/automation.py`: PlaywrightAutomation class
-   `src/core/actions.py`: ActionExecutor class
-   `src/core/extractor.py`: DataExtractor class
-   `src/app/server_playwright.py`: FastAPI endpoints

### 6.2. Integration Tests Coverage

**Target:** Key integration scenarios

-   Server endpoints integration
-   Amazon automation workflow
-   n8n HTTP request simulation
-   Error handling scenarios
-   Session management lifecycle

### 6.3. End-to-End Tests Coverage

**Target:** Real-world usage scenarios

-   Complete n8n workflow execution
-   Amazon product data extraction
-   Multiple concurrent sessions
-   Performance benchmarks

## 7. Testing Workflow

### 7.1. Development Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v

# Coverage report
pytest --cov=src tests/ --cov-report=html
```

### 7.2. Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
    test:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v2

            - name: Set up Python
              uses: actions/setup-python@v2
              with:
                  python-version: "3.11"

            - name: Install dependencies
              run: |
                  pip install -r requirements.txt
                  playwright install chromium

            - name: Run unit tests
              run: pytest tests/unit/ -v

            - name: Run integration tests
              run: pytest tests/integration/ -v

            - name: Generate coverage report
              run: pytest --cov=src tests/ --cov-report=xml

            - name: Upload coverage
              uses: codecov/codecov-action@v1
```

## 8. Current Status & Implementation Progress

### 8.1. ✅ Completed Components

#### Modular Architecture

-   **✅ Input Models**: `src/models/input.py` - Comprehensive validation models
-   **✅ Output Models**: `src/models/output.py` - Response formatting models
-   **✅ Automation Engine**: `src/core/automation.py` - Browser management
-   **✅ Action Executor**: `src/core/actions.py` - Action execution logic
-   **✅ Data Extractor**: `src/core/extractor.py` - Data extraction utilities
-   **✅ Server Logic**: `src/app/server_playwright.py` - FastAPI endpoints
-   **✅ Main Logic**: `src/app/main.py` - Core automation workflow

#### Modern FastAPI Server

-   **✅ Lifespan Events**: Modern context manager implementation
-   **✅ Session Management**: BrowserManager với session lifecycle
-   **✅ Error Handling**: Comprehensive error handling
-   **✅ API Endpoints**: Complete browser session management API

#### Amazon Automation

-   **✅ Default Configuration**: Working Amazon t-shirt search
-   **✅ Data Extraction**: Multiple data types extracted
-   **✅ Error Resilience**: Continue on failures
-   **✅ Structured Output**: JSON format cho n8n

### 8.2. ⏳ Pending Test Implementation

#### Unit Tests (Priority: High)

-   **⏳ Model Tests**: Test Pydantic validation
-   **⏳ Automation Tests**: Test PlaywrightAutomation class
-   **⏳ Action Tests**: Test ActionExecutor functionality
-   **⏳ Extractor Tests**: Test DataExtractor functionality
-   **⏳ Server Tests**: Test FastAPI endpoints

#### Integration Tests (Priority: High)

-   **⏳ Server Integration**: End-to-end server testing
-   **⏳ Amazon Integration**: Full automation workflow testing
-   **⏳ n8n Integration**: Simulated n8n workflow testing
-   **⏳ Session Management**: Browser session lifecycle testing

#### Performance Tests (Priority: Medium)

-   **⏳ Execution Time**: Automation performance benchmarks
-   **⏳ Memory Usage**: Resource consumption testing
-   **⏳ Concurrent Sessions**: Multiple session handling
-   **⏳ Load Testing**: Server load capacity testing

### 8.3. Test Infrastructure Needs

#### Test Setup

-   **⏳ Pytest Configuration**: Setup pytest với async support
-   **⏳ Mock Framework**: Configure mocking cho browser testing
-   **⏳ Test Fixtures**: Create reusable test data
-   **⏳ Coverage Tools**: Setup coverage reporting

#### CI/CD Integration

-   **⏳ GitHub Actions**: Automated testing on commits
-   **⏳ Coverage Reports**: Code coverage tracking
-   **⏳ Performance Monitoring**: Track performance regressions
-   **⏳ Quality Gates**: Enforce quality standards

## 9. Quality Assurance Strategy

### 9.1. Testing Principles

#### Test Pyramid

-   **Unit Tests (70%)**: Fast, isolated tests cho individual components
-   **Integration Tests (20%)**: Test component interactions
-   **End-to-End Tests (10%)**: Full workflow validation

#### Test Characteristics

-   **Fast**: Unit tests should run in milliseconds
-   **Reliable**: Tests should be deterministic
-   **Isolated**: Tests should not depend on external services
-   **Maintainable**: Tests should be easy to understand và update

### 9.2. Mock Strategy

#### Browser Mocking

-   **Unit Tests**: Mock Playwright components
-   **Integration Tests**: Use real browsers with controlled environments
-   **Performance Tests**: Measure actual browser performance

#### External Service Mocking

-   **Amazon**: Mock responses for reliable testing
-   **n8n**: Simulate n8n HTTP requests
-   **Network**: Mock network failures và timeouts

### 9.3. Test Data Management

#### Fixtures

-   **Valid Inputs**: Complete valid automation configurations
-   **Edge Cases**: Boundary conditions và error scenarios
-   **Real Data**: Captured Amazon responses cho validation

#### Test Environments

-   **Local**: Developer testing với real browsers
-   **CI**: Headless testing trong containers
-   **Staging**: Full integration testing

## 10. Implementation Roadmap

### Phase 1: Unit Test Foundation (Week 1)

1. **Setup Test Infrastructure**: Pytest, fixtures, mocking
2. **Model Tests**: Validate Pydantic models
3. **Core Logic Tests**: Test automation, actions, extractor
4. **Coverage Setup**: Achieve 90% unit test coverage

### Phase 2: Integration Testing (Week 2)

1. **Server Integration**: Test FastAPI endpoints
2. **Amazon Integration**: Test full automation workflow
3. **Session Management**: Test browser session lifecycle
4. **Error Handling**: Validate error scenarios

### Phase 3: n8n Integration Testing (Week 3)

1. **n8n Simulation**: Test n8n HTTP request scenarios
2. **Response Validation**: Ensure n8n-compatible responses
3. **Workflow Testing**: Complete end-to-end testing
4. **Performance Validation**: Ensure acceptable performance

### Phase 4: Production Readiness (Week 4)

1. **Load Testing**: Test concurrent session handling
2. **Performance Benchmarks**: Establish performance baselines
3. **CI/CD Integration**: Automated testing pipeline
4. **Documentation**: Complete test documentation

## 11. Success Metrics

### 11.1. Code Quality Metrics

-   **Test Coverage**: > 90% for unit tests
-   **Integration Coverage**: > 80% for integration tests
-   **Code Quality**: All tests passing, no critical issues
-   **Performance**: < 30 seconds automation execution

### 11.2. Reliability Metrics

-   **Test Reliability**: > 95% test pass rate
-   **Automation Success**: > 90% Amazon automation success
-   **Error Handling**: All error scenarios covered
-   **Session Management**: Reliable session lifecycle

### 11.3. Developer Experience

-   **Test Speed**: Unit tests < 5 seconds total
-   **Feedback Loop**: Fast test feedback cho developers
-   **Documentation**: Clear testing guidelines
-   **Debugging**: Easy test failure diagnosis

**Current Status**: Solid foundation established, ready for comprehensive test implementation!
