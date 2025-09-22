from abc import ABC, abstractmethod
from src.domain.entities.commission import Commission


class CommissionRepository(ABC):
    @abstractmethod
    async def save(self, commission: Commission) -> None:
        pass
