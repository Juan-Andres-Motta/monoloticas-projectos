from typing import Dict, Any
from .application_command import Command
from .command_handler import CommandHandler


class CommandBus:
    """Command bus implementation"""

    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}

    def register(self, command_name: str, handler: CommandHandler) -> None:
        """Register a command handler"""
        self._handlers[command_name] = handler

    async def execute(self, command_name: str, command: Command) -> Any:
        """Execute a command"""
        handler = self._handlers.get(command_name)
        if not handler:
            raise ValueError(f"No handler registered for command: {command_name}")

        return await handler.handle(command)
