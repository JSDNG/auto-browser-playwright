"""Input models used by the current automation scripts."""

from pydantic import BaseModel, Field, validator


class ViewportConfig(BaseModel):
    width: int = 1280
    height: int = 720


class SearchInput(BaseModel):
    """Simple search input for Etsy scraping."""

    keyword: str = Field(default="t-shirt", min_length=1)
    pages: int = Field(default=5, ge=1, le=20)

    @validator("keyword")
    def strip_keyword(cls, v: str):
        cleaned = v.strip()
        return cleaned or "t-shirt"