from pydantic import BaseModel
from uuid import UUID


class RecordTrackingEventResponse(BaseModel):
    """HTTP response after recording tracking event"""

    tracking_event_id: UUID
    status: str
    message: str
    processing_time_ms: float
