"""Input models used by the current automation scripts."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class ViewportConfig(BaseModel):
    width: int = 1280
    height: int = 720


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

