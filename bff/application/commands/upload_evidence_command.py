from dataclasses import dataclass
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


@dataclass
class EngagementMetrics:
    views: int
    likes: int
    comments: int
    shares: int


@dataclass
class Demographics:
    primary_country: str
    age_range: str


@dataclass
class AudienceData:
    followers_count: int
    audience_reached: int
    demographics: Demographics


@dataclass
class EvidenceDetails:
    platform: Platform
    post_url: str
    post_date: datetime
    content_type: ContentType
    engagement_metrics: EngagementMetrics


@dataclass
class UploadEvidenceCommand:
    partner_id: str
    campaign_id: str
    evidence_type: EvidenceType
    evidence_details: EvidenceDetails
    audience_data: AudienceData
    description: str