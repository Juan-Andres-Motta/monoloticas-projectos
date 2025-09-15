from typing import Dict, Any
from sqlalchemy.orm import Session

from config.database import SessionLocal
from ingestion.infrastructure.repositories.sqlalchemy_tracking_event_repository import (
    SqlAlchemyTrackingEventRepository,
)
from ingestion.application.handlers.record_tracking_event_handler import (
    RecordTrackingEventHandler,
)
from seedwork.application.command_bus import CommandBus
from seedwork.domain.domain_event_publisher import InMemoryDomainEventPublisher
from attribution.application.handlers.attribution_event_handler import (
    AttributionEventHandler,
)
from messaging.handlers.pulsar_event_handler import PulsarEventHandler
from messaging.pulsar_publisher import pulsar_publisher


class Container:
    """Simple dependency injection container"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._setup_dependencies()

    def _setup_dependencies(self):
        # Database session
        db_session = SessionLocal()

        # Event Publisher (Domain layer)
        event_publisher = InMemoryDomainEventPublisher()

        # Event Handlers (Application layer)
        attribution_handler = AttributionEventHandler()
        pulsar_handler = PulsarEventHandler(pulsar_publisher)

        event_publisher.register_handler(
            "tracking_event.recorded.v1", attribution_handler
        )
        event_publisher.register_handler("tracking_event.recorded.v1", pulsar_handler)

        # Repository (Infrastructure layer)
        tracking_repository = SqlAlchemyTrackingEventRepository(db_session)

        # Command Handler (Application layer)
        record_handler = RecordTrackingEventHandler(
            repository=tracking_repository, event_publisher=event_publisher
        )

        # Command Bus (Application layer)
        command_bus = CommandBus()
        command_bus.register("record_tracking_event", record_handler)

        # Register services
        self._services["command_bus"] = command_bus
        self._services["tracking_repository"] = tracking_repository
        self._services["db_session"] = db_session
        self._services["event_publisher"] = event_publisher
        self._services["pulsar_publisher"] = pulsar_publisher

    def get(self, service_name: str):
        return self._services.get(service_name)
