from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from uuid import UUID

from ...domain.aggregates.tracking_event import TrackingEvent
from ...domain.repositories.tracking_event_repository import TrackingEventRepository
from ..models.tracking_event_model import TrackingEventModel


class SqlAlchemyTrackingEventRepository(TrackingEventRepository):
    """SQLAlchemy implementation of tracking event repository"""

    def __init__(self, session: Session):
        self._session = session

    async def save(self, tracking_event: TrackingEvent) -> None:
        """Save tracking event to database"""
        try:
            # Convert domain aggregate to SQLAlchemy model
            model = TrackingEventModel(
                tracking_event_id=tracking_event.tracking_event_id,
                partner_id=tracking_event.partner_id,
                campaign_id=tracking_event.campaign_id,
                visitor_id=tracking_event.visitor_id,
                interaction_type=tracking_event.interaction_type,
                source_url=tracking_event.source_url,
                destination_url=tracking_event.destination_url,
                recorded_at=tracking_event.recorded_at,
            )

            self._session.add(model)
            self._session.commit()

        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Failed to save tracking event: {str(e)}")

    async def get_by_id(self, tracking_event_id: UUID) -> Optional[TrackingEvent]:
        """Get tracking event by ID"""
        try:
            model = (
                self._session.query(TrackingEventModel)
                .filter(TrackingEventModel.tracking_event_id == tracking_event_id)
                .first()
            )

            if not model:
                return None

            # Convert SQLAlchemy model back to domain aggregate
            return TrackingEvent(
                partner_id=model.partner_id,
                campaign_id=model.campaign_id,
                visitor_id=model.visitor_id,
                interaction_type=model.interaction_type,
                source_url=model.source_url,
                destination_url=model.destination_url,
                tracking_event_id=model.tracking_event_id,
                recorded_at=model.recorded_at,
            )

        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get tracking event: {str(e)}")
