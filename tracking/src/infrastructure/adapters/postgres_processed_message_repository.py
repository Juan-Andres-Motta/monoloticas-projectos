import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import insert, select
from src.domain.ports.processed_message_repository import ProcessedMessageRepository
from .models import processed_messages_table

logger = logging.getLogger(__name__)


class PostgresProcessedMessageRepository(ProcessedMessageRepository):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self.sessionmaker = sessionmaker

    async def is_processed(self, message_id: str) -> bool:
        session = self.sessionmaker()
        try:
            stmt = select(processed_messages_table).where(
                processed_messages_table.c.message_id == message_id
            )
            result = await session.execute(stmt)
            row = result.first()
            return row is not None
        finally:
            await session.close()

    async def mark_processed(self, message_id: str) -> None:
        session = self.sessionmaker()
        try:
            stmt = insert(processed_messages_table).values(
                message_id=message_id,
                processed_at=datetime.utcnow(),
            )
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Message {message_id} marked as processed")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to mark message {message_id} as processed: {e}")
            raise
        finally:
            await session.close()
