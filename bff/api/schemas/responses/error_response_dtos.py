from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from ..common.base_dtos import ErrorDetailDto, TimestampMixin


class ValidationErrorDto(BaseModel):
    """Validation error for specific fields"""
    field: str = Field(..., description="Field name that failed validation")
    value: Any = Field(..., description="Value that was provided")
    message: str = Field(..., description="Validation error message")
    code: str = Field(..., description="Error code for programmatic handling")


class BusinessRuleErrorDto(BaseModel):
    """Business rule violation error"""
    rule_id: str = Field(..., description="Identifier of the violated business rule")
    rule_description: str = Field(..., description="Human-readable description of the rule")
    violation_details: str = Field(..., description="Details about how the rule was violated")
    suggested_action: Optional[str] = Field(None, description="Suggested action to resolve the violation")


class SystemErrorDto(BaseModel):
    """System-level error information"""
    error_id: str = Field(..., description="Unique error identifier for tracking")
    component: str = Field(..., description="System component where error occurred")
    error_type: str = Field(..., description="Type of system error")
    severity: str = Field(..., description="Error severity level")
    is_retryable: bool = Field(..., description="Whether the operation can be retried")


class ErrorResponseDto(BaseModel, TimestampMixin):
    """Standard error response structure"""

    # Basic error information
    success: bool = Field(default=False, description="Always false for error responses")
    error_code: str = Field(..., description="Standardized error code")
    message: str = Field(..., description="Human-readable error message")

    # Request context
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
    command_id: Optional[UUID] = Field(None, description="Command identifier if applicable")
    user_id: Optional[str] = Field(None, description="User identifier")

    # Detailed error information
    details: Optional[ErrorDetailDto] = Field(None, description="Detailed error information")
    validation_errors: List[ValidationErrorDto] = Field(default_factory=list, description="Field validation errors")
    business_rule_errors: List[BusinessRuleErrorDto] = Field(default_factory=list, description="Business rule violations")
    system_error: Optional[SystemErrorDto] = Field(None, description="System error details")

    # Additional context
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error occurrence timestamp")
    path: Optional[str] = Field(None, description="API endpoint path where error occurred")
    method: Optional[str] = Field(None, description="HTTP method")

    # Help and resolution
    documentation_url: Optional[str] = Field(None, description="Link to relevant documentation")
    support_contact: Optional[str] = Field(None, description="Support contact information")
    resolution_steps: List[str] = Field(default_factory=list, description="Steps to resolve the error")

    # Debugging information (only in development)
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information (dev only)")

    class Config:
        schema_extra = {
            "examples": {
                "validation_error": {
                    "success": False,
                    "error_code": "VALIDATION_FAILED",
                    "message": "Request validation failed",
                    "validation_errors": [
                        {
                            "field": "commission_rate",
                            "value": 150,
                            "message": "Commission rate must be between 0 and 100",
                            "code": "VALUE_OUT_OF_RANGE"
                        }
                    ],
                    "path": "/api/v1/campaigns/camp123/accept",
                    "method": "POST"
                },
                "business_rule_error": {
                    "success": False,
                    "error_code": "BUSINESS_RULE_VIOLATION",
                    "message": "Campaign acceptance violates business rules",
                    "business_rule_errors": [
                        {
                            "rule_id": "PARTNER_ELIGIBILITY_001",
                            "rule_description": "Partner must have minimum 1000 followers",
                            "violation_details": "Partner has only 500 followers",
                            "suggested_action": "Increase follower count or apply for exception"
                        }
                    ]
                },
                "system_error": {
                    "success": False,
                    "error_code": "SYSTEM_ERROR",
                    "message": "Internal system error occurred",
                    "system_error": {
                        "error_id": "ERR-2025-001-12345",
                        "component": "pulsar_publisher",
                        "error_type": "CONNECTION_TIMEOUT",
                        "severity": "HIGH",
                        "is_retryable": True
                    },
                    "resolution_steps": [
                        "Wait a moment and retry the request",
                        "Contact support if problem persists"
                    ]
                }
            }
        }


class FieldErrorDto(BaseModel):
    """Specific field error for form validation"""
    field_path: str = Field(..., description="JSONPath to the field with error")
    error_type: str = Field(..., description="Type of validation error")
    message: str = Field(..., description="Error message")
    rejected_value: Any = Field(..., description="Value that was rejected")
    allowed_values: Optional[List[Any]] = Field(None, description="List of allowed values")


class BatchErrorResponseDto(BaseModel):
    """Error response for batch operations"""
    success: bool = Field(default=False)
    total_items: int = Field(..., description="Total number of items processed")
    successful_items: int = Field(..., description="Number of successfully processed items")
    failed_items: int = Field(..., description="Number of failed items")

    # Individual item errors
    item_errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errors for individual items")

    # Overall batch error
    batch_error: Optional[ErrorResponseDto] = Field(None, description="Overall batch processing error")

    # Summary
    error_summary: Dict[str, int] = Field(default_factory=dict, description="Count of errors by type")


class RateLimitErrorDto(BaseModel):
    """Rate limiting error response"""
    success: bool = Field(default=False)
    error_code: str = Field(default="RATE_LIMIT_EXCEEDED")
    message: str = Field(..., description="Rate limit error message")

    # Rate limit details
    limit: int = Field(..., description="Rate limit threshold")
    window_seconds: int = Field(..., description="Rate limit window in seconds")
    remaining_requests: int = Field(..., description="Remaining requests in current window")
    reset_time: datetime = Field(..., description="When the rate limit resets")

    # Retry information
    retry_after_seconds: int = Field(..., description="Seconds to wait before retrying")


class AuthenticationErrorDto(BaseModel):
    """Authentication error response"""
    success: bool = Field(default=False)
    error_code: str = Field(..., description="Authentication error code")
    message: str = Field(..., description="Authentication error message")

    # Authentication details
    auth_method: Optional[str] = Field(None, description="Authentication method used")
    token_expired: Optional[bool] = Field(None, description="Whether token has expired")
    required_scopes: Optional[List[str]] = Field(None, description="Required authentication scopes")

    # Resolution steps
    login_url: Optional[str] = Field(None, description="URL to re-authenticate")
    refresh_token_url: Optional[str] = Field(None, description="URL to refresh token")


class ConflictErrorDto(BaseModel):
    """Conflict error for resource state issues"""
    success: bool = Field(default=False)
    error_code: str = Field(default="CONFLICT")
    message: str = Field(..., description="Conflict error message")

    # Conflict details
    conflicting_resource: str = Field(..., description="Resource that conflicts")
    current_state: str = Field(..., description="Current state of the resource")
    requested_state: str = Field(..., description="Requested state")

    # Resolution options
    resolution_options: List[str] = Field(default_factory=list, description="Possible ways to resolve conflict")
    force_override_available: bool = Field(default=False, description="Whether force override is possible")


class NotFoundErrorDto(BaseModel):
    """Resource not found error"""
    success: bool = Field(default=False)
    error_code: str = Field(default="NOT_FOUND")
    message: str = Field(..., description="Not found error message")

    # Resource details
    resource_type: str = Field(..., description="Type of resource not found")
    resource_id: str = Field(..., description="ID of resource not found")

    # Suggestions
    similar_resources: Optional[List[str]] = Field(None, description="Similar resources that exist")
    search_suggestions: Optional[List[str]] = Field(None, description="Search suggestions")