from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional


class CalculateCommissionRequest(BaseModel):
    """Request schema for commission calculation"""

    tracking_event_id: UUID
    partner_id: str
    campaign_id: str
    visitor_id: str
    interaction_type: str


class CommissionResponse(BaseModel):
    """Response schema for commission data"""

    commission_id: UUID
    tracking_event_id: UUID
    partner_id: str
    campaign_id: str
    visitor_id: str
    interaction_type: str
    commission_amount: Decimal
    commission_rate: Decimal
    currency: str
    status: str
    calculated_at: datetime


class CalculateCommissionResponse(BaseModel):
    """Response schema for commission calculation"""

    commission_id: UUID
    status: str
    message: str
    processing_time_ms: float


class CommissionListResponse(BaseModel):
    """Response schema for commission list"""

    commissions: list[CommissionResponse]
    total_count: int
    page: int
    page_size: int
