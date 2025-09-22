import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.domain.entities.partner import Partner
from src.domain.ports.partner_repository import PartnerRepository
from .models import partners_table

logger = logging.getLogger(__name__)


class PostgresPartnerRepository(PartnerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, partner: Partner) -> None:
        logger.info(f"Saving partner to database: {partner.partner_id}")
        # Assuming a table 'partners' with columns: id (auto), partner_id, partner_type, acceptance_terms (json), estimated_monthly_reach
        stmt = insert(partners_table).values(
            partner_id=partner.partner_id,
            partner_type=partner.partner_type,
            acceptance_terms=json.dumps(partner.acceptance_terms.dict()),
            estimated_monthly_reach=partner.estimated_monthly_reach,
        )
        await self.session.execute(stmt)
        await self.session.commit()
        logger.info(f"Partner saved successfully: {partner.partner_id}")
