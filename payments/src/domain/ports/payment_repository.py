from abc import ABC, abstractmethod
from src.domain.entities.payment import Payment


class PaymentRepository(ABC):
    @abstractmethod
    async def save(self, payment: Payment) -> None:
        pass
