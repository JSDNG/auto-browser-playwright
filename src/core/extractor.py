from src.models.input import ExtractConfig
from playwright.async_api import Page


class DataExtractor:
    def __init__(self, page: Page):
        self.page = page

    def _format_selector(self, selector: str) -> str:
        """Format selector to support both CSS and XPath."""
        # If selector starts with // or contains xpath=, treat as XPath
        if selector.startswith("//") or selector.startswith("xpath="):
            if not selector.startswith("xpath="):
                return f"xpath={selector}"
            return selector
        return selector

    async def extract(self, extract_config: ExtractConfig):
        """Extract data based on configuration"""
        selector = self._format_selector(extract_config.selector)
        
        if extract_config.multiple:
            elements = await self.page.query_selector_all(selector)
            results = []
            
            for element in elements:
                if extract_config.attribute:
                    value = await element.get_attribute(extract_config.attribute)
                else:
                    value = await element.text_content()
                results.append(value)
            
            return results
        else:
            element = await self.page.query_selector(selector)
            if element:
                if extract_config.attribute:
                    return await element.get_attribute(extract_config.attribute)
                else:
                    return await element.text_content()
            return None 