from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class TimestampMixin:
    """Mixin for DTOs that need timestamp fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class UserContextMixin(BaseModel):
    """Mixin for DTOs that need user context"""
    user_id: str = Field(..., description="User ID extracted from JWT")


class PaginationRequest(BaseModel):
    """Standard pagination request DTO"""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(50, ge=1, le=100, description="Number of items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("desc", description="Sort order: asc or desc")

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v and v.lower() not in ['asc', 'desc']:
            raise ValueError('sort_order must be either "asc" or "desc"')
        return v.lower() if v else v


class PaginationResponse(BaseModel):
    """Standard pagination response DTO"""
    page: int
    page_size: int
    total_count: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(cls, page: int, page_size: int, total_count: int):
        """Factory method to create pagination response"""
        total_pages = (total_count + page_size - 1) // page_size
        return cls(
            page=page,
            page_size=page_size,
            total_count=total_count,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


class CommandStatus(str, Enum):
    """Standard command processing statuses"""
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class ValidationStatus(str, Enum):
    """Standard validation statuses"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    UNDER_REVIEW = "UNDER_REVIEW"


class Priority(str, Enum):
    """Standard priority levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Currency(str, Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"


class MoneyDto(BaseModel):
    """Money value with currency"""
    amount: float = Field(..., ge=0, description="Amount in the specified currency")
    currency: Currency = Field(default=Currency.USD, description="Currency code")

    def __str__(self):
        return f"{self.amount} {self.currency}"


class AddressDto(BaseModel):
    """Standard address DTO"""
    street: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str


class ContactDto(BaseModel):
    """Standard contact information DTO"""
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = None
    website: Optional[str] = None


class MetadataDto(BaseModel):
    """Generic metadata container"""
    tags: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    source: Optional[str] = None
    version: str = Field(default="v1")


class ErrorDetailDto(BaseModel):
    """Detailed error information"""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthCheckDto(BaseModel):
    """Health check response DTO"""
    status: str = Field(..., description="Overall health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dependencies: Optional[Dict[str, str]] = Field(default_factory=dict)
    uptime_seconds: Optional[int] = None