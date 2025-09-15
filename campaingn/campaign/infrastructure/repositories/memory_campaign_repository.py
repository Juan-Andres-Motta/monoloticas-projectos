"""
In-Memory Campaign Repository Implementation
"""

from uuid import UUID
from typing import Optional, Dict

from campaign.domain.aggregates.campaign import Campaign
from campaign.domain.repositories.campaign_repository import CampaignRepository


class MemoryCampaignRepository(CampaignRepository):
    """In-memory implementation of campaign repository for testing/demo"""

    def __init__(self):
        self._campaigns: Dict[UUID, Campaign] = {}

    async def save(self, campaign: Campaign) -> None:
        """Save a campaign aggregate"""
        self._campaigns[campaign.id] = campaign
        print(f"💾 Campaign saved: {campaign.id}")

    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign by ID"""
        campaign = self._campaigns.get(campaign_id)
        print(
            f"🔍 Campaign lookup for {campaign_id}: {'Found' if campaign else 'Not found'}"
        )
        return campaign

    async def get_by_name(self, name: str) -> Optional[Campaign]:
        """Get campaign by name"""
        for campaign in self._campaigns.values():
            if campaign.name == name:
                return campaign
        return None

    async def exists(self, campaign_id: UUID) -> bool:
        """Check if campaign exists"""
        return campaign_id in self._campaigns

    async def delete(self, campaign_id: UUID) -> None:
        """Delete campaign"""
        if campaign_id in self._campaigns:
            del self._campaigns[campaign_id]
            print(f"🗑️ Campaign deleted: {campaign_id}")

    def get_all(self) -> Dict[UUID, Campaign]:
        """Get all campaigns (for debugging)"""
        return self._campaigns.copy()

    def count(self) -> int:
        """Get total number of campaigns"""
        return len(self._campaigns)
