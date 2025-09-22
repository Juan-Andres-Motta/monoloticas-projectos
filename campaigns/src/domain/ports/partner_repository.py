from abc import ABC, abstractmethod
from src.domain.entities.partner import Partner


class PartnerRepository(ABC):
    @abstractmethod
    async def save(self, partner: Partner) -> None:
        pass
