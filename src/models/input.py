"""Input models used by the current automation scripts."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator


class ViewportConfig(BaseModel):
    width: int = 1280
    height: int = 720


class ActionConfig(BaseModel):
    """Configuration for a single automation action."""
    type: str = Field(..., description="Action type: click, fill, type, wait, get_text, get_attribute, screenshot")
    selector: Optional[str] = Field(None, description="CSS or XPath selector for the element")
    value: Optional[str] = Field(None, description="Value to fill/type or attribute name for get_attribute")
    timeout: int = Field(30000, description="Timeout in milliseconds")


class ExtractConfig(BaseModel):
    """Configuration for data extraction."""
    name: str = Field(..., description="Name/key for the extracted data")
    selector: str = Field(..., description="CSS or XPath selector for the element(s)")
    attribute: Optional[str] = Field(None, description="Attribute name to extract (e.g., 'href', 'src')")
    multiple: bool = Field(False, description="Whether to extract multiple elements")


class AutomationInput(BaseModel):
    """Complete automation configuration."""
    url: str = Field(..., description="URL to navigate to")
    headless: bool = Field(True, description="Run browser in headless mode")
    timeout: int = Field(30000, description="Default timeout in milliseconds")
    viewport: ViewportConfig = Field(default_factory=ViewportConfig, description="Viewport configuration")
    wait_for_selector: Optional[str] = Field(None, description="Selector to wait for after navigation")
    actions: List[ActionConfig] = Field(default_factory=list, description="List of actions to execute")
    extract: List[ExtractConfig] = Field(default_factory=list, description="List of data extractions to perform")


class GrokInput(BaseModel):
    """Input model for Grok interaction."""

    filename: str = Field(default="", min_length=1, description="Filename to input into Grok")

    @field_validator("filename")
    @classmethod
    def strip_filename(cls, v: str):
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Filename cannot be empty")
        return cleaned

