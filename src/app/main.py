import sys
import json
import time
import asyncio
import os
import platform
from typing import Dict, Any, Optional
from pathlib import Path

# Fix path for running main.py directly
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Fix Windows event loop issue
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from src.models.input import AutomationInput, ViewportConfig, ActionConfig, ExtractConfig
from src.models.output import AutomationOutput, ErrorResponse, create_success_response, create_error_response
from src.core.automation import PlaywrightAutomation
from src.core.extractor import DataExtractor
from src.core.actions import ActionExecutor
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_default_config() -> AutomationInput:
    """Get hardcoded automation configuration."""
    config = AutomationInput(
        url="https://www.amazon.com/",
        headless=False,
        timeout=300000,
        viewport=ViewportConfig(width=1280, height=720),
        wait_for_selector="body",
        actions=[
            ActionConfig(
                type="wait",
                selector="body",
                timeout=300000
            ),
            ActionConfig(
                type="click",
                selector="body > div > div.a-row.a-spacing-double-large > div.a-section > div > div > form > div > div > span > span > button",
                timeout=10000
            ),
            ActionConfig(
                type="wait",
                selector="body",
                timeout=20000
            ),
            ActionConfig(
                type="click",
                selector="#twotabsearchtextbox",
                timeout=20000
            ),
            ActionConfig(
                type="fill",
                selector="#twotabsearchtextbox",
                value="t-shirt",
                timeout=10000
            ),
            ActionConfig(
                type="click",
                selector="#nav-search-submit-button",
                timeout=10000
            ),
            ActionConfig(
                type="wait",
                selector="body",
                timeout=20000
            ),
            # Add extraction actions
            ActionConfig(
                type="get_text",
                selector="h1.a-size-base.s-desktop-toolbar",
                timeout=10000
            )
        ],
        extract=[
            ExtractConfig(
                name="search_results",
                selector="[data-component-type='s-search-result'] h2 a span",
                multiple=True
            ),
            ExtractConfig(
                name="search_results_links",
                selector="[data-component-type='s-search-result'] h2 a",
                attribute="href",
                multiple=True
            ),
            ExtractConfig(
                name="search_count",
                selector="span.a-size-base.a-color-base",
                multiple=False
            )
        ]
    )
    logger.info(f"[DEBUG] Default config URL: {config.url}, type: {type(config.url)}")
    return config


def output_json(response: Dict[str, Any]) -> None:
    """Output JSON response to stdout."""
    print(json.dumps(response, indent=2, separators=(',', ':'), default=str), flush=True)


