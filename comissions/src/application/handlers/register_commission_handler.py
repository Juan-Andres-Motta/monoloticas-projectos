import logging
from src.application.commands.register_commission_command import (
    RegisterCommissionCommand,
)
from src.domain.ports.commission_repository import CommissionRepository
from src.domain.ports.saga_log_repository import SagaLogRepository
from src.domain.entities.saga_log import SagaLog, SagaStep, SagaStatus

logger = logging.getLogger(__name__)


class RegisterCommissionHandler:
    def __init__(
        self,
        commission_repository: CommissionRepository,
        saga_log_repository: SagaLogRepository,
    ):
        self.commission_repository = commission_repository
        self.saga_log_repository = saga_log_repository

    async def handle(self, command: RegisterCommissionCommand) -> None:
        saga_id = str(command.commission.tracking_id)

        # Log commission received
        await self.saga_log_repository.save(
            SagaLog(
                saga_id=saga_id,
                step=SagaStep.COMMISSION_RECEIVED,
                status=SagaStatus.SUCCESS,
            )
        )

        logger.info(
            f"Handling RegisterCommissionCommand for partner: {command.commission.partner_id}, campaign: {command.commission.campaign_id}"
        )

        # Log partner queried (assuming it's done in consumer)
        await self.saga_log_repository.save(
            SagaLog(
                saga_id=saga_id,
                step=SagaStep.PARTNER_QUERIED,
                status=SagaStatus.SUCCESS,
                details=f"partner_id: {command.commission.partner_id}",
            )
        )

        await self.commission_repository.save(command.commission)
        logger.info(
            f"Commission registered successfully for partner: {command.commission.partner_id}"
        )

        # Log commission saved
        await self.saga_log_repository.save(
            SagaLog(
                saga_id=saga_id,
                step=SagaStep.COMMISSION_SAVED,
                status=SagaStatus.SUCCESS,
            )
        )
