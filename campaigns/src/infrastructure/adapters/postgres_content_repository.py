import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.domain.entities.content import Content
from src.domain.ports.content_repository import ContentRepository
from .models import contents_table

logger = logging.getLogger(__name__)


class PostgresContentRepository(ContentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, content: Content) -> None:
        try:
            logger.info(f"Saving content to database: {content.content_id}")
            stmt = insert(contents_table).values(
                content_id=content.content_id,
                campaign_id=content.campaign_id,
                content_url=content.content_url,
            )
            result = await self.session.execute(stmt)
            logger.info(f"Executed insert statement for content: {content.content_id}")
            await self.session.commit()
            logger.info(f"Committed transaction for content: {content.content_id}")
            logger.info(f"Content saved successfully: {content.content_id}")
        except Exception as e:
            logger.error(f"Failed to save content {content.content_id}: {e}")
            await self.session.rollback()
            raise
