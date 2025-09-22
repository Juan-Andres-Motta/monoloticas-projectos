import logging
from src.application.commands.register_tracking_event_command import (
    RegisterTrackingEventCommand,
)
from src.domain.ports.tracking_event_repository import TrackingEventRepository
from src.domain.ports.saga_log_repository import SagaLogRepository
from src.domain.entities.saga_log import SagaLog, SagaStep, SagaStatus
from src.infrastructure.adapters.pulsar_producer import PulsarCommissionPublisher

logger = logging.getLogger(__name__)


class RegisterTrackingEventHandler:
    def __init__(
        self,
        tracking_event_repository: TrackingEventRepository,
        commission_publisher: PulsarCommissionPublisher,
        saga_log_repository: SagaLogRepository,
    ):
        self.tracking_event_repository = tracking_event_repository
        self.commission_publisher = commission_publisher
        self.saga_log_repository = saga_log_repository

    async def handle(self, command: RegisterTrackingEventCommand) -> None:
        logger.info(
            f"Handling RegisterTrackingEventCommand for campaign: {command.tracking_event.campaign_id}, event: {command.tracking_event.event_type}"
        )
        tracking_id = await self.tracking_event_repository.save(command.tracking_event)
        logger.info(
            f"Tracking event registered successfully for campaign: {command.tracking_event.campaign_id} with id: {tracking_id}"
        )

        saga_id = str(tracking_id)

        # Log saga start
        await self.saga_log_repository.save(
            SagaLog(saga_id=saga_id, step=SagaStep.STARTED, status=SagaStatus.PENDING)
        )

        # Log tracking saved
        await self.saga_log_repository.save(
            SagaLog(
                saga_id=saga_id,
                step=SagaStep.TRACKING_SAVED,
                status=SagaStatus.SUCCESS,
                details=f"tracking_id: {tracking_id}",
            )
        )

        # Publish commission event
        event_type = command.tracking_event.event_type
        commission_type = self._map_event_to_commission_type(event_type)
        amount = self._calculate_commission_amount(event_type)
        await self.commission_publisher.publish_commission_event(
            amount=amount,
            campaign_id=command.tracking_event.campaign_id,
            commission_type=commission_type,
            tracking_id=tracking_id,
        )
        logger.info(
            f"Commission event published for campaign: {command.tracking_event.campaign_id} with tracking_id: {tracking_id}"
        )

        # Log commission published
        await self.saga_log_repository.save(
            SagaLog(
                saga_id=saga_id,
                step=SagaStep.COMMISSION_PUBLISHED,
                status=SagaStatus.SUCCESS,
            )
        )

    def _map_event_to_commission_type(self, event_type: str) -> str:
        mapping = {
            "click": "CPC",
            "impression": "CPM",
            "conversion": "CPA",
        }
        return mapping.get(event_type, "CPC")  # Default to CPC

    def _calculate_commission_amount(self, event_type: str) -> float:
        # Simple fixed amounts, can be made configurable
        amounts = {
            "click": 0.10,
            "impression": 0.01,
            "conversion": 1.00,
        }
        return amounts.get(event_type, 0.10)
