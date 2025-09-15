from pydantic import BaseModel
from uuid import UUID
from enum import Enum


class CommandStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class UploadEvidenceResponse(BaseModel):
    command_id: UUID
    status: CommandStatus
    message: str
    campaign_id: str
    partner_id: str
    user_id: str
    evidence_type: str