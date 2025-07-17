"""
Quick test of data extraction actions.
"""

import asyncio
from src.models.input import AutomationInput
from src.core.automation import PlaywrightAutomation
from src.core.actions import ActionExecutor


async def test_extraction():
    """Test extraction actions on example.com"""
    
    config = AutomationInput(
        url="https://example.com",
        headless=False,
        timeout=30000,
        actions=[
            # Extract page title
            {
                "type": "get_text",
                "selector": "h1",
                "extract_name": "page_title"
            },
            # Extract all links
            {
                "type": "get_all_attributes",
                "selector": "a",
                "attribute": "href",
                "extract_name": "all_links"
            },
            # Extract all paragraphs
            {
                "type": "get_all_text",
                "selector": "p",
                "extract_name": "all_paragraphs"
            }
        ]
    )
    
    automation = PlaywrightAutomation()
    
    try:
        await automation.setup()
        await automation.navigate(str(config.url))
        
        action_executor = ActionExecutor(automation.page)
        
        for action in config.actions:
            print(f"Executing: {action.type} -> {action.extract_name}")
            await action_executor.execute(action)
        
        # Get extracted data
        extracted_data = action_executor.get_extracted_data()
        
        print("\nExtracted Data:")
        for key, value in extracted_data.items():
            print(f"{key}: {value}")
        
        # Keep browser open
        print("\nPress Enter to close browser...")
        input()
        
        await automation.detach()
        
    except Exception as e:
        print(f"Error: {e}")
        await automation.detach()


if __name__ == "__main__":
    asyncio.run(test_extraction()) 