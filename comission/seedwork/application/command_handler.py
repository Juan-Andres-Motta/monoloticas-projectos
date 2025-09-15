from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from .application_command import Command

CommandType = TypeVar("CommandType", bound=Command)
ResultType = TypeVar("ResultType")


class CommandHandler(ABC, Generic[CommandType, ResultType]):
    """Base class for command handlers"""

    @abstractmethod
    async def handle(self, command: CommandType) -> ResultType:
        """Handle the command"""
        pass
