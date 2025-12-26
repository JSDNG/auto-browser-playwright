"""
Action executor for custom automation actions.
"""

import asyncio
import sys
from typing import Optional, List
from playwright.async_api import Page, ElementHandle

from src.models.input import ActionConfig


class ActionExecutor:
    """Executor for automation actions."""
    
    def __init__(self, page: Page):
        """Initialize action executor."""
        self.page = page
        self.extracted_data = {}  # Store extracted data
    
    def _format_selector(self, selector: str) -> str:
        """Format selector to support both CSS and XPath."""
        if not selector:
            return selector
        # If selector starts with // or contains xpath=, treat as XPath
        if selector.startswith("//") or selector.startswith("xpath="):
            if not selector.startswith("xpath="):
                return f"xpath={selector}"
            return selector
        return selector
    
    async def execute(self, action: ActionConfig):
        """Execute an action"""
        action_type = action.type.lower()
        selector = self._format_selector(action.selector) if action.selector else None
        
        if action_type == "click":
            if not selector:
                raise ValueError("Selector is required for click action")
            await self.page.click(selector, timeout=action.timeout)
            
        elif action_type == "fill":
            if not selector:
                raise ValueError("Selector is required for fill action")
            await self.page.fill(selector, action.value or "", timeout=action.timeout)
            
        elif action_type == "type":
            if not selector:
                raise ValueError("Selector is required for type action")
            await self.page.type(selector, action.value or "", timeout=action.timeout)
            
        elif action_type == "wait":
            if selector:
                await self.page.wait_for_selector(selector, timeout=action.timeout)
            else:
                await asyncio.sleep(action.timeout / 1000)
                
        elif action_type == "get_text":
            if not selector:
                raise ValueError("Selector is required for get_text action")
            element = await self.page.query_selector(selector)
            if element:
                text = await element.text_content()
                self.extracted_data[action.selector] = text
                
        elif action_type == "get_attribute":
            if not selector:
                raise ValueError("Selector is required for get_attribute action")
            if not action.value:
                raise ValueError("Attribute name (value) is required for get_attribute action")
            element = await self.page.query_selector(selector)
            if element:
                attr_value = await element.get_attribute(action.value)
                self.extracted_data[f"{action.selector}_{action.value}"] = attr_value
                
        elif action_type == "screenshot":
            screenshot = await self.page.screenshot()
            self.extracted_data["screenshot"] = screenshot
            
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def get_extracted_data(self):
        """Get extracted data from actions"""
        return self.extracted_data
    
    def clear_extracted_data(self) -> None:
        """Clear extracted data."""
        self.extracted_data.clear()
    
    # Data extraction methods
    async def _get_text(self, selector: str, timeout: int) -> str:
        """Extract text content from element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        text = await element.text_content()
        return text.strip() if text else ""
    
    async def _get_attribute(self, selector: str, attribute: str, timeout: int) -> Optional[str]:
        """Extract attribute value from element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        return await element.get_attribute(attribute)
    
    async def _get_href(self, selector: str, timeout: int) -> Optional[str]:
        """Extract href attribute from anchor element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        href = await element.get_attribute("href")
        return href
    
    async def _get_src(self, selector: str, timeout: int) -> Optional[str]:
        """Extract src attribute from img/iframe/script element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        src = await element.get_attribute("src")
        return src
    
    async def _get_value(self, selector: str, timeout: int) -> Optional[str]:
        """Extract value from input element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        value = await element.get_attribute("value")
        return value
    
    async def _get_html(self, selector: str, timeout: int) -> str:
        """Extract innerHTML from element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        html = await element.inner_html()
        return html
    
    async def _get_all_text(self, selector: str, timeout: int) -> List[str]:
        """Extract text content from all matching elements."""
        try:
            elements = await self.page.query_selector_all(selector)
            if not elements:
                return []
            
            texts = []
            for element in elements:
                text = await element.text_content()
                if text:
                    texts.append(text.strip())
            
            return texts
        except Exception as e:
            print(f"[WARNING] get_all_text failed for selector '{selector}': {e}", file=sys.stderr)
            return []
    
    async def _get_all_attributes(self, selector: str, attribute: str, timeout: int) -> List[Optional[str]]:
        """Extract attribute values from all matching elements."""
        try:
            elements = await self.page.query_selector_all(selector)
            if not elements:
                return []
            
            attributes = []
            for element in elements:
                attr_value = await element.get_attribute(attribute)
                attributes.append(attr_value)
            
            return attributes
        except Exception as e:
            print(f"[WARNING] get_all_attributes failed for selector '{selector}': {e}", file=sys.stderr)
            return [] 