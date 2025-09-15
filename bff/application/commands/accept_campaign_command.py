from dataclasses import dataclass
from decimal import Decimal
from typing import List
from enum import Enum


class PartnerType(str, Enum):
    AFFILIATE = "AFFILIATE"
    INFLUENCER = "INFLUENCER"
    CONTENT_CREATOR = "CONTENT_CREATOR"


class CommissionType(str, Enum):
    CPA = "CPA"
    CPL = "CPL"
    CPC = "CPC"


@dataclass
class AcceptanceTerms:
    commission_type: CommissionType
    commission_rate: Decimal
    cookie_duration_days: int
    promotional_methods: List[str]


@dataclass
class AcceptCampaignCommand:
    campaign_id: str
    partner_id: str
    partner_type: PartnerType
    acceptance_terms: AcceptanceTerms
    estimated_monthly_reach: int