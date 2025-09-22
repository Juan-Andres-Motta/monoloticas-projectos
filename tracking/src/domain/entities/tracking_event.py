from pydantic import BaseModel
from datetime import datetime


class TrackingEvent(BaseModel):
    id: int | None = None
    campaign_id: str
    event_type: str  # e.g., "click"
    status: str = "success"
    timestamp: datetime = datetime.utcnow()
