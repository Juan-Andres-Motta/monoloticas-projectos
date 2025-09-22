import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.domain.entities.commission import Commission
from src.domain.ports.commission_repository import CommissionRepository
from .models import commissions_table

logger = logging.getLogger(__name__)


class PostgresCommissionRepository(CommissionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, commission: Commission) -> None:
        logger.info(
            f"Saving commission to database for partner: {commission.partner_id}, campaign: {commission.campaign_id}"
        )
        stmt = insert(commissions_table).values(
            amount=commission.amount,
            partner_id=commission.partner_id,
            campaign_id=commission.campaign_id,
            commission_type=commission.commission_type,
            tracking_id=commission.tracking_id,
            status=commission.status,
            created_at=commission.created_at,
        )
        await self.session.execute(stmt)
        await self.session.commit()
        logger.info(
            f"Commission saved successfully for partner: {commission.partner_id}"
        )
