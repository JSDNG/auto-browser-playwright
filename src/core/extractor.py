"""
Data extractor for extracting structured data from web pages.
"""

import re
from typing import List, Any, Optional, Union, Dict
from playwright.async_api import Page, ElementHandle

from src.models.input import ExtractItem


class DataExtractor:
    """Extractor for structured data from web pages."""
    
    def __init__(self, page: Page):
        """Initialize data extractor."""
        self.page = page
    
    async def extract(self, extract_item: ExtractItem) -> Any:
        """Extract data based on extraction configuration."""
        selector = extract_item.selector
        attribute = extract_item.attribute
        multiple = extract_item.multiple
        
        try:
            if multiple:
                return await self._extract_multiple(selector, attribute)
            else:
                return await self._extract_single(selector, attribute)
                
        except Exception as e:
            # Return None for missing elements instead of raising error
            return None if not multiple else []
    
    async def _extract_single(self, selector: str, attribute: Optional[str] = None) -> Any:
        """Extract single element data."""
        try:
            # Try to wait for selector with increased timeout
            element = await self.page.wait_for_selector(selector, timeout=10000)
            if not element:
                return None
            
            if attribute:
                # Extract attribute value
                value = await element.get_attribute(attribute)
                return self._clean_text(value) if value else None
            else:
                # Extract text content
                text = await element.text_content()
                return self._clean_text(text) if text else None
                
        except Exception as e:
            # If original selector fails, try some common fallbacks
            if selector == "h1":
                fallback_selectors = ["h1", "h2", "h3", "title", "[role='heading']", ".title", "#title"]
                for fallback in fallback_selectors:
                    try:
                        element = await self.page.query_selector(fallback)
                        if element:
                            if attribute:
                                value = await element.get_attribute(attribute)
                                return self._clean_text(value) if value else None
                            else:
                                text = await element.text_content()
                                if text and text.strip():
                                    return self._clean_text(text)
                    except:
                        continue
                
                # Final fallback: try to get page title
                try:
                    page_title = await self.page.title()
                    if page_title:
                        return self._clean_text(page_title)
                except:
                    pass
            
            return None
    
    async def _extract_multiple(self, selector: str, attribute: Optional[str] = None) -> List[Any]:
        """Extract multiple elements data."""
        try:
            elements = await self.page.query_selector_all(selector)
            if not elements:
                return []
            
            results = []
            for element in elements:
                if attribute:
                    # Extract attribute value
                    value = await element.get_attribute(attribute)
                    if value:
                        results.append(self._clean_text(value))
                else:
                    # Extract text content
                    text = await element.text_content()
                    if text:
                        results.append(self._clean_text(text))
            
            return results
            
        except Exception:
            return []
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common unwanted characters
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        return text.strip()
    
    async def extract_table(self, table_selector: str) -> List[Dict[str, str]]:
        """Extract table data."""
        try:
            table = await self.page.wait_for_selector(table_selector, timeout=5000)
            if not table:
                return []
            
            # Extract headers
            headers = []
            header_cells = await table.query_selector_all("thead th, thead td")
            for cell in header_cells:
                text = await cell.text_content()
                headers.append(self._clean_text(text) if text else "")
            
            # Extract rows
            rows = []
            row_elements = await table.query_selector_all("tbody tr")
            for row_element in row_elements:
                cells = await row_element.query_selector_all("td")
                row_data = {}
                
                for i, cell in enumerate(cells):
                    text = await cell.text_content()
                    column_name = headers[i] if i < len(headers) else f"column_{i}"
                    row_data[column_name] = self._clean_text(text) if text else ""
                
                rows.append(row_data)
            
            return rows
            
        except Exception:
            return []
    
    async def extract_links(self, container_selector: str = "body") -> List[Dict[str, str]]:
        """Extract all links from container."""
        try:
            container = await self.page.wait_for_selector(container_selector, timeout=5000)
            if not container:
                return []
            
            links = []
            link_elements = await container.query_selector_all("a[href]")
            
            for link in link_elements:
                href = await link.get_attribute("href")
                text = await link.text_content()
                
                if href:
                    links.append({
                        "url": href,
                        "text": self._clean_text(text) if text else ""
                    })
            
            return links
            
        except Exception:
            return []
    
    async def extract_forms(self, container_selector: str = "body") -> List[Dict[str, Any]]:
        """Extract form data from container."""
        try:
            container = await self.page.wait_for_selector(container_selector, timeout=5000)
            if not container:
                return []
            
            forms = []
            form_elements = await container.query_selector_all("form")
            
            for form in form_elements:
                form_data = {
                    "action": await form.get_attribute("action") or "",
                    "method": await form.get_attribute("method") or "GET",
                    "fields": []
                }
                
                # Extract form fields
                inputs = await form.query_selector_all("input, textarea, select")
                for input_element in inputs:
                    field_data = {
                        "name": await input_element.get_attribute("name") or "",
                        "type": await input_element.get_attribute("type") or "",
                        "value": await input_element.get_attribute("value") or "",
                        "required": await input_element.get_attribute("required") is not None
                    }
                    form_data["fields"].append(field_data)
                
                forms.append(form_data)
            
            return forms
            
        except Exception:
            return []
    
    async def extract_meta_data(self) -> Dict[str, str]:
        """Extract page metadata."""
        try:
            meta_data = {}
            
            # Get page title
            title = await self.page.title()
            meta_data["title"] = title if title else ""
            
            # Get meta tags
            meta_tags = await self.page.query_selector_all("meta")
            for meta in meta_tags:
                name = await meta.get_attribute("name")
                content = await meta.get_attribute("content")
                
                if name and content:
                    meta_data[name] = content
                
                # Also check for property attribute (Open Graph)
                property_attr = await meta.get_attribute("property")
                if property_attr and content:
                    meta_data[property_attr] = content
            
            # Get canonical URL
            canonical = await self.page.query_selector("link[rel='canonical']")
            if canonical:
                href = await canonical.get_attribute("href")
                if href:
                    meta_data["canonical"] = href
            
            return meta_data
            
        except Exception:
            return {}
    
    async def extract_images(self, container_selector: str = "body") -> List[Dict[str, str]]:
        """Extract image data from container."""
        try:
            container = await self.page.wait_for_selector(container_selector, timeout=5000)
            if not container:
                return []
            
            images = []
            img_elements = await container.query_selector_all("img")
            
            for img in img_elements:
                src = await img.get_attribute("src")
                alt = await img.get_attribute("alt")
                title = await img.get_attribute("title")
                
                if src:
                    images.append({
                        "src": src,
                        "alt": alt or "",
                        "title": title or ""
                    })
            
            return images
            
        except Exception:
            return [] 