from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from ...domain.repositories.commission_repository import CommissionRepository
from ...domain.aggregates.commission import Commission
from ..models.commission_model import CommissionModel


class SqlAlchemyCommissionRepository(CommissionRepository):
    """SQLAlchemy implementation of Commission repository"""

    def __init__(self, db_session: Session):
        self._session = db_session

    async def save(self, commission: Commission) -> None:
        """Save commission to database"""

        # Check if commission already exists
        existing = (
            self._session.query(CommissionModel)
            .filter(CommissionModel.commission_id == commission.commission_id)
            .first()
        )

        if existing:
            # Update existing commission
            existing.tracking_event_id = commission.tracking_event_id
            existing.partner_id = commission.partner_id
            existing.campaign_id = commission.campaign_id
            existing.visitor_id = commission.visitor_id
            existing.interaction_type = commission.interaction_type
            existing.commission_amount = commission.commission_amount
            existing.commission_rate = commission.commission_rate
            existing.currency = commission.currency
            existing.status = commission.status
            existing.calculated_at = commission.calculated_at
        else:
            # Create new commission
            commission_model = CommissionModel(
                commission_id=commission.commission_id,
                tracking_event_id=commission.tracking_event_id,
                partner_id=commission.partner_id,
                campaign_id=commission.campaign_id,
                visitor_id=commission.visitor_id,
                interaction_type=commission.interaction_type,
                commission_amount=commission.commission_amount,
                commission_rate=commission.commission_rate,
                currency=commission.currency,
                status=commission.status,
                calculated_at=commission.calculated_at,
            )
            self._session.add(commission_model)

        self._session.commit()

    async def find_by_id(self, commission_id: UUID) -> Optional[Commission]:
        """Find commission by ID"""
        model = (
            self._session.query(CommissionModel)
            .filter(CommissionModel.commission_id == commission_id)
            .first()
        )

        if model:
            return self._model_to_aggregate(model)
        return None

    async def find_by_tracking_event_id(
        self, tracking_event_id: UUID
    ) -> Optional[Commission]:
        """Find commission by tracking event ID"""
        model = (
            self._session.query(CommissionModel)
            .filter(CommissionModel.tracking_event_id == tracking_event_id)
            .first()
        )

        if model:
            return self._model_to_aggregate(model)
        return None

    async def find_by_partner_id(
        self, partner_id: str, limit: int = 100
    ) -> List[Commission]:
        """Find commissions by partner ID"""
        models = (
            self._session.query(CommissionModel)
            .filter(CommissionModel.partner_id == partner_id)
            .limit(limit)
            .all()
        )

        return [self._model_to_aggregate(model) for model in models]

    async def find_by_campaign_id(
        self, campaign_id: str, limit: int = 100
    ) -> List[Commission]:
        """Find commissions by campaign ID"""
        models = (
            self._session.query(CommissionModel)
            .filter(CommissionModel.campaign_id == campaign_id)
            .limit(limit)
            .all()
        )

        return [self._model_to_aggregate(model) for model in models]

    def _model_to_aggregate(self, model: CommissionModel) -> Commission:
        """Convert database model to domain aggregate"""
        commission = Commission(
            commission_id=model.commission_id,
            tracking_event_id=model.tracking_event_id,
            partner_id=model.partner_id,
            campaign_id=model.campaign_id,
            visitor_id=model.visitor_id,
            interaction_type=model.interaction_type,
            commission_amount=model.commission_amount,
            commission_rate=model.commission_rate,
            currency=model.currency,
            calculated_at=model.calculated_at,
            status=model.status,
        )
        return commission
