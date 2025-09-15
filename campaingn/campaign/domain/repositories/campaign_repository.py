"""
Campaign Repository Interface
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from ..aggregates.campaign import Campaign


class CampaignRepository(ABC):
    """Repository interface for campaign aggregate"""

    @abstractmethod
    async def save(self, campaign: Campaign) -> None:
        """Save a campaign aggregate"""
        pass

    @abstractmethod
    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign by ID"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Campaign]:
        """Get campaign by name"""
        pass

    @abstractmethod
    async def exists(self, campaign_id: UUID) -> bool:
        """Check if campaign exists"""
        pass

    @abstractmethod
    async def delete(self, campaign_id: UUID) -> None:
        """Delete campaign"""
        pass
