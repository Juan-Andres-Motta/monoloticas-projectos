from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class TimestampMixin(BaseModel):
    """Mixin for timestamps"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class MetadataDto(BaseModel):
    """Generic metadata container"""
    tags: list[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    source: Optional[str] = None
    version: str = Field(default="v1")


class EventSeverity(str, Enum):
    """Event severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventCategory(str, Enum):
    """Event categories for classification"""
    CAMPAIGN = "CAMPAIGN"
    EVIDENCE = "EVIDENCE"
    PAYMENT = "PAYMENT"
    PARTNER = "PARTNER"
    SYSTEM = "SYSTEM"
    COMPLIANCE = "COMPLIANCE"
    PERFORMANCE = "PERFORMANCE"


class AuditAction(str, Enum):
    """Audit trail actions"""
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class BaseIntegrationEventDto(BaseModel, TimestampMixin):
    """Base integration event structure for cross-service communication"""

    # Event identification
    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    event_type: str = Field(..., description="Type of integration event")
    event_version: str = Field(default="v1", description="Event schema version")

    # Event context
    aggregate_id: str = Field(..., description="Identifier of the aggregate that generated this event")
    aggregate_type: str = Field(..., description="Type of aggregate")
    user_id: Optional[str] = Field(None, description="User who triggered the event")

    # Event metadata
    event_category: EventCategory = Field(..., description="Event category")
    severity: EventSeverity = Field(default=EventSeverity.MEDIUM, description="Event severity")
    correlation_id: Optional[UUID] = Field(None, description="Correlation ID for tracing")
    causation_id: Optional[UUID] = Field(None, description="ID of the command that caused this event")

    # Timing
    occurred_at: datetime = Field(default_factory=datetime.utcnow, description="When the event occurred")

    # Additional data
    metadata: Optional[MetadataDto] = Field(None, description="Additional metadata")

    class Config:
        schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_type": "campaign.accepted.v1",
                "aggregate_id": "camp_winter_sale_2025",
                "aggregate_type": "Campaign",
                "user_id": "user_123",
                "event_category": "CAMPAIGN",
                "severity": "MEDIUM"
            }
        }


class CampaignAcceptedEventDto(BaseIntegrationEventDto):
    """Event emitted when a campaign is accepted"""
    event_type: str = Field(default="campaign.accepted.v1", description="Event type")
    event_category: EventCategory = Field(default=EventCategory.CAMPAIGN, description="Event category")

    # Event payload
    campaign_id: str = Field(..., description="Campaign identifier")
    partner_id: str = Field(..., description="Partner identifier")
    enrollment_id: str = Field(..., description="Enrollment identifier")
    contract_id: str = Field(..., description="Contract identifier")

    # Campaign details
    commission_rate: float = Field(..., description="Agreed commission rate")
    commission_type: str = Field(..., description="Type of commission")
    start_date: datetime = Field(..., description="Campaign start date")
    end_date: datetime = Field(..., description="Campaign end date")

    # Additional context
    auto_approved: bool = Field(default=False, description="Whether acceptance was auto-approved")
    approval_criteria_met: Dict[str, bool] = Field(default_factory=dict, description="Approval criteria status")


class EvidenceUploadedEventDto(BaseIntegrationEventDto):
    """Integration event emitted when evidence is uploaded"""
    event_type: str = Field(default="evidence.uploaded.v1", description="Event type")
    event_category: EventCategory = Field(default=EventCategory.EVIDENCE, description="Event category")

    # Event payload
    evidence_id: str = Field(..., description="Evidence identifier")
    campaign_id: str = Field(..., description="Campaign identifier")
    partner_id: str = Field(..., description="Partner identifier")

    # Evidence details
    evidence_type: str = Field(..., description="Type of evidence")
    platform: str = Field(..., description="Platform where content was posted")
    content_url: str = Field(..., description="URL of the content")

    # Metrics
    estimated_reach: Optional[int] = Field(None, description="Estimated audience reach")
    engagement_score: Optional[float] = Field(None, description="Engagement quality score")

    # Compliance
    requires_review: bool = Field(default=True, description="Whether manual review is required")
    compliance_flags: Dict[str, bool] = Field(default_factory=dict, description="Compliance check results")


