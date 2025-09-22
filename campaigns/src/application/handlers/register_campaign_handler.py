import logging
from src.application.commands.register_campaign_command import RegisterCampaignCommand
from src.domain.ports.campaign_repository import CampaignRepository

logger = logging.getLogger(__name__)


class RegisterCampaignHandler:
    def __init__(self, campaign_repository: CampaignRepository):
        self.campaign_repository = campaign_repository

    async def handle(self, command: RegisterCampaignCommand) -> None:
        logger.info(
            f"Handling RegisterCampaignCommand for campaign: {command.campaign.campaign_id}"
        )
        await self.campaign_repository.save(command.campaign)
        logger.info(f"Campaign registered successfully: {command.campaign.campaign_id}")
