from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from seedwork.domain.domain_event import DomainEvent


@dataclass
class CommissionCalculated(DomainEvent):
    """Event published when commission is calculated"""

    commission_id: UUID = None
    tracking_event_id: UUID = None
    partner_id: str = None
    campaign_id: str = None
    visitor_id: str = None
    interaction_type: str = None
    commission_amount: Decimal = None
    commission_rate: Decimal = None
    currency: str = None

    def event_type(self) -> str:
        return "commission.calculated.v1"
