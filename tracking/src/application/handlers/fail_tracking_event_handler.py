import logging
from src.application.commands.fail_tracking_event_command import (
    FailTrackingEventCommand,
)
from src.domain.ports.tracking_event_repository import TrackingEventRepository
from src.domain.ports.saga_log_repository import SagaLogRepository
from src.domain.entities.saga_log import SagaLog, SagaStep, SagaStatus

logger = logging.getLogger(__name__)


class FailTrackingEventHandler:
    def __init__(
        self,
        tracking_event_repository: TrackingEventRepository,
        saga_log_repository: SagaLogRepository,
    ):
        self.tracking_event_repository = tracking_event_repository
        self.saga_log_repository = saga_log_repository

    async def handle(self, command: FailTrackingEventCommand) -> None:
        saga_id = str(command.tracking_id)

        logger.info(
            f"Handling FailTrackingEventCommand for tracking_id: {command.tracking_id}"
        )
        try:
            await self.tracking_event_repository.update_status(
                command.tracking_id, "failed"
            )
            logger.info(
                f"Tracking event {command.tracking_id} marked as failed successfully"
            )

            # Log commission failed
            await self.saga_log_repository.save(
                SagaLog(
                    saga_id=saga_id,
                    step=SagaStep.COMMISSION_FAILED,
                    status=SagaStatus.FAILED,
                    details=f"tracking_id: {command.tracking_id}",
                )
            )

            # Log compensation completed
            await self.saga_log_repository.save(
                SagaLog(
                    saga_id=saga_id,
                    step=SagaStep.COMPENSATION_COMPLETED,
                    status=SagaStatus.SUCCESS,
                    details="Marked tracking as failed",
                )
            )

        except Exception as e:
            logger.error(
                f"Failed to handle FailTrackingEventCommand for tracking_id {command.tracking_id}: {e}"
            )
            # Log compensation failed
            await self.saga_log_repository.save(
                SagaLog(
                    saga_id=saga_id,
                    step=SagaStep.COMPENSATION_COMPLETED,
                    status=SagaStatus.FAILED,
                    details=str(e),
                )
            )
            raise
