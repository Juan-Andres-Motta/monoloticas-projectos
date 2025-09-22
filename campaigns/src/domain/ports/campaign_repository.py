from abc import ABC, abstractmethod
from src.domain.entities.campaign import Campaign


class CampaignRepository(ABC):
    @abstractmethod
    async def save(self, campaign: Campaign) -> None:
        pass
