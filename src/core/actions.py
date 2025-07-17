"""
Action executor for custom automation actions.
"""

import asyncio
import sys
from typing import Optional, List
from playwright.async_api import Page, ElementHandle

from src.models.input import Action


class ActionExecutor:
    """Executor for automation actions."""
    
    def __init__(self, page: Page):
        """Initialize action executor."""
        self.page = page
        self.extracted_data = {}  # Store extracted data
    
    async def execute(self, action: Action) -> None:
        """Execute a single action with error handling."""
        action_type = action.type
        selector = action.selector
        value = action.value
        timeout = action.timeout or 5000
        extract_name = action.extract_name
        attribute = action.attribute
        
        try:
            # Wait for element to be present (not needed for get_all_* actions)
            if not action_type.startswith("get_all_"):
                await self.page.wait_for_selector(selector, timeout=timeout)
            
            # Execute based on action type
            if action_type == "click":
                await self._click(selector, timeout)
            elif action_type == "fill":
                await self._fill(selector, value, timeout)
            elif action_type == "select":
                await self._select(selector, value, timeout)
            elif action_type == "wait":
                await self._wait(selector, timeout)
            elif action_type == "press":
                await self._press(selector, value, timeout)
            elif action_type == "hover":
                await self._hover(selector, timeout)
            elif action_type == "check":
                await self._check(selector, timeout)
            elif action_type == "uncheck":
                await self._uncheck(selector, timeout)
            # Data extraction actions
            elif action_type == "get_text":
                result = await self._get_text(selector, timeout)
                self.extracted_data[extract_name] = result
            elif action_type == "get_attribute":
                result = await self._get_attribute(selector, attribute, timeout)
                self.extracted_data[extract_name] = result
            elif action_type == "get_href":
                result = await self._get_href(selector, timeout)
                self.extracted_data[extract_name] = result
            elif action_type == "get_src":
                result = await self._get_src(selector, timeout)
                self.extracted_data[extract_name] = result
            elif action_type == "get_value":
                result = await self._get_value(selector, timeout)
                self.extracted_data[extract_name] = result
            elif action_type == "get_html":
                result = await self._get_html(selector, timeout)
                self.extracted_data[extract_name] = result
            elif action_type == "get_all_text":
                result = await self._get_all_text(selector, timeout)
                self.extracted_data[extract_name] = result
            elif action_type == "get_all_attributes":
                result = await self._get_all_attributes(selector, attribute, timeout)
                self.extracted_data[extract_name] = result
            else:
                raise ValueError(f"Unknown action type: {action_type}")
                
        except Exception as e:
            # Log warning but continue with next action
            import sys
            print(f"[WARNING] Action '{action_type}' failed on selector '{selector}': {e}", file=sys.stderr)
            print(f"[WARNING] Skipping action and continuing with next one...", file=sys.stderr)
            # Don't raise exception - just continue
    
    async def _click(self, selector: str, timeout: int) -> None:
        """Click element with human-like behavior."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Scroll into view if needed
        await element.scroll_into_view_if_needed()
        
        # Wait for element to be clickable
        await element.wait_for_element_state("stable", timeout=timeout)
        
        # Add random mouse movement before click (human-like behavior)
        import random
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Hover over element first
        await element.hover()
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # Click element
        await element.click()
        
        # Add small delay after click
        await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def _fill(self, selector: str, value: str, timeout: int) -> None:
        """Fill input field with human-like behavior."""
        if not value:
            raise ValueError("Value is required for fill action")
        
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Click on the element first (human-like behavior)
        await element.click()
        
        # Add small delay to mimic human behavior
        await asyncio.sleep(0.5)
        
        # Type with human-like speed (100ms between characters)
        await element.fill("", force=True)  # Clear first
        await element.type(value, delay=100)  # Type with delay
        
        # Add another small delay
        await asyncio.sleep(0.3)
    
    async def _select(self, selector: str, value: str, timeout: int) -> None:
        """Select option in dropdown."""
        if not value:
            raise ValueError("Value is required for select action")
        
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Select option by value
        await element.select_option(value)
    
    async def _wait(self, selector: str, timeout: int) -> None:
        """Wait for element to be present."""
        await self.page.wait_for_selector(selector, timeout=timeout)
    
    async def _press(self, selector: str, key: str, timeout: int) -> None:
        """Press key on element."""
        if not key:
            raise ValueError("Key is required for press action")
        
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Focus element and press key
        await element.focus()
        await element.press(key)
    
    async def _hover(self, selector: str, timeout: int) -> None:
        """Hover over element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Scroll element into view and hover
        await element.scroll_into_view_if_needed()
        await element.hover()
    
    async def _check(self, selector: str, timeout: int) -> None:
        """Check checkbox or radio button."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Check if already checked
        is_checked = await element.is_checked()
        if not is_checked:
            await element.check()
    
    async def _uncheck(self, selector: str, timeout: int) -> None:
        """Uncheck checkbox."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Check if already unchecked
        is_checked = await element.is_checked()
        if is_checked:
            await element.uncheck()
    
    async def execute_batch(self, actions: List[Action]) -> None:
        """Execute multiple actions in sequence."""
        for action in actions:
            await self.execute(action)
            
            # Small delay between actions
            await asyncio.sleep(0.1)
    
    async def wait_for_element_state(
        self, 
        selector: str, 
        state: str, 
        timeout: int = 5000
    ) -> None:
        """Wait for element to reach specific state."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        await element.wait_for_element_state(state, timeout=timeout)
    
    async def scroll_to_element(self, selector: str, timeout: int = 5000) -> None:
        """Scroll to element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        await element.scroll_into_view_if_needed()
    
    async def get_element_text(self, selector: str, timeout: int = 5000) -> str:
        """Get text content of element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        return await element.text_content() or ""
    
    async def get_element_attribute(
        self, 
        selector: str, 
        attribute: str, 
        timeout: int = 5000
    ) -> Optional[str]:
        """Get attribute value of element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        return await element.get_attribute(attribute)
    
    async def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is visible."""
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            if not element:
                return False
            
            return await element.is_visible()
        except:
            return False
    
    async def is_element_enabled(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is enabled."""
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            if not element:
                return False
            
            return await element.is_enabled()
        except:
            return False
    
    def get_extracted_data(self) -> dict:
        """Get all extracted data."""
        return self.extracted_data.copy()
    
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