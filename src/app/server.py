import asyncio
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

from src.models.input import AutomationInput
from src.models.output import create_success_response, create_error_response
from src.core.automation import PlaywrightAutomation
from src.core.actions import ActionExecutor
from src.core.extractor import DataExtractor


app = FastAPI(
    title="Playwright Automation Server",
    description="Server for n8n integration with Playwright automation and data extraction",
    version="1.0.0"
)


class AutomationRequest(BaseModel):
    """Request model for automation - requires actions from n8n."""
    
    url: Optional[str] = Field(
        default="https://www.amazon.com/",
        description="Target URL (default: Amazon)"
    )
    actions: list = Field(
        description="Actions to perform (REQUIRED - must provide actions)",
        default=[]
    )
    extract_data: Optional[bool] = Field(
        default=True,
        description="Whether to extract data from the page"
    )
    
    @validator("actions")
    def validate_actions(cls, v):
        """Validate that actions are provided and not empty."""
        if not v or len(v) == 0:
            raise ValueError("Actions are required! Please provide at least one action.")
        return v


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


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Playwright Automation Server for n8n",
        "version": "1.0.0",
        "endpoints": {
            "automation": "/automation (requires actions)",
            "automation_default": "/automation/default (uses default actions)",
            "automation_custom": "/automation/custom (full configuration)",
            "health": "/health",
            "config": "/config/default"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "playwright-automation-server"
    }


@app.post("/automation")
async def run_automation(request: AutomationRequest):
    """
    Main automation endpoint for n8n integration.
    
    - REQUIRES actions in request body
    - Returns extracted data from the automation process
    - Uses default URL if not provided
    """
    start_time = time.time()
    
    try:
        # Create automation configuration from request
        automation_config = AutomationInput(
            url=request.url or "https://www.amazon.com/",
            headless=False,
            timeout=300000,
            viewport={"width": 1280, "height": 720},
            actions=request.actions,  # Use actions from request (required)
            extract=[]
        )
        
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
        # Ensure browser is closed on error
        try:
            await automation.close()
        except:
            pass
        
        # Create error response
        error_type = "automation"
        error_str = str(e)
        
        if "timeout" in error_str.lower():
            error_type = "timeout"
        elif "element not found" in error_str.lower():
            error_type = "element_not_found"
        elif "navigation" in error_str.lower():
            error_type = "navigation"
        
        response = create_error_response(
            error=error_str,
            error_type=error_type
        )
        
        raise HTTPException(
            status_code=500,
            detail=response.model_dump()
        )


@app.post("/automation/default")
async def run_default_automation():
    """
    Default automation endpoint - uses predefined Amazon configuration.
    
    - No request body required
    - Uses default Amazon product search actions
    - Returns extracted product data
    """
    start_time = time.time()
    
    try:
        # Get default configuration
        automation_config = get_default_config()
        
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
        # Ensure browser is closed on error
        try:
            await automation.close()
        except:
            pass
        
        # Create error response
        error_type = "automation"
        error_str = str(e)
        
        if "timeout" in error_str.lower():
            error_type = "timeout"
        elif "element not found" in error_str.lower():
            error_type = "element_not_found"
        elif "navigation" in error_str.lower():
            error_type = "navigation"
        
        response = create_error_response(
            error=error_str,
            error_type=error_type
        )
        
        raise HTTPException(
            status_code=500,
            detail=response.model_dump()
        )


@app.post("/automation/custom")
async def run_custom_automation(automation_input: AutomationInput):
    """
    Custom automation endpoint with full configuration.
    
    - Accepts full AutomationInput configuration
    - Returns extracted data from the automation process
    """
    start_time = time.time()
    
    try:
        # Run automation with custom configuration
        automation = PlaywrightAutomation(
            headless=automation_input.headless,
            timeout=automation_input.timeout,
            viewport=automation_input.viewport
        )
        
        await automation.launch()
        await automation.navigate(str(automation_input.url))
        
        # Execute actions
        action_executor = ActionExecutor(automation.page)
        for action in automation_input.actions:
            await action_executor.execute(action)
        
        # Get extracted data
        extracted_data = action_executor.get_extracted_data()
        
        # Extract data from configuration
        if automation_input.extract:
            data_extractor = DataExtractor(automation.page)
            for extract_item in automation_input.extract:
                result = await data_extractor.extract(extract_item)
                extracted_data[extract_item.name] = result
        
        # Add metadata
        extracted_data["page_url"] = str(automation_input.url)
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
        # Ensure browser is closed on error
        try:
            await automation.close()
        except:
            pass
        
        # Create error response
        error_type = "automation"
        error_str = str(e)
        
        if "timeout" in error_str.lower():
            error_type = "timeout"
        elif "element not found" in error_str.lower():
            error_type = "element_not_found"
        elif "navigation" in error_str.lower():
            error_type = "navigation"
        
        response = create_error_response(
            error=error_str,
            error_type=error_type
        )
        
        raise HTTPException(
            status_code=500,
            detail=response.model_dump()
        )


@app.get("/config/default")
async def get_default_configuration():
    """Get default automation configuration."""
    config = get_default_config()
    return config.model_dump()


if __name__ == "__main__":
    uvicorn.run(
        "src.app.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 