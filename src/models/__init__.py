"""
Data models for input validation and output formatting.
"""

from .input import AutomationInput, Action
from .output import AutomationOutput, ErrorResponse

__all__ = [
    "AutomationInput",
    "Action",
    "AutomationOutput", 
    "ErrorResponse"
] 