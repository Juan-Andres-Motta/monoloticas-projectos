from pydantic import BaseModel


class FailTrackingEventCommand(BaseModel):
    tracking_id: int
