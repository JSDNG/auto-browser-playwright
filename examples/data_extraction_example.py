"""
Example demonstrating data extraction actions.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.input import AutomationInput
from src.core.automation import PlaywrightAutomation
from src.core.actions import ActionExecutor


async def demo_data_extraction():
    """Demo các action lấy thông tin từ website."""
    
    # Cấu hình automation với các action extraction
    config = AutomationInput(
        url="https://example.com",
        headless=False,
        timeout=30000,
        actions=[
            # Lấy text từ thẻ h1
            {
                "type": "get_text",
                "selector": "h1",
                "extract_name": "page_title"
            },
            
            # Lấy href từ tất cả links
            {
                "type": "get_all_attributes",
                "selector": "a",
                "attribute": "href",
                "extract_name": "all_links"
            },
            
            # Lấy src từ tất cả images
            {
                "type": "get_all_attributes",
                "selector": "img",
                "attribute": "src",
                "extract_name": "all_images"
            },
            
            # Lấy text từ tất cả paragraphs
            {
                "type": "get_all_text",
                "selector": "p",
                "extract_name": "all_paragraphs"
            },
            
            # Lấy HTML content từ main content
            {
                "type": "get_html",
                "selector": "main",
                "extract_name": "main_content"
            },
            
            # Lấy attribute class từ body
            {
                "type": "get_attribute",
                "selector": "body",
                "attribute": "class",
                "extract_name": "body_classes"
            }
        ]
    )
    
    # Chạy automation
    automation = PlaywrightAutomation()
    
    try:
        await automation.setup()
        await automation.navigate(str(config.url))
        
        # Execute actions
        action_executor = ActionExecutor(automation.page)
        
        for action in config.actions:
            print(f"Executing: {action.type} -> {action.extract_name}")
            await action_executor.execute(action)
        
        # Lấy extracted data
        extracted_data = action_executor.get_extracted_data()
        
        print("\n" + "="*50)
        print("EXTRACTED DATA:")
        print("="*50)
        
        for key, value in extracted_data.items():
            print(f"\n{key}:")
            if isinstance(value, list):
                for i, item in enumerate(value):
                    print(f"  [{i}] {item}")
            else:
                print(f"  {value}")
        
        # Giữ browser mở
        print("\n" + "="*50)
        print("Browser will stay open. Press Ctrl+C to exit.")
        print("="*50)
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            await automation.detach()
            
    except Exception as e:
        print(f"Error: {e}")
        await automation.detach()


async def demo_google_search_extraction():
    """Demo lấy thông tin từ Google search results."""
    
    config = AutomationInput(
        url="https://www.google.com",
        headless=False,
        timeout=30000,
        actions=[
            # Search for something
            {
                "type": "fill",
                "selector": "input[name='q']",
                "value": "Python programming"
            },
            {
                "type": "press",
                "selector": "input[name='q']",
                "value": "Enter"
            },
            {
                "type": "wait",
                "selector": "#search"
            },
            
            # Extract search results
            {
                "type": "get_all_text",
                "selector": "h3",
                "extract_name": "search_titles"
            },
            {
                "type": "get_all_attributes",
                "selector": "a[href*='/url?q=']",
                "attribute": "href",
                "extract_name": "search_links"
            },
            {
                "type": "get_all_text",
                "selector": ".VwiC3b",
                "extract_name": "search_descriptions"
            }
        ]
    )
    
    automation = PlaywrightAutomation()
    
    try:
        await automation.setup()
        await automation.navigate(str(config.url))
        
        action_executor = ActionExecutor(automation.page)
        
        for action in config.actions:
            print(f"Executing: {action.type}")
            await action_executor.execute(action)
        
        extracted_data = action_executor.get_extracted_data()
        
        print("\n" + "="*50)
        print("GOOGLE SEARCH RESULTS:")
        print("="*50)
        
        titles = extracted_data.get("search_titles", [])
        descriptions = extracted_data.get("search_descriptions", [])
        
        for i, title in enumerate(titles[:10]):  # Show first 10 results
            print(f"\n[{i+1}] {title}")
            if i < len(descriptions):
                print(f"    {descriptions[i]}")
        
        print(f"\nTotal results found: {len(titles)}")
        
        # Keep browser open
        print("\nBrowser will stay open. Press Ctrl+C to exit.")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            await automation.detach()
            
    except Exception as e:
        print(f"Error: {e}")
        await automation.detach()


async def demo_ecommerce_extraction():
    """Demo lấy thông tin sản phẩm từ e-commerce website."""
    
    config = AutomationInput(
        url="https://example-shop.com",
        headless=False,
        timeout=30000,
        actions=[
            # Extract product information
            {
                "type": "get_text",
                "selector": ".product-title",
                "extract_name": "product_title"
            },
            {
                "type": "get_text",
                "selector": ".price",
                "extract_name": "product_price"
            },
            {
                "type": "get_src",
                "selector": ".product-image img",
                "extract_name": "product_image"
            },
            {
                "type": "get_text",
                "selector": ".product-description",
                "extract_name": "product_description"
            },
            {
                "type": "get_all_text",
                "selector": ".review-text",
                "extract_name": "customer_reviews"
            },
            {
                "type": "get_all_attributes",
                "selector": ".related-product a",
                "attribute": "href",
                "extract_name": "related_products"
            }
        ]
    )
    
    # Similar implementation as above examples
    print("E-commerce extraction demo - implement similar to above examples")


if __name__ == "__main__":
    print("Data Extraction Examples")
    print("1. Basic extraction from example.com")
    print("2. Google search results extraction")
    print("3. E-commerce product extraction")
    
    choice = input("\nChoose example (1-3): ")
    
    if choice == "1":
        asyncio.run(demo_data_extraction())
    elif choice == "2":
        asyncio.run(demo_google_search_extraction())
    elif choice == "3":
        asyncio.run(demo_ecommerce_extraction())
    else:
        print("Invalid choice") 