"""
Data models for input validation and output formatting.
"""

from src.models.input import AutomationInput
from src.models.output import AutomationOutput, ErrorResponse

__all__ = [
    "AutomationInput",
    "AutomationOutput", 
    "ErrorResponse"
] 