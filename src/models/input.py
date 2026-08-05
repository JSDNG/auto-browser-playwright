"""
Input models used by the CDP tracking automation.
"""

from pydantic import BaseModel


class ViewportConfig(BaseModel):
    width: int = 1280
    height: int = 720
