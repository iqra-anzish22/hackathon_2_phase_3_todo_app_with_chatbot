"""
Pydantic schemas for error responses.
Defines the structure of error responses returned by the API.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """
    Field-level error detail for validation errors.

    Used in ErrorResponse.details to provide specific information
    about which fields failed validation and why.
    """
    field: str = Field(..., description="Name of the field that failed validation")
    message: str = Field(..., description="Specific validation error message for this field")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "title",
                "message": "Title cannot be empty or whitespace only"
            }
        }


class ErrorResponse(BaseModel):
    """
    Standardized error response structure for all API errors.

    All error responses follow this format to ensure consistency
    and enable uniform error handling on the frontend.
    """
    error_code: str = Field(
        ...,
        description="Machine-readable error identifier (UPPER_SNAKE_CASE)",
        pattern="^[A-Z_]+$"
    )
    message: str = Field(
        ...,
        description="Human-readable error message for display to users",
        min_length=1,
        max_length=500
    )
    details: Optional[List[ErrorDetail]] = Field(
        None,
        description="Optional array of field-level error details (only for validation errors)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": [
                    {
                        "field": "title",
                        "message": "Title cannot be empty or whitespace only"
                    }
                ]
            }
        }
