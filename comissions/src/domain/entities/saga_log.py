from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class SagaStep(str, Enum):
    COMMISSION_RECEIVED = "commission_received"
    PARTNER_QUERIED = "partner_queried"
    COMMISSION_SAVED = "commission_saved"
    COMMISSION_FAILED = "commission_failed"


class SagaStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class SagaLog(BaseModel):
    id: int | None = None
    saga_id: str  # tracking_id
    step: SagaStep
    status: SagaStatus
    timestamp: datetime = datetime.utcnow()
    details: str | None = None