class PaymentRequestedEventDto(BaseIntegrationEventDto):
    """Integration event emitted when payment is requested"""
    event_type: str = Field(default="payment.requested.v1", description="Event type")
    event_category: EventCategory = Field(default=EventCategory.PAYMENT, description="Event category")

    # Event payload
    payment_request_id: str = Field(..., description="Payment request identifier")
    partner_id: str = Field(..., description="Partner identifier")

    # Payment details
    requested_amount: float = Field(..., description="Requested payment amount")
    currency: str = Field(..., description="Payment currency")
    payment_method: str = Field(..., description="Requested payment method")
    request_type: str = Field(..., description="Type of payment request")

    # Period details
    commission_period_start: datetime = Field(..., description="Commission period start")
    commission_period_end: datetime = Field(..., description="Commission period end")
    included_campaigns: list[str] = Field(..., description="Campaigns included in request")

    # Processing flags
    auto_approve_eligible: bool = Field(default=False, description="Eligible for auto-approval")
    priority_processing: bool = Field(default=False, description="Requires priority processing")


class SystemAlertEventDto(BaseIntegrationEventDto):
    """Integration event for system alerts and notifications"""
    event_type: str = Field(default="system.alert.v1", description="Event type")
    event_category: EventCategory = Field(default=EventCategory.SYSTEM, description="Event category")

    # Alert details
    alert_type: str = Field(..., description="Type of system alert")
    alert_message: str = Field(..., description="Alert message")
    component: str = Field(..., description="System component generating alert")

    # Alert context
    error_code: Optional[str] = Field(None, description="Associated error code")
    affected_users: list[str] = Field(default_factory=list, description="Users affected by the alert")
    resolution_required: bool = Field(default=True, description="Whether resolution action is required")

    # Additional details
    alert_data: Dict[str, Any] = Field(default_factory=dict, description="Additional alert data")


class ComplianceViolationEventDto(BaseIntegrationEventDto):
    """Integration event emitted when compliance violation is detected"""
    event_type: str = Field(default="compliance.violation.v1", description="Event type")
    event_category: EventCategory = Field(default=EventCategory.COMPLIANCE, description="Event category")
    severity: EventSeverity = Field(default=EventSeverity.HIGH, description="Event severity")

    # Violation details
    violation_type: str = Field(..., description="Type of compliance violation")
    violation_description: str = Field(..., description="Description of the violation")
    affected_resource_id: str = Field(..., description="ID of the affected resource")
    affected_resource_type: str = Field(..., description="Type of affected resource")

    # Detection details
    detection_method: str = Field(..., description="How the violation was detected")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Detection confidence score")

    # Required actions
    immediate_action_required: bool = Field(default=True, description="Whether immediate action is required")
    suggested_actions: list[str] = Field(default_factory=list, description="Suggested remediation actions")

    # Violation context
    violation_data: Dict[str, Any] = Field(default_factory=dict, description="Additional violation data")


class PerformanceThresholdEventDto(BaseIntegrationEventDto):
    """Integration event emitted when performance thresholds are crossed"""
    event_type: str = Field(default="performance.threshold.v1", description="Event type")
    event_category: EventCategory = Field(default=EventCategory.PERFORMANCE, description="Event category")

    # Threshold details
    metric_name: str = Field(..., description="Name of the performance metric")
    threshold_type: str = Field(..., description="Type of threshold (e.g., 'minimum', 'maximum')")
    threshold_value: float = Field(..., description="The threshold value")
    actual_value: float = Field(..., description="The actual measured value")

    # Context
    measurement_period: str = Field(..., description="Time period for the measurement")
    affected_entity_id: str = Field(..., description="ID of the entity being measured")
    affected_entity_type: str = Field(..., description="Type of entity being measured")

    # Impact assessment
    impact_level: str = Field(..., description="Level of impact from threshold crossing")
    automated_actions_taken: list[str] = Field(default_factory=list, description="Automated actions triggered")
    manual_review_required: bool = Field(default=True, description="Whether manual review is needed")


class AuditTrailEventDto(BaseIntegrationEventDto):
    """Integration event for audit trail logging"""
    event_type: str = Field(default="audit.action.v1", description="Event type")
    event_category: EventCategory = Field(default=EventCategory.SYSTEM, description="Event category")

    # Audit details
    action: AuditAction = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource acted upon")
    resource_id: str = Field(..., description="ID of resource acted upon")

    # Change details
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values (for updates)")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values (for updates)")

    # Context
    ip_address: Optional[str] = Field(None, description="IP address of the actor")
    user_agent: Optional[str] = Field(None, description="User agent string")
    session_id: Optional[str] = Field(None, description="Session identifier")

    # Additional context
    business_justification: Optional[str] = Field(None, description="Business justification for the action")
    audit_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional audit metadata")