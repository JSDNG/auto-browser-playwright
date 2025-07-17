"""
Input validation models for automation requests.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator, HttpUrl


class Action(BaseModel):
    """Model for automation actions."""
    
    type: Literal[
        "click", "fill", "select", "wait", "press", "hover", "check", "uncheck",
        "get_text", "get_attribute", "get_href", "get_src", "get_value", "get_html",
        "get_all_text", "get_all_attributes"
    ] = Field(
        description="Type of action to perform"
    )
    selector: str = Field(
        description="CSS selector for target element"
    )
    value: Optional[str] = Field(
        default=None,
        description="Value for fill, select, or press actions"
    )
    timeout: Optional[int] = Field(
        default=5000,
        description="Timeout in milliseconds for the action"
    )
    extract_name: Optional[str] = Field(
        default=None,
        description="Name for extracted data (required for get_* actions)"
    )
    attribute: Optional[str] = Field(
        default=None,
        description="Attribute name for get_attribute action"
    )
    
    @validator("selector")
    def validate_selector(cls, v):
        """Validate CSS selector format."""
        if not v or not v.strip():
            raise ValueError("Selector cannot be empty")
        return v.strip()
    
    @validator("value")
    def validate_value(cls, v, values):
        """Validate value based on action type."""
        action_type = values.get("type")
        if action_type in ["fill", "select", "press"] and not v:
            raise ValueError(f"Value is required for {action_type} action")
        return v
    
    @validator("extract_name")
    def validate_extract_name(cls, v, values):
        """Validate extract_name based on action type."""
        action_type = values.get("type")
        extract_actions = ["get_text", "get_attribute", "get_href", "get_src", "get_value", "get_html", "get_all_text", "get_all_attributes"]
        if action_type in extract_actions and not v:
            raise ValueError(f"extract_name is required for {action_type} action")
        return v
    
    @validator("attribute")
    def validate_attribute(cls, v, values):
        """Validate attribute based on action type."""
        action_type = values.get("type")
        if action_type == "get_attribute" and not v:
            raise ValueError("attribute is required for get_attribute action")
        return v


class ExtractItem(BaseModel):
    """Model for data extraction configuration."""
    
    name: str = Field(
        description="Name for the extracted data"
    )
    selector: str = Field(
        description="CSS selector for target element"
    )
    attribute: Optional[str] = Field(
        default=None,
        description="Attribute to extract (default: text content)"
    )
    multiple: bool = Field(
        default=False,
        description="Whether to extract multiple elements"
    )
    
    @validator("name")
    def validate_name(cls, v):
        """Validate extraction name."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @validator("selector")
    def validate_selector(cls, v):
        """Validate CSS selector format."""
        if not v or not v.strip():
            raise ValueError("Selector cannot be empty")
        return v.strip()


class AutomationInput(BaseModel):
    """Main input model for automation requests."""
    
    url: HttpUrl = Field(
        description="Target URL for automation"
    )
    actions: List[Action] = Field(
        default_factory=list,
        description="List of actions to perform"
    )
    extract: List[ExtractItem] = Field(
        default_factory=list,
        description="List of data extraction configurations"
    )
    headless: bool = Field(
        default=False,
        description="Whether to run browser in headless mode"
    )
    timeout: int = Field(
        default=30000,
        description="Global timeout in milliseconds"
    )
    viewport: Optional[Dict[str, int]] = Field(
        default=None,
        description="Viewport configuration {width: int, height: int}"
    )
    wait_for_selector: Optional[str] = Field(
        default=None,
        description="Wait for specific selector before starting actions"
    )
    
    @validator("url")
    def validate_url(cls, v):
        """Validate URL security."""
        url_str = str(v)
        
        # Allow common test and development URLs
        allowed_patterns = [
            "https://example.com",
            "https://httpbin.org",
            "https://google.com",
            "https://meet.google.com",
            "https://www.google.com",
            "https://github.com",
            "https://stackoverflow.com"
        ]
        
        # Check if URL starts with allowed patterns
        for pattern in allowed_patterns:
            if url_str.startswith(pattern):
                return v
        
        # Block dangerous local URLs only in production
        import os
        if os.getenv("ENVIRONMENT") == "production":
            blocked_domains = [
                "127.0.0.1",
                "0.0.0.0",
                "10.",
                "192.168.",
                "172.16.",
                "172.17.",
                "172.18.",
                "172.19.",
                "172.20.",
                "172.21.",
                "172.22.",
                "172.23.",
                "172.24.",
                "172.25.",
                "172.26.",
                "172.27.",
                "172.28.",
                "172.29.",
                "172.30.",
                "172.31."
            ]
            
            for blocked in blocked_domains:
                if blocked in url_str:
                    raise ValueError(f"URL contains blocked domain: {blocked}")
        
        return v
    
    @validator("timeout")
    def validate_timeout(cls, v):
        """Validate timeout value."""
        if v < 1000 or v > 300000:  # 1 second to 5 minutes
            raise ValueError("Timeout must be between 1000ms and 300000ms")
        return v
    
    @validator("viewport")
    def validate_viewport(cls, v):
        """Validate viewport configuration."""
        if v is not None:
            if "width" not in v or "height" not in v:
                raise ValueError("Viewport must contain width and height")
            if v["width"] < 100 or v["height"] < 100:
                raise ValueError("Viewport dimensions must be at least 100x100")
            if v["width"] > 3840 or v["height"] > 2160:
                raise ValueError("Viewport dimensions must not exceed 3840x2160")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "actions": [
                    {
                        "type": "fill",
                        "selector": "#username",
                        "value": "testuser"
                    },
                    {
                        "type": "click",
                        "selector": "#submit"
                    }
                ],
                "extract": [
                    {
                        "name": "title",
                        "selector": "h1"
                    },
                    {
                        "name": "links",
                        "selector": "a",
                        "attribute": "href",
                        "multiple": True
                    }
                ],
                "headless": True,
                "timeout": 30000
            }
        } 