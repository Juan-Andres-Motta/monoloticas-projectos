from dataclasses import dataclass
from uuid import UUID
from seedwork.application.application_command import Command


@dataclass
class CalculateCommissionCommand(Command):
    """Command to calculate commission from tracking event"""

    tracking_event_id: UUID
    partner_id: str
    campaign_id: str
    visitor_id: str
    interaction_type: str
