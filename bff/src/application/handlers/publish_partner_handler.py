import logging
from src.application.commands.publish_partner_command import PublishPartnerCommand
from src.domain.ports.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class PublishPartnerHandler:
    def __init__(self, event_publisher: EventPublisher):
        self.event_publisher = event_publisher

    async def handle(self, command: PublishPartnerCommand) -> None:
        logger.info(
            f"Publishing partner event for partner_id: {command.partner.partner_id}"
        )
        await self.event_publisher.publish_partner_event(command.partner)
        logger.info(
            f"Partner event published successfully: {command.partner.partner_id}"
        )
