from abc import ABC, abstractmethod
from src.domain.entities.campaign_partner import CampaignPartner


class CampaignPartnerRepository(ABC):
    @abstractmethod
    async def save(self, campaign_partner: CampaignPartner) -> None:
        pass
