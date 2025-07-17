import sys
import json
import time
import asyncio
from typing import Dict, Any, Optional

from pydantic import ValidationError

from src.models.input import AutomationInput
from src.models.output import AutomationOutput, ErrorResponse, create_success_response, create_error_response
from src.core.automation import PlaywrightAutomation
from src.core.extractor import DataExtractor
from src.core.actions import ActionExecutor


def get_hardcoded_config() -> AutomationInput:
    """Get hardcoded automation configuration."""
    return AutomationInput(
        url="https://www.amazon.com/",
        headless=False,
        timeout=300000,
        viewport={"width": 1280, "height": 720},
        wait_for_selector="body",  # Chờ body load trước
        actions=[
            {
                "type": "wait",
                "selector": "body",
                "timeout": 300000
            },
            {
                "type": "click",
                "selector": "body > div > div.a-row.a-spacing-double-large > div.a-section > div > div > form > div > div > span > span > button",
                "timeout": 10000
            },
            {
                "type": "wait",
                "selector": "body",
                "timeout": 20000
            },
            {
                "type": "click",
                "selector": "#twotabsearchtextbox",
                "timeout": 20000
            },
            {
                "type": "fill",
                "selector": "#twotabsearchtextbox",
                "value": "t-shirt",
                "timeout": 10000
            },
            {
                "type": "click",
                "selector": "#nav-search-submit-button",
                "timeout": 10000
            },
            {
                "type": "wait",
                "selector": "body",
                "timeout": 20000
            },
            {
                "type": "fill",
                "selector": "#\39 baf2e7f-b6fb-4e8d-8210-f7f3628e8070 > div > div > span > div > div > div.a-section.a-spacing-small.puis-padding-left-small.puis-padding-right-small > div.a-section.a-spacing-none.a-spacing-top-small.s-title-instructions-style > a > h2 > span",
                "timeout": 10000
            },
            # {
            #     "type": "click",
            #     "selector": "#passwordNext > div > button > span",
            #     "timeout": 30000
            # },
            # {
            #     "type": "wait",
            #     "selector": "body",
            #     "timeout": 10000
            # },
            # # {
            # #     "type": "click",
            # #     "selector": "#yDmH0d > c-wiz > div > div.JYXaTc.lUWEgd > div > div.FO2vFd > div > div > button > span",
            # #     "timeout": 10000
            # # },
            # # {
            # #     "type": "wait",
            # #     "selector": "body",
            # #     "timeout": 5000
            # # },
            # # {
            # #     "type": "click",
            # #     "selector": "#yDmH0d > c-wiz.SSPGKf.JHVYhd > div > div > div > div > div.MFXio > button.VfPpkd-LgbsSe.ksBjEc.lKxP2d.LQeN7.MXew1e.lJTaZd > span",
            # #     "timeout": 10000
            # # },
            # # {
            # #     "type": "wait",
            # #     "selector": "body", 
            # #     "timeout": 3000
            # # },
            # # {
            # #     "type": "click",
            # #     "selector": "#yDmH0d > c-wiz:nth-child(10) > div > div > div > div > div > div.MFXio > button.VfPpkd-LgbsSe.ksBjEc.lKxP2d.LQeN7.MXew1e.lJTaZd > span",
            # #     "timeout": 10000
            # # },
            # # {
            # #     "type": "wait",
            # #     "selector": "body",
            # #     "timeout": 5000
            # # },
            # {
            #     "type": "click",
            #     "selector": "#yDmH0d > c-wiz > div > div.eEJIWe > div.UdVxgf > div > div.dWOKZe > div.sZjBXe > div > div.tB5Jxf-xl07Ob-XxIAqe-OWXEXe-oYxtQd > div:nth-child(1) > div > button",
            #     "timeout": 10000
            # }
        ],
        extract=[]
    )


def output_json(response: Dict[str, Any]) -> None:
    """Output JSON response to stdout."""
    print(json.dumps(response, indent=2, separators=(',', ':'), default=str), flush=True)


async def run_automation(automation_input: AutomationInput) -> Dict[str, Any]:
    """Run the automation workflow."""
    start_time = time.time()
    
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
        
        if debug_mode:
            print(f"[DEBUG] Browser launched successfully", file=sys.stderr)
            print(f"[DEBUG] Navigating to {automation_input.url}", file=sys.stderr)
        
        await automation.navigate(str(automation_input.url))
        
        if debug_mode:
            print(f"[DEBUG] Successfully navigated to {automation_input.url}", file=sys.stderr)
            page_title = await automation.page.title()
            print(f"[DEBUG] Page title: {page_title}", file=sys.stderr)
        
        # Wait for initial selector if specified
        if automation_input.wait_for_selector:
            await automation.wait_for_selector(automation_input.wait_for_selector)
        
        # Execute actions
        action_executor = None
        if automation_input.actions:
            action_executor = ActionExecutor(automation.page)
            for action in automation_input.actions:
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
        response = create_success_response(
            data=extracted_data,
            execution_time=execution_time
        )
        
        return response.model_dump()
        
    except Exception as e:
        debug_mode = True
        
        if debug_mode:
            print(f"[ERROR] Automation failed: {e}", file=sys.stderr)
        
        # Ensure browser is closed on error
        try:
            await automation.detach()
        except Exception as close_error:
            if debug_mode:
                print(f"[ERROR] Failed to detach browser: {close_error}", file=sys.stderr)
        
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
        
        response = create_error_response(
            error=error_str,
            error_type=error_type
        )
        
        return response.model_dump()


def main() -> None:
    """Main CLI entry point."""
    try:
        print("Starting automation with hardcoded configuration...", file=sys.stderr)
        
        # Get hardcoded configuration
        automation_input = get_hardcoded_config()
        
        print(f"Target URL: {automation_input.url}", file=sys.stderr)
        print(f"Headless mode: {automation_input.headless}", file=sys.stderr)
        
        # Run automation
        try:
            response = asyncio.run(run_automation(automation_input))
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