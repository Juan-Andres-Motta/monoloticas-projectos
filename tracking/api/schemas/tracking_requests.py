from pydantic import BaseModel, Field


class RecordTrackingEventRequest(BaseModel):
    """HTTP request to record tracking event"""

    partner_id: str = Field(..., min_length=1, description="Partner identifier")
    campaign_id: str = Field(..., min_length=1, description="Campaign identifier")
    visitor_id: str = Field(..., min_length=1, description="Visitor identifier")
    interaction_type: str = Field(..., description="Type of interaction")
    source_url: str = Field(..., min_length=1, description="Source URL")
    destination_url: str = Field(..., min_length=1, description="Destination URL")
