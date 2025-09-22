from abc import ABC, abstractmethod
from src.domain.entities.saga_log import SagaLog


class SagaLogRepository(ABC):
    @abstractmethod
    async def save(self, saga_log: SagaLog) -> int:
        pass

    @abstractmethod
    async def get_by_saga_id(self, saga_id: str) -> list[SagaLog]:
        pass

    @abstractmethod
    async def update_status(self, saga_id: str, step: str, status: str) -> None:
        pass
