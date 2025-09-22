import logging
from src.application.commands.fail_tracking_event_command import (
    FailTrackingEventCommand,
)
from src.domain.ports.tracking_event_repository import TrackingEventRepository

logger = logging.getLogger(__name__)


class FailTrackingEventHandler:
    def __init__(self, tracking_event_repository: TrackingEventRepository):
        self.tracking_event_repository = tracking_event_repository

    async def handle(self, command: FailTrackingEventCommand) -> None:
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
        except Exception as e:
            logger.error(
                f"Failed to handle FailTrackingEventCommand for tracking_id {command.tracking_id}: {e}"
            )
            raise
