from abc import ABC, abstractmethod
from src.domain.entities.content import Content


class ContentRepository(ABC):
    @abstractmethod
    async def save(self, content: Content) -> None:
        pass
