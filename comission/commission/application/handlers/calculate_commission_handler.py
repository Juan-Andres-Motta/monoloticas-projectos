from uuid import UUID
from seedwork.application.command_handler import CommandHandler
from seedwork.domain.domain_event_publisher import DomainEventPublisher
from ..commands.calculate_commission_command import CalculateCommissionCommand
from ...domain.repositories.commission_repository import CommissionRepository
from ...domain.aggregates.commission import Commission


class CalculateCommissionHandler(CommandHandler[CalculateCommissionCommand, UUID]):
    """Handles commission calculation from tracking events"""

    def __init__(
        self,
        repository: CommissionRepository,
        event_publisher: DomainEventPublisher = None,
    ):
        self._repository = repository
        self._event_publisher = event_publisher

    async def handle(self, command: CalculateCommissionCommand) -> UUID:
        """Handle the calculate commission command"""

        # Check if commission already exists for this tracking event
        existing_commission = await self._repository.find_by_tracking_event_id(
            command.tracking_event_id
        )

        if existing_commission:
            # Return existing commission ID to avoid duplicates
            return existing_commission.commission_id

        # Create commission using domain factory method
        commission = Commission.calculate_commission(
            tracking_event_id=command.tracking_event_id,
            partner_id=command.partner_id,
            campaign_id=command.campaign_id,
            visitor_id=command.visitor_id,
            interaction_type=command.interaction_type,
        )

        # Persist commission
        await self._repository.save(commission)

        # Publish domain events
        if self._event_publisher:
            domain_events = commission.clear_domain_events()
            if domain_events:
                await self._event_publisher.publish(domain_events)

        return commission.commission_id
