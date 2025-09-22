import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.domain.entities.campaign_partner import CampaignPartner
from src.domain.ports.campaign_partner_repository import CampaignPartnerRepository
from .models import campaign_partners_table

logger = logging.getLogger(__name__)


class PostgresCampaignPartnerRepository(CampaignPartnerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, campaign_partner: CampaignPartner) -> None:
        try:
            logger.info(
                f"Saving campaign-partner association: {campaign_partner.campaign_id} - {campaign_partner.partner_id}"
            )
            stmt = insert(campaign_partners_table).values(
                campaign_id=campaign_partner.campaign_id,
                partner_id=campaign_partner.partner_id,
            )
            result = await self.session.execute(stmt)
            logger.info(f"Executed insert statement for campaign-partner association")
            await self.session.commit()
            logger.info(f"Committed transaction for campaign-partner association")
            logger.info(f"Campaign-partner association saved successfully")
        except Exception as e:
            logger.error(f"Failed to save campaign-partner association: {e}")
            await self.session.rollback()
            raise
