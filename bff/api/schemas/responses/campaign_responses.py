from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from typing import Optional


class CommandStatus(str, Enum):
    ACCEPTED = "accepted"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStatus(str, Enum):
    SYNC = "sync"
    ASYNC = "async"


class AcceptCampaignResponse(BaseModel):
    command_id: str
    status: CommandStatus
    message: str
    campaign_id: str
    partner_id: str
    processing_status: ProcessingStatus = ProcessingStatus.ASYNC
    user_id: Optional[str] = None
