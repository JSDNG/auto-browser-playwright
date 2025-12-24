"""Input models used by the current automation scripts."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class ViewportConfig(BaseModel):
    width: int = 1280
    height: int = 720


class GrokInput(BaseModel):
    """Input model for Grok interaction."""

    text: str = Field(default="", min_length=1, description="Text to input into Grok")

    @field_validator("text")
    @classmethod
    def strip_text(cls, v: str):
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Text cannot be empty")
        return cleaned

