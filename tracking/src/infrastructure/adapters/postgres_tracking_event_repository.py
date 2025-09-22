import logging
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import insert
from src.domain.entities.tracking_event import TrackingEvent
from src.domain.ports.tracking_event_repository import TrackingEventRepository
from .models import tracking_events_table

logger = logging.getLogger(__name__)


class PostgresTrackingEventRepository(TrackingEventRepository):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self.sessionmaker = sessionmaker

    async def save(self, tracking_event: TrackingEvent) -> int:
        logger.info(
            f"Saving tracking event to database for campaign: {tracking_event.campaign_id}, event: {tracking_event.event_type}"
        )
        session = self.sessionmaker()
        try:
            stmt = (
                insert(tracking_events_table)
                .values(
                    campaign_id=tracking_event.campaign_id,
                    event_type=tracking_event.event_type,
                    status=tracking_event.status,
                    timestamp=tracking_event.timestamp,
                )
                .returning(tracking_events_table.c.id)
            )
            result = await session.execute(stmt)
            tracking_id = result.scalar_one()
            await session.commit()
            logger.info(
                f"Tracking event saved successfully for campaign: {tracking_event.campaign_id} with id: {tracking_id}"
            )
            return tracking_id
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def update_status(self, tracking_id: int, status: str) -> None:
        logger.info(f"Updating status of tracking event {tracking_id} to {status}")
        session = self.sessionmaker()
        try:
            from sqlalchemy import update

            stmt = (
                update(tracking_events_table)
                .where(tracking_events_table.c.id == tracking_id)
                .values(status=status)
            )
            result = await session.execute(stmt)
            logger.info(
                f"Update statement executed for tracking_id {tracking_id}, rows affected: {result.rowcount}"
            )
            if result.rowcount == 0:
                logger.info(f"No tracking event found with id {tracking_id} to update")
            await session.commit()
            logger.info(f"Tracking event {tracking_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Failed to update status for tracking_id {tracking_id}: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
