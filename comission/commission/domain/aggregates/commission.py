from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
from uuid import UUID, uuid4

from seedwork.domain.aggregate_root import AggregateRoot
from ..events.commission_calculated import CommissionCalculated


@dataclass
class Commission(AggregateRoot):
    """Commission Aggregate Root"""

    tracking_event_id: UUID
    partner_id: str
    campaign_id: str
    visitor_id: str
    interaction_type: str
    commission_amount: Decimal
    commission_rate: Decimal
    currency: str = "USD"
    commission_id: UUID = field(default_factory=uuid4)
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "calculated"

    @classmethod
    def calculate_commission(
        cls,
        tracking_event_id: UUID,
        partner_id: str,
        campaign_id: str,
        visitor_id: str,
        interaction_type: str,
    ) -> "Commission":
        """Factory method to create commission from tracking event"""

        # Get commission rate based on business rules
        commission_rate = cls._get_commission_rate(partner_id, interaction_type)

        # Calculate commission amount based on interaction type
        base_amount = cls._get_base_amount(interaction_type)
        commission_amount = base_amount * commission_rate

        commission = cls(
            tracking_event_id=tracking_event_id,
            partner_id=partner_id,
            campaign_id=campaign_id,
            visitor_id=visitor_id,
            interaction_type=interaction_type,
            commission_amount=commission_amount,
            commission_rate=commission_rate,
        )

        # Validate business rules
        if not cls._is_eligible_for_commission(interaction_type):
            commission.status = "rejected"
            commission.commission_amount = Decimal("0.00")

        # Publish domain event
        event = CommissionCalculated(
            commission_id=commission.commission_id,
            tracking_event_id=tracking_event_id,
            partner_id=partner_id,
            campaign_id=campaign_id,
            visitor_id=visitor_id,
            interaction_type=interaction_type,
            commission_amount=commission.commission_amount,
            commission_rate=commission.commission_rate,
            currency=commission.currency,
        )
        commission.add_domain_event(event)

        return commission

    @staticmethod
    def _get_commission_rate(partner_id: str, interaction_type: str) -> Decimal:
        """Business rule: calculate commission rate based on partner and interaction type"""

        # Default rates by interaction type
        base_rates = {
            "click": Decimal("0.10"),  # 10% commission for clicks
            "view": Decimal("0.05"),  # 5% commission for views
            "engagement": Decimal("0.15"),  # 15% commission for engagements
        }

        base_rate = base_rates.get(interaction_type, Decimal("0.05"))

        # Premium partners get higher rates
        premium_partners = ["partner_premium_1", "partner_premium_2"]
        if partner_id in premium_partners:
            return base_rate * Decimal("1.5")  # 50% bonus for premium partners

        return base_rate

    @staticmethod
    def _get_base_amount(interaction_type: str) -> Decimal:
        """Business rule: get base amount for commission calculation"""

        base_amounts = {
            "click": Decimal("2.00"),  # $2.00 base for clicks
            "view": Decimal("0.50"),  # $0.50 base for views
            "engagement": Decimal("5.00"),  # $5.00 base for engagements
        }

        return base_amounts.get(interaction_type, Decimal("1.00"))

    @staticmethod
    def _is_eligible_for_commission(interaction_type: str) -> bool:
        """Business rule: validate if interaction is eligible for commission"""
        eligible_types = ["click", "view", "engagement"]
        return interaction_type in eligible_types

    def apply_bonus(self, bonus_percentage: Decimal) -> None:
        """Apply bonus to commission amount"""
        if self.status == "calculated":
            bonus_amount = self.commission_amount * (bonus_percentage / Decimal("100"))
            self.commission_amount += bonus_amount

    def reject_commission(self, reason: str) -> None:
        """Reject commission with reason"""
        self.status = "rejected"
        self.commission_amount = Decimal("0.00")
