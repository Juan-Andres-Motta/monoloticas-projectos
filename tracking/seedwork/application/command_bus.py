from typing import Dict, Any
from .application_command import Command
from .command_handler import CommandHandler


class CommandBus:
    """Routes commands to appropriate handlers"""

    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}

    def register(self, command_name: str, handler: CommandHandler):
        self._handlers[command_name] = handler

    async def execute(self, command_name: str, command: Command) -> Any:
        if command_name not in self._handlers:
            raise ValueError(f"No handler registered for command: {command_name}")

        handler = self._handlers[command_name]
        return await handler.handle(command)
