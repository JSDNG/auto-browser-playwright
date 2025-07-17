"""
Output format models for automation responses.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    success: bool = Field(
        default=False,
        description="Indicates if the operation was successful"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Empty data object for error responses"
    )
    error: str = Field(
        description="Error message describing what went wrong"
    )
    error_type: Optional[str] = Field(
        default=None,
        description="Type of error (validation, automation, timeout, etc.)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the error occurred"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }
        json_schema_extra = {
            "example": {
                "success": False,
                "data": {},
                "error": "Element not found: #submit-button",
                "error_type": "automation",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class AutomationOutput(BaseModel):
    """Model for successful automation responses."""
    
    success: bool = Field(
        default=True,
        description="Indicates if the operation was successful"
    )
    data: Dict[str, Any] = Field(
        description="Extracted data from the automation"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message (null for successful responses)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the automation completed"
    )
    execution_time: Optional[float] = Field(
        default=None,
        description="Execution time in seconds"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "title": "Example Page",
                    "links": [
                        "https://example.com/page1",
                        "https://example.com/page2"
                    ]
                },
                "error": None,
                "timestamp": "2024-01-01T00:00:00Z",
                "execution_time": 2.5
            }
        }


def create_success_response(data: Dict[str, Any], execution_time: Optional[float] = None) -> AutomationOutput:
    """Create a successful automation response."""
    return AutomationOutput(
        data=data,
        execution_time=execution_time
    )


def create_error_response(error: str, error_type: Optional[str] = None) -> ErrorResponse:
    """Create an error response."""
    return ErrorResponse(
        error=error,
        error_type=error_type
    ) 