async def run_automation(automation_input: AutomationInput) -> Dict[str, Any]:
    """Run the automation workflow."""
    start_time = time.time()
    automation = None
    
    try:
        # Initialize automation engine
        automation = PlaywrightAutomation(
            headless=automation_input.headless,
            timeout=automation_input.timeout,
            viewport=automation_input.viewport
        )
        
        # Launch browser and navigate to URL
        debug_mode = False 
        
        if debug_mode:
            print(f"[DEBUG] Launching browser (headless={automation_input.headless})", file=sys.stderr)
        
        await automation.launch()
        
        url_str = str(automation_input.url)
        logger.info(f"Navigating to {url_str}")
        logger.info(f"[DEBUG] URL type: {type(url_str)}, value: {repr(url_str)}")
        await automation.navigate(url_str)
        
        logger.info(f"Successfully navigated to {automation_input.url}")
        page_title = await automation.page.title()
        logger.info(f"Page title: {page_title}")
        
        # Wait for initial selector if specified
        if automation_input.wait_for_selector:
            await automation.wait_for_selector(automation_input.wait_for_selector)
        
        # Execute actions
        action_executor = None
        if automation_input.actions:
            action_executor = ActionExecutor(automation.page)
            for i, action in enumerate(automation_input.actions):
                logger.info(f"Executing action {i+1}/{len(automation_input.actions)}: {action.type}")
                await action_executor.execute(action)
        
        # Extract data
        extracted_data = {}
        
        # Get data from action executor (from get_* actions)
        if action_executor:
            action_data = action_executor.get_extracted_data()
            extracted_data.update(action_data)
        
        # Get data from extract configuration
        if automation_input.extract:
            data_extractor = DataExtractor(automation.page)
            for extract_item in automation_input.extract:
                logger.info(f"Extracting data: {extract_item.name}")
                result = await data_extractor.extract(extract_item)
                extracted_data[extract_item.name] = result
        
        # Xử lý đóng browser dựa trên cấu hình
        if debug_mode:
            print(f"[DEBUG] Extracted data: {extracted_data}", file=sys.stderr)
            
        # Cấu hình có đóng browser tự động hay không
        AUTO_CLOSE_BROWSER = False  # Đặt False để browser không tự động đóng
        
        if AUTO_CLOSE_BROWSER:
            if debug_mode:
                print(f"[DEBUG] Browser will stay open. Press Enter to close...", file=sys.stderr)
                input("Press Enter to close browser...")
            # Close browser properly
            await automation.close()
        else:
            if debug_mode:
                print(f"[DEBUG] Browser will stay open indefinitely. Close manually when done.", file=sys.stderr)
                print(f"[DEBUG] Script will exit but browser will remain open.", file=sys.stderr)
                print(f"[DEBUG] Press Ctrl+C to exit script while keeping browser open.", file=sys.stderr)
            else:
                print(f"Browser will stay open. Press Ctrl+C to exit script.", file=sys.stderr)
                
            # Giữ script chạy để browser không bị đóng
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print(f"Script interrupted. Browser will remain open.", file=sys.stderr)
                # Detach browser process để tránh cleanup lỗi
                await automation.detach()
                return {"success": True, "data": extracted_data, "message": "Browser kept open"}
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Create success response
        response = {
            "success": True,
            "data": extracted_data,
            "execution_time": execution_time,
            "page_title": page_title,
            "final_url": automation.page.url
        }
        
        # Keep automation instance for potential future use
        return response, automation
        
    except Exception as e:
        logger.error(f"Automation failed: {e}")
        
        # Ensure browser is closed on error
        if automation:
            try:
                await automation.close()
            except Exception as close_error:
                logger.error(f"Failed to close browser: {close_error}")
        
        # Create error response
        error_type = "automation"
        error_str = str(e)
        
        if "timeout" in error_str.lower():
            error_type = "timeout"
        elif "element not found" in error_str.lower():
            error_type = "element_not_found"
        elif "navigation" in error_str.lower() or "navigate" in error_str.lower():
            error_type = "navigation"
        elif "network" in error_str.lower():
            error_type = "network"
        elif "connection" in error_str.lower():
            error_type = "connection"
        
        response = {
            "success": False,
            "error": error_str,
            "error_type": error_type,
            "execution_time": time.time() - start_time
        }
        
        return response, None


def main() -> None:
    """Main CLI entry point."""
    try:
        print("Starting automation with hardcoded configuration...", file=sys.stderr)
        
        # Get hardcoded configuration
        automation_input = get_default_config()
        
        print(f"Target URL: {automation_input.url}", file=sys.stderr)
        print(f"Headless mode: {automation_input.headless}", file=sys.stderr)
        
        # Run automation
        try:
            response, automation = asyncio.run(run_automation(automation_input))
            output_json(response)
            
            # Exit with appropriate code
            if response.get("success"):
                print("Automation completed successfully!", file=sys.stderr)
                sys.exit(0)
            else:
                print("Automation failed!", file=sys.stderr)
                sys.exit(1)
                
        except Exception as e:
            error_response = create_error_response(
                error=f"Automation failed: {e}",
                error_type="system"
            )
            output_json(error_response.model_dump())
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("Automation interrupted by user", file=sys.stderr)
        error_response = create_error_response(
            error="Automation interrupted by user",
            error_type="interrupted"
        )
        output_json(error_response.model_dump())
        # Exit gracefully to avoid cleanup errors
        try:
            # Give a moment for any pending operations to complete
            import time
            time.sleep(0.1)
        except:
            pass
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        error_response = create_error_response(
            error=f"Unexpected error: {e}",
            error_type="system"
        )
        output_json(error_response.model_dump())
        sys.exit(1)


if __name__ == "__main__":
    main() 