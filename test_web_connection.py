#!/usr/bin/env python3
"""
Simple test to check web connection capabilities.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.models.input import AutomationInput
from src.core.automation import PlaywrightAutomation


async def test_web_connection():
    """Test basic web connection."""
    print("🌐 Testing web connection...")
    
    # Test URL
    test_url = "https://meet.google.com/landing"
    
    print(f"\n🔍 Testing: {test_url}")
    
    try:
        # Create automation input
        automation_input = AutomationInput(
            url=test_url,
            headless=False,  # Visible browser for debugging
            timeout=30000,
            actions=[],
            extract=[]
        )
        
        # Initialize automation
        automation = PlaywrightAutomation(
            headless=automation_input.headless,
            timeout=automation_input.timeout,
            viewport=automation_input.viewport
        )
        
        # Test connection
        print(f"  🔧 Launching browser...")
        await automation.launch()
        print(f"  ✅ Browser launched!")
        
        print(f"  🌐 Navigating to {test_url}...")
        await automation.navigate(test_url)
        print(f"  ✅ Successfully navigated to {test_url}")
        
        # Get page title
        title = await automation.page.title()
        print(f"  📄 Page title: {title}")
        
        # Wait a bit so you can see the page
        print(f"  ⏳ Waiting 3 seconds...")
        await asyncio.sleep(3)
        
        # Close browser
        await automation.close()
        print(f"  ✅ Browser closed successfully")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        try:
            await automation.close()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(test_web_connection()) 