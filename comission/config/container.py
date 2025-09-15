from typing import Dict, Any
from sqlalchemy.orm import Session

from config.database import SessionLocal
from commission.infrastructure.repositories.sqlalchemy_commission_repository import (
    SqlAlchemyCommissionRepository,
)
from commission.application.handlers.calculate_commission_handler import (
    CalculateCommissionHandler,
)
from commission.application.handlers.commission_notification_handler import (
    CommissionNotificationHandler,
)
from seedwork.application.command_bus import CommandBus
from seedwork.domain.domain_event_publisher import InMemoryDomainEventPublisher


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
        notification_handler = CommissionNotificationHandler()
        event_publisher.register_handler(
            "commission.calculated.v1", notification_handler
        )

        # Repository (Infrastructure layer)
        commission_repository = SqlAlchemyCommissionRepository(db_session)

        # Command Handler (Application layer)
        calculate_handler = CalculateCommissionHandler(
            repository=commission_repository, event_publisher=event_publisher
        )

        # Command Bus (Application layer)
        command_bus = CommandBus()
        command_bus.register("calculate_commission", calculate_handler)

        # Register services
        self._services["command_bus"] = command_bus
        self._services["commission_repository"] = commission_repository
        self._services["db_session"] = db_session
        self._services["event_publisher"] = event_publisher

    def get(self, service_name: str):
        return self._services.get(service_name)
