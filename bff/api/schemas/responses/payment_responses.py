from pydantic import BaseModel
from uuid import UUID
from enum import Enum


class CommandStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RequestPaymentResponse(BaseModel):
    command_id: UUID
    status: CommandStatus
    message: str
    partner_id: str
    user_id: str
    request_type: str
    requested_amount: float
    currency: str