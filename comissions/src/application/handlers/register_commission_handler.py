import logging
from src.application.commands.register_commission_command import (
    RegisterCommissionCommand,
)
from src.domain.ports.commission_repository import CommissionRepository

logger = logging.getLogger(__name__)


class RegisterCommissionHandler:
    def __init__(self, commission_repository: CommissionRepository):
        self.commission_repository = commission_repository

    async def handle(self, command: RegisterCommissionCommand) -> None:
        logger.info(
            f"Handling RegisterCommissionCommand for partner: {command.commission.partner_id}, campaign: {command.commission.campaign_id}"
        )
        await self.commission_repository.save(command.commission)
        logger.info(
            f"Commission registered successfully for partner: {command.commission.partner_id}"
        )
