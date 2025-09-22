import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.domain.entities.campaign import Campaign
from src.domain.ports.campaign_repository import CampaignRepository
from .models import campaigns_table

logger = logging.getLogger(__name__)


class PostgresCampaignRepository(CampaignRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, campaign: Campaign) -> None:
        try:
            logger.info(f"Saving campaign to database: {campaign.campaign_id}")
            stmt = insert(campaigns_table).values(
                campaign_id=campaign.campaign_id, name=campaign.name
            )
            result = await self.session.execute(stmt)
            logger.info(
                f"Executed insert statement for campaign: {campaign.campaign_id}"
            )
            await self.session.commit()
            logger.info(f"Committed transaction for campaign: {campaign.campaign_id}")
            logger.info(f"Campaign saved successfully: {campaign.campaign_id}")
        except Exception as e:
            logger.error(f"Failed to save campaign {campaign.campaign_id}: {e}")
            await self.session.rollback()
            raise
