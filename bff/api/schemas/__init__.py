# BFF API Schemas Package

# Request Schemas
from .requests.campaign_requests import AcceptCampaignRequest, AcceptanceTerms, PartnerType, CommissionType
from .requests.evidence_requests import (
    UploadEvidenceRequest, EvidenceDetails, AudienceData, EngagementMetrics, Demographics,
    EvidenceType, Platform, ContentType
)
from .requests.payment_requests import (
    RequestPaymentRequest, PaymentDetails, CommissionPeriod, InvoiceDetails, AccountInfo,
    RequestType, PaymentMethod, AccountType
)

# Response Schemas
from .responses.campaign_responses import AcceptCampaignResponse
from .responses.evidence_responses import UploadEvidenceResponse
from .responses.payment_responses import RequestPaymentResponse
from .responses.error_response_dtos import (
    ErrorResponseDto,
    ValidationErrorDto,
    BusinessRuleErrorDto,
    SystemErrorDto,
    FieldErrorDto,
    BatchErrorResponseDto,
    RateLimitErrorDto,
    AuthenticationErrorDto,
    ConflictErrorDto,
    NotFoundErrorDto,
)

# Common Base Types
from .common.base_dtos import (
    TimestampMixin,
    UserContextMixin,
    PaginationRequest,
    PaginationResponse,
    CommandStatus,
    ValidationStatus,
    Priority,
    Currency,
    MoneyDto,
    AddressDto,
    ContactDto,
    MetadataDto,
    ErrorDetailDto,
    HealthCheckDto,
)

__all__ = [
    # Request Schemas
    "AcceptCampaignRequest",
    "AcceptanceTerms",
    "PartnerType",
    "CommissionType",
    "UploadEvidenceRequest",
    "EvidenceDetails",
    "AudienceData",
    "EngagementMetrics",
    "Demographics",
    "EvidenceType",
    "Platform",
    "ContentType",
    "RequestPaymentRequest",
    "PaymentDetails",
    "CommissionPeriod",
    "InvoiceDetails",
    "AccountInfo",
    "RequestType",
    "PaymentMethod",
    "AccountType",

    # Response Schemas
    "AcceptCampaignResponse",
    "UploadEvidenceResponse",
    "RequestPaymentResponse",

    # Error Schemas
    "ErrorResponseDto",
    "ValidationErrorDto",
    "BusinessRuleErrorDto",
    "SystemErrorDto",
    "FieldErrorDto",
    "BatchErrorResponseDto",
    "RateLimitErrorDto",
    "AuthenticationErrorDto",
    "ConflictErrorDto",
    "NotFoundErrorDto",

    # Common Base Types
    "TimestampMixin",
    "UserContextMixin",
    "PaginationRequest",
    "PaginationResponse",
    "CommandStatus",
    "ValidationStatus",
    "Priority",
    "Currency",
    "MoneyDto",
    "AddressDto",
    "ContactDto",
    "MetadataDto",
    "ErrorDetailDto",
    "HealthCheckDto",
]