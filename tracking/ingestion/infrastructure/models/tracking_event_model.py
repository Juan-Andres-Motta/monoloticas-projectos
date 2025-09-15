from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid as uuid_lib

from config.database import Base


class TrackingEventModel(Base):
    """SQLAlchemy model for tracking events"""

    __tablename__ = "tracking_events"

    tracking_event_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4
    )
    partner_id = Column(String(255), nullable=False, index=True)
    campaign_id = Column(String(255), nullable=False, index=True)
    visitor_id = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False, index=True)
    source_url = Column(Text, nullable=False)
    destination_url = Column(Text, nullable=False)
    recorded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"<TrackingEvent(id={self.tracking_event_id}, partner={self.partner_id}, type={self.interaction_type})>"
