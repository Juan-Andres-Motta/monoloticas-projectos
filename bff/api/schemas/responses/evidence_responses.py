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


class UploadEvidenceResponse(BaseModel):
    command_id: str
    status: CommandStatus
    message: str
    campaign_id: str
    partner_id: str
    evidence_type: str
    processing_status: ProcessingStatus = ProcessingStatus.ASYNC
    user_id: Optional[str] = None
