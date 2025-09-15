from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any

from .application_command import Command

TCommand = TypeVar("TCommand", bound=Command)
TResult = TypeVar("TResult")


class CommandHandler(ABC, Generic[TCommand, TResult]):
    """Base command handler for CQRS"""

    @abstractmethod
    async def handle(self, command: TCommand) -> TResult:
        pass
