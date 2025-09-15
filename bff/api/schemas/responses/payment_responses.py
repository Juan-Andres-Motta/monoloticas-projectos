from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from typing import Optional


class CommandStatus(str, Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStatus(str, Enum):
    SYNC = "sync"
    ASYNC = "async"


class RequestPaymentResponse(BaseModel):
    command_id: str
    status: CommandStatus
    message: str
    partner_id: str
    request_type: str
    requested_amount: float
    currency: str
    processing_status: ProcessingStatus = ProcessingStatus.ASYNC
    user_id: Optional[str] = None
