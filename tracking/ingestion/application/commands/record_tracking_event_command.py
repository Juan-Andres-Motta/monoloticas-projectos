from dataclasses import dataclass
from seedwork.application.application_command import Command


@dataclass
class RecordTrackingEventCommand(Command):
    """Command to record a new tracking event"""

    partner_id: str
    campaign_id: str
    visitor_id: str
    interaction_type: str
    source_url: str
    destination_url: str
