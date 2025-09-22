import uuid
from pydantic import BaseModel, Field


class Content(BaseModel):
    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    content_url: str
