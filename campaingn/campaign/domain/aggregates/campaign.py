"""
Campaign Aggregate Root
Domain logic for campaign management and partner acceptance
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Dict, Any
from enum import Enum

from ..events.campaign_events import CampaignCreated, CampaignAccepted, VideoAdded
from ...seedwork.domain.aggregates import AggregateRoot


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PartnerType(str, Enum):
    INFLUENCER = "influencer"
    AFFILIATE = "affiliate"
    BRAND_AMBASSADOR = "brand_ambassador"


class CommissionType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    HYBRID = "hybrid"


class AcceptanceTerms:
    """Value object for campaign acceptance terms"""

    def __init__(
        self,
        commission_type: CommissionType,
        commission_rate: float,
        cookie_duration_days: int,
        promotional_methods: List[str],
    ):
        self.commission_type = commission_type
        self.commission_rate = commission_rate
        self.cookie_duration_days = cookie_duration_days
        self.promotional_methods = promotional_methods

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commission_type": self.commission_type.value,
            "commission_rate": self.commission_rate,
            "cookie_duration_days": self.cookie_duration_days,
            "promotional_methods": self.promotional_methods,
        }


class Campaign(AggregateRoot):
    """Campaign aggregate root"""

    def __init__(self, campaign_id: UUID, name: str, description: str = ""):
        super().__init__(campaign_id)
        self._name = name
        self._description = description
        self._status = CampaignStatus.DRAFT
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._video_urls: List[str] = []
        self._accepted_partners: Dict[str, Dict[str, Any]] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def status(self) -> CampaignStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def video_urls(self) -> List[str]:
        return self._video_urls.copy()

    @property
    def accepted_partners(self) -> Dict[str, Dict[str, Any]]:
        return self._accepted_partners.copy()

    @classmethod
    def create(cls, campaign_id: UUID, name: str, description: str = "") -> "Campaign":
        """Create a new campaign"""
        campaign = cls(campaign_id, name, description)

        # Add domain event
        campaign.add_event(
            CampaignCreated(
                aggregate_id=campaign_id,
                campaign_id=campaign_id,
                name=name,
                description=description,
                status=CampaignStatus.DRAFT.value,
                created_at=campaign._created_at,
            )
        )

        return campaign

    def accept_partner(
        self,
        partner_id: str,
        partner_type: PartnerType,
        acceptance_terms: AcceptanceTerms,
        estimated_monthly_reach: int,
        user_id: str,
    ) -> None:
        """Accept a partner for this campaign"""

        if partner_id in self._accepted_partners:
            raise ValueError(
                f"Partner {partner_id} has already been accepted for campaign {self.id}"
            )

        # Store partner acceptance details
        partner_data = {
            "partner_id": partner_id,
            "partner_type": partner_type.value,
            "acceptance_terms": acceptance_terms.to_dict(),
            "estimated_monthly_reach": estimated_monthly_reach,
            "accepted_at": datetime.utcnow(),
            "accepted_by": user_id,
        }

        self._accepted_partners[partner_id] = partner_data
        self._updated_at = datetime.utcnow()

        # If this is the first partner, activate the campaign
        if len(self._accepted_partners) == 1 and self._status == CampaignStatus.DRAFT:
            self._status = CampaignStatus.ACTIVE

        # Add domain event
        self.add_event(
            CampaignAccepted(
                aggregate_id=self.id,
                campaign_id=self.id,
                partner_id=partner_id,
                partner_type=partner_type.value,
                acceptance_terms=acceptance_terms.to_dict(),
                estimated_monthly_reach=estimated_monthly_reach,
                accepted_by=user_id,
                accepted_at=datetime.utcnow(),
            )
        )

    def add_video_url(self, video_url: str, added_by: str) -> None:
        """Add a video URL to the campaign"""

        if video_url in self._video_urls:
            raise ValueError(
                f"Video URL {video_url} already exists in campaign {self.id}"
            )

        self._video_urls.append(video_url)
        self._updated_at = datetime.utcnow()

        # Add domain event
        self.add_event(
            VideoAdded(
                aggregate_id=self.id,
                campaign_id=self.id,
                video_url=video_url,
                added_by=added_by,
                added_at=datetime.utcnow(),
            )
        )

    def activate(self) -> None:
        """Activate the campaign"""
        if self._status != CampaignStatus.DRAFT:
            raise ValueError(f"Cannot activate campaign in {self._status.value} status")

        self._status = CampaignStatus.ACTIVE
        self._updated_at = datetime.utcnow()

    def pause(self) -> None:
        """Pause the campaign"""
        if self._status != CampaignStatus.ACTIVE:
            raise ValueError(f"Cannot pause campaign in {self._status.value} status")

        self._status = CampaignStatus.PAUSED
        self._updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Complete the campaign"""
        if self._status not in [CampaignStatus.ACTIVE, CampaignStatus.PAUSED]:
            raise ValueError(f"Cannot complete campaign in {self._status.value} status")

        self._status = CampaignStatus.COMPLETED
        self._updated_at = datetime.utcnow()

    def get_partner_acceptance(self, partner_id: str) -> Dict[str, Any]:
        """Get partner acceptance details"""
        if partner_id not in self._accepted_partners:
            raise ValueError(f"Partner {partner_id} not found in campaign {self.id}")

        return self._accepted_partners[partner_id].copy()

    def is_partner_accepted(self, partner_id: str) -> bool:
        """Check if a partner has been accepted"""
        return partner_id in self._accepted_partners

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": str(self.id),
            "name": self._name,
            "description": self._description,
            "status": self._status.value,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "video_urls": self._video_urls,
            "accepted_partners": self._accepted_partners,
        }
