from pydantic import BaseModel
from datetime import datetime


class Commission(BaseModel):
    amount: float
    partner_id: str
    campaign_id: str
    commission_type: str  # e.g., "CPA", "CPC"
    tracking_id: str
    status: str = "success"
    created_at: datetime = datetime.utcnow()
