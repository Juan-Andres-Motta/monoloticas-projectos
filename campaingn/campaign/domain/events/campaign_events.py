"""
Campaign Domain Events
Events that occur within the campaign domain
"""

from datetime import datetime
from uuid import UUID
from typing import Dict, Any, List

from ...seedwork.domain.events import DomainEvent


class CampaignCreated(DomainEvent):
    """Event raised when a new campaign is created"""

    def __init__(
        self,
        aggregate_id: UUID,
        campaign_id: UUID,
        name: str,
        description: str,
        status: str,
        created_at: datetime,
    ):
        super().__init__(aggregate_id)
        self.campaign_id = campaign_id
        self.name = name
        self.description = description
        self.status = status
        self.created_at = created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": "CampaignCreated",
            "aggregate_id": str(self.aggregate_id),
            "campaign_id": str(self.campaign_id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "occurred_on": self.occurred_on.isoformat(),
        }


class CampaignAccepted(DomainEvent):
    """Event raised when a partner accepts a campaign"""

    def __init__(
        self,
        aggregate_id: UUID,
        campaign_id: UUID,
        partner_id: str,
        partner_type: str,
        acceptance_terms: Dict[str, Any],
        estimated_monthly_reach: int,
        accepted_by: str,
        accepted_at: datetime,
    ):
        super().__init__(aggregate_id)
        self.campaign_id = campaign_id
        self.partner_id = partner_id
        self.partner_type = partner_type
        self.acceptance_terms = acceptance_terms
        self.estimated_monthly_reach = estimated_monthly_reach
        self.accepted_by = accepted_by
        self.accepted_at = accepted_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": "CampaignAccepted",
            "aggregate_id": str(self.aggregate_id),
            "campaign_id": str(self.campaign_id),
            "partner_id": self.partner_id,
            "partner_type": self.partner_type,
            "acceptance_terms": self.acceptance_terms,
            "estimated_monthly_reach": self.estimated_monthly_reach,
            "accepted_by": self.accepted_by,
            "accepted_at": self.accepted_at.isoformat(),
            "occurred_on": self.occurred_on.isoformat(),
        }


class VideoAdded(DomainEvent):
    """Event raised when a video URL is added to a campaign"""

    def __init__(
        self,
        aggregate_id: UUID,
        campaign_id: UUID,
        video_url: str,
        added_by: str,
        added_at: datetime,
    ):
        super().__init__(aggregate_id)
        self.campaign_id = campaign_id
        self.video_url = video_url
        self.added_by = added_by
        self.added_at = added_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": "VideoAdded",
            "aggregate_id": str(self.aggregate_id),
            "campaign_id": str(self.campaign_id),
            "video_url": self.video_url,
            "added_by": self.added_by,
            "added_at": self.added_at.isoformat(),
            "occurred_on": self.occurred_on.isoformat(),
        }


class CampaignStatusChanged(DomainEvent):
    """Event raised when campaign status changes"""

    def __init__(
        self,
        aggregate_id: UUID,
        campaign_id: UUID,
        old_status: str,
        new_status: str,
        changed_by: str,
        changed_at: datetime,
    ):
        super().__init__(aggregate_id)
        self.campaign_id = campaign_id
        self.old_status = old_status
        self.new_status = new_status
        self.changed_by = changed_by
        self.changed_at = changed_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": "CampaignStatusChanged",
            "aggregate_id": str(self.aggregate_id),
            "campaign_id": str(self.campaign_id),
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat(),
            "occurred_on": self.occurred_on.isoformat(),
        }
