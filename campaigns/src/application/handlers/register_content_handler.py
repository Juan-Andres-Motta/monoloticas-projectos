import logging
from src.application.commands.register_content_command import RegisterContentCommand
from src.domain.ports.content_repository import ContentRepository

logger = logging.getLogger(__name__)


class RegisterContentHandler:
    def __init__(self, content_repository: ContentRepository):
        self.content_repository = content_repository

    async def handle(self, command: RegisterContentCommand) -> None:
        logger.info(
            f"Handling RegisterContentCommand for content: {command.content.content_id}"
        )
        await self.content_repository.save(command.content)
        logger.info(f"Content registered successfully: {command.content.content_id}")
