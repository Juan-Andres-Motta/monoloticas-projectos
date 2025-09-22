from abc import ABC, abstractmethod
from datetime import datetime


class ProcessedMessageRepository(ABC):
    @abstractmethod
    async def is_processed(self, message_id: str) -> bool:
        pass

    @abstractmethod
    async def mark_processed(self, message_id: str) -> None:
        pass
