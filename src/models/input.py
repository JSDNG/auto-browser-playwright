"""
Input validation models for automation requests.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import re


class ViewportConfig(BaseModel):
    width: int = 1280
    height: int = 720


class ActionConfig(BaseModel):
    type: str
    selector: Optional[str] = None
    value: Optional[str] = None
    timeout: int = 30000
    wait_until: Optional[str] = "domcontentloaded"


class ExtractConfig(BaseModel):
    name: str
    selector: str
    attribute: Optional[str] = None
    multiple: bool = False


class AutomationInput(BaseModel):
    url: str 
    headless: bool = False
    timeout: int = 300000
    viewport: ViewportConfig = Field(default_factory=ViewportConfig)
    wait_for_selector: Optional[str] = None
    actions: List[ActionConfig] = Field(default_factory=list)
    extract: List[ExtractConfig] = Field(default_factory=list)
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format and provide fallback"""
        if not v or v.lower() in ['string', 'none', 'null', '']:
            return "https://www.amazon.com/"
        
        # Simple URL validation
        url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
        if not url_pattern.match(v):
            # If not a valid URL, use default
            return "https://www.amazon.com/"
        
        return v 


class SearchInput(BaseModel):
    """Simple search input for Etsy scraping."""

    keyword: str = Field(default="t-shirt", min_length=1)
    pages: int = Field(default=5, ge=1, le=20)

    @validator("keyword")
    def strip_keyword(cls, v: str):
        cleaned = v.strip()
        return cleaned or "t-shirt"