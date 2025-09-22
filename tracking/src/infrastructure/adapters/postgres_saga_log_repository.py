import logging
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import insert, select, update
from src.domain.entities.saga_log import SagaLog
from src.domain.ports.saga_log_repository import SagaLogRepository
from .models import saga_logs_table

logger = logging.getLogger(__name__)


class PostgresSagaLogRepository(SagaLogRepository):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self.sessionmaker = sessionmaker

    async def save(self, saga_log: SagaLog) -> int:
        logger.info(
            f"Saving saga log for saga_id: {saga_log.saga_id}, step: {saga_log.step}"
        )
        session = self.sessionmaker()
        try:
            stmt = (
                insert(saga_logs_table)
                .values(
                    saga_id=saga_log.saga_id,
                    step=saga_log.step,
                    status=saga_log.status,
                    timestamp=saga_log.timestamp,
                    details=saga_log.details,
                )
                .returning(saga_logs_table.c.id)
            )
            result = await session.execute(stmt)
            log_id = result.scalar_one()
            await session.commit()
            logger.info(
                f"Saga log saved successfully for saga_id: {saga_log.saga_id} with id: {log_id}"
            )
            return log_id
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def get_by_saga_id(self, saga_id: str) -> list[SagaLog]:
        logger.info(f"Retrieving saga logs for saga_id: {saga_id}")
        session = self.sessionmaker()
        try:
            stmt = select(saga_logs_table).where(saga_logs_table.c.saga_id == saga_id)
            result = await session.execute(stmt)
            rows = result.fetchall()
            logs = [
                SagaLog(
                    id=row.id,
                    saga_id=row.saga_id,
                    step=row.step,
                    status=row.status,
                    timestamp=row.timestamp,
                    details=row.details,
                )
                for row in rows
            ]
            logger.info(f"Retrieved {len(logs)} saga logs for saga_id: {saga_id}")
            return logs
        finally:
            await session.close()

    async def update_status(self, saga_id: str, step: str, status: str) -> None:
        logger.info(f"Updating status for saga_id: {saga_id}, step: {step} to {status}")
        session = self.sessionmaker()
        try:
            stmt = (
                update(saga_logs_table)
                .where(
                    (saga_logs_table.c.saga_id == saga_id)
                    & (saga_logs_table.c.step == step)
                )
                .values(status=status)
            )
            result = await session.execute(stmt)
            logger.info(
                f"Update executed for saga_id {saga_id}, step {step}, rows affected: {result.rowcount}"
            )
            await session.commit()
        except Exception as e:
            logger.error(
                f"Failed to update status for saga_id {saga_id}, step {step}: {e}"
            )
            await session.rollback()
            raise
        finally:
            await session.close()
