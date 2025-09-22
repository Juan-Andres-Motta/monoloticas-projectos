import logging
from src.application.commands.register_payment_command import RegisterPaymentCommand
from src.domain.ports.payment_repository import PaymentRepository

logger = logging.getLogger(__name__)


class RegisterPaymentHandler:
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    async def handle(self, command: RegisterPaymentCommand) -> None:
        logger.info(
            f"Handling RegisterPaymentCommand for user_id: {command.payment.user_id}"
        )
        await self.payment_repository.save(command.payment)
        logger.info(
            f"Payment registered successfully for user: {command.payment.user_id}"
        )
