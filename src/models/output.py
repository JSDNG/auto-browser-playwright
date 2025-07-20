"""
Output format models for automation responses.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AutomationOutput(BaseModel):
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    execution_time: Optional[float] = None
    error: Optional[str] = None
    error_type: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    data: Dict[str, Any] = Field(default_factory=dict)
    error: str
    error_type: Optional[str] = None


def create_success_response(data: Dict[str, Any], execution_time: Optional[float] = None) -> AutomationOutput:
    """Create a successful automation response."""
    return AutomationOutput(
        success=True,
        data=data,
        execution_time=execution_time
    )


def create_error_response(error: str, error_type: Optional[str] = None) -> ErrorResponse:
    """Create an error response."""
    return ErrorResponse(
        error=error,
        error_type=error_type
    ) 