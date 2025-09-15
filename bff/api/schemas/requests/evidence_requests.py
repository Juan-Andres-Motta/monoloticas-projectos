from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class EvidenceType(str, Enum):
    POST = "POST"
    STORY = "STORY"
    VIDEO = "VIDEO"
    ARTICLE = "ARTICLE"


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    BLOG = "blog"
    FACEBOOK = "facebook"


class ContentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    ARTICLE = "article"


class EngagementMetrics(BaseModel):
    views: int
    likes: int
    comments: int
    shares: int


class Demographics(BaseModel):
    primary_country: str
    age_range: str


class AudienceData(BaseModel):
    followers_count: int
    audience_reached: int
    demographics: Demographics


class EvidenceDetails(BaseModel):
    platform: Platform
    post_url: str
    post_date: datetime
    content_type: ContentType
    engagement_metrics: EngagementMetrics


class UploadEvidenceRequest(BaseModel):
    partner_id: str
    campaign_id: str
    evidence_type: EvidenceType
    evidence_details: EvidenceDetails
    audience_data: AudienceData
    description: str