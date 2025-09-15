from uuid import UUID
from seedwork.application.command_handler import CommandHandler
from seedwork.domain.domain_event_publisher import DomainEventPublisher
from ..commands.record_tracking_event_command import RecordTrackingEventCommand
from ...domain.repositories.tracking_event_repository import TrackingEventRepository
from ...domain.aggregates.tracking_event import TrackingEvent


class RecordTrackingEventHandler(CommandHandler[RecordTrackingEventCommand, UUID]):
    """Handles recording tracking events"""

    def __init__(
        self,
        repository: TrackingEventRepository,
        event_publisher: DomainEventPublisher = None,
    ):
        self._repository = repository
        self._event_publisher = event_publisher

    async def handle(self, command: RecordTrackingEventCommand) -> UUID:
        """Handle the record tracking event command"""

        # Create aggregate using factory method
        tracking_event = TrackingEvent.record_new_interaction(
            partner_id=command.partner_id,
            campaign_id=command.campaign_id,
            visitor_id=command.visitor_id,
            interaction_type=command.interaction_type,
            source_url=command.source_url,
            destination_url=command.destination_url,
        )

        # Persist aggregate
        await self._repository.save(tracking_event)

        # Publish domain events
        if self._event_publisher:
            domain_events = tracking_event.clear_domain_events()
            if domain_events:
                await self._event_publisher.publish(domain_events)

        return tracking_event.tracking_event_id
