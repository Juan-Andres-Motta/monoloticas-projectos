from sqlalchemy import Column, String, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from config.database import Base
from datetime import datetime
import uuid


class CommissionModel(Base):
    """SQLAlchemy model for Commission"""

    __tablename__ = "commissions"

    commission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_event_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    partner_id = Column(String(255), nullable=False, index=True)
    campaign_id = Column(String(255), nullable=False, index=True)
    visitor_id = Column(String(255), nullable=False)
    interaction_type = Column(String(50), nullable=False)
    commission_amount = Column(Numeric(10, 2), nullable=False)
    commission_rate = Column(Numeric(5, 4), nullable=False)  # e.g., 0.1500 for 15%
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(String(50), nullable=False, default="calculated")
    calculated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<CommissionModel {self.commission_id} - {self.partner_id} - {self.commission_amount} {self.currency}>"
