from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class SagaStep(str, Enum):
    STARTED = "started"
    TRACKING_SAVED = "tracking_saved"
    COMMISSION_PUBLISHED = "commission_published"
    COMMISSION_FAILED = "commission_failed"
    COMPENSATION_COMPLETED = "compensation_completed"


class SagaStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    COMPENSATED = "compensated"


class SagaLog(BaseModel):
    id: int | None = None
    saga_id: str  # tracking_id
    step: SagaStep
    status: SagaStatus
    timestamp: datetime = datetime.utcnow()
    details: str | None = None
