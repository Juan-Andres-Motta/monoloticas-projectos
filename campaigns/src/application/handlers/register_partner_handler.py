import logging
from src.application.commands.register_partner_command import RegisterPartnerCommand
from src.domain.ports.partner_repository import PartnerRepository

logger = logging.getLogger(__name__)


class RegisterPartnerHandler:
    def __init__(self, partner_repository: PartnerRepository):
        self.partner_repository = partner_repository

    async def handle(self, command: RegisterPartnerCommand) -> None:
        logger.info(
            f"Handling RegisterPartnerCommand for partner_id: {command.partner.partner_id}"
        )
        await self.partner_repository.save(command.partner)
        logger.info(f"Successfully registered partner: {command.partner.partner_id}")
