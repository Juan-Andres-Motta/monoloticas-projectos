from pydantic import BaseModel
from typing import List


class AcceptanceTerms(BaseModel):
    commission_type: str
    commission_rate: float
    cookie_duration_days: int
    promotional_methods: List[str]


class Partner(BaseModel):
    partner_id: str
    partner_type: str
    acceptance_terms: AcceptanceTerms
    estimated_monthly_reach: int
