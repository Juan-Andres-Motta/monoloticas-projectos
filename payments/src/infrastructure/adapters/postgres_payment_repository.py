import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.domain.entities.payment import Payment
from src.domain.ports.payment_repository import PaymentRepository
from .models import payments_table

logger = logging.getLogger(__name__)


class PostgresPaymentRepository(PaymentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, payment: Payment) -> None:
        logger.info(f"Saving payment to database for user: {payment.user_id}")
        stmt = insert(payments_table).values(
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment.payment_method,
            account_details=json.dumps(payment.account_details),
            user_id=payment.user_id,
        )
        await self.session.execute(stmt)
        await self.session.commit()
        logger.info(f"Payment saved successfully for user: {payment.user_id}")
