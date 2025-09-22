from src.domain.entities.tracking_event import TrackingEvent


class RegisterTrackingEventCommand:
    def __init__(self, tracking_event: TrackingEvent):
        self.tracking_event = tracking_event
