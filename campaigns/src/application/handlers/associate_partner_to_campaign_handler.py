import logging
from src.application.commands.associate_partner_to_campaign_command import (
    AssociatePartnerToCampaignCommand,
)
from src.domain.ports.campaign_partner_repository import CampaignPartnerRepository

logger = logging.getLogger(__name__)


class AssociatePartnerToCampaignHandler:
    def __init__(self, campaign_partner_repository: CampaignPartnerRepository):
        self.campaign_partner_repository = campaign_partner_repository

    async def handle(self, command: AssociatePartnerToCampaignCommand) -> None:
        logger.info(
            f"Handling AssociatePartnerToCampaignCommand for campaign: {command.campaign_partner.campaign_id}, partner: {command.campaign_partner.partner_id}"
        )
        await self.campaign_partner_repository.save(command.campaign_partner)
        logger.info(
            f"Partner associated to campaign successfully: {command.campaign_partner.partner_id} -> {command.campaign_partner.campaign_id}"
        )
