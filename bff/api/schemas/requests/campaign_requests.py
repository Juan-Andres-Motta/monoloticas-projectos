from pydantic import BaseModel
from typing import List
from decimal import Decimal
from enum import Enum


class PartnerType(str, Enum):
    AFFILIATE = "AFFILIATE"
    INFLUENCER = "INFLUENCER"
    CONTENT_CREATOR = "CONTENT_CREATOR"


class CommissionType(str, Enum):
    CPA = "CPA"
    CPL = "CPL"
    CPC = "CPC"


class AcceptanceTerms(BaseModel):
    commission_type: CommissionType
    commission_rate: Decimal
    cookie_duration_days: int
    promotional_methods: List[str]


class AcceptCampaignRequest(BaseModel):
    partner_id: str
    partner_type: PartnerType
    acceptance_terms: AcceptanceTerms
    estimated_monthly_reach: int