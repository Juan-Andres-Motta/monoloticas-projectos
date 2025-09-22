from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
import uuid
from src.application.commands.publish_partner_command import PublishPartnerCommand
from src.application.handlers.publish_partner_handler import PublishPartnerHandler
from src.domain.entities.partner import Partner, AcceptanceTerms
from src.domain.entities.payment import Payment
from src.infrastructure.adapters.pulsar_producer import PulsarEventPublisher

app = FastAPI(title="BFF Service", version="1.0.0")

logger = logging.getLogger(__name__)

# Dependency injection (in a real app, use DI container)
# For simplicity, assume publisher is injected
publisher = None  # Will be set in main


def set_publisher(p):
    global publisher
    publisher = p


class AcceptanceTermsRequest(BaseModel):
    commission_type: str
    commission_rate: float
    cookie_duration_days: int
    promotional_methods: List[str]


class PartnerRequest(BaseModel):
    partner_id: str
    partner_type: str
    acceptance_terms: AcceptanceTermsRequest
    estimated_monthly_reach: int


class CampaignRequest(BaseModel):
    campaign_id: str
    name: str


class ContentRequest(BaseModel):
    content_url: str


class TrackingEventRequest(BaseModel):
    campaign_id: str
    event_type: str


class FailTrackingEventRequest(BaseModel):
    tracking_id: int


class PaymentRequest(BaseModel):
    amount: float
    currency: str
    payment_method: str
    account_details: str
    user_id: str


@app.post("/partners")
async def create_partner(partner_request: PartnerRequest):
    try:
        acceptance_terms = AcceptanceTerms(**partner_request.acceptance_terms.dict())
        partner = Partner(
            partner_id=partner_request.partner_id,
            partner_type=partner_request.partner_type,
            acceptance_terms=acceptance_terms,
            estimated_monthly_reach=partner_request.estimated_monthly_reach,
        )
        await publisher.publish_partner_event(partner)
        return {
            "message": "Partner event published successfully",
            "partner_id": partner.partner_id,
        }
    except Exception as e:
        logger.error(f"Error publishing partner event: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish partner event")


@app.post("/campaigns")
async def create_campaign(campaign_request: CampaignRequest):
    try:
        await publisher.publish_campaign_event(
            campaign_request.campaign_id, campaign_request.name
        )
        return {
            "message": "Campaign event published successfully",
            "campaign_id": campaign_request.campaign_id,
        }
    except Exception as e:
        logger.error(f"Error publishing campaign event: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish campaign event")


@app.post("/campaigns/{campaign_id}/partners/{partner_id}")
async def associate_partner_to_campaign(campaign_id: str, partner_id: str):
    try:
        await publisher.publish_association_event(campaign_id, partner_id)
        return {
            "message": "Campaign-partner association event published successfully",
            "campaign_id": campaign_id,
            "partner_id": partner_id,
        }
    except Exception as e:
        logger.error(f"Error publishing association event: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to publish association event"
        )


@app.post("/campaigns/{campaign_id}/content")
async def submit_content_to_campaign(campaign_id: str, content_request: ContentRequest):
    try:
        content_id = str(uuid.uuid4())
        await publisher.publish_content_event(
            content_id, campaign_id, content_request.content_url
        )
        return {
            "message": "Content association event published successfully",
            "campaign_id": campaign_id,
            "content_id": content_id,
            "content_url": content_request.content_url,
        }
    except Exception as e:
        logger.error(f"Error publishing content event: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish content event")


@app.post("/tracking")
async def register_tracking_event(tracking_request: TrackingEventRequest):
    try:
        await publisher.publish_tracking_event(
            tracking_request.campaign_id,
            tracking_request.event_type,
        )
        return {
            "message": "Tracking event published successfully",
            "campaign_id": tracking_request.campaign_id,
            "event_type": tracking_request.event_type,
        }
    except Exception as e:
        logger.error(f"Error publishing tracking event: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish tracking event")


@app.post("/fail-tracking")
async def fail_tracking_event(fail_request: FailTrackingEventRequest):
    try:
        await publisher.publish_fail_tracking_event(fail_request.tracking_id)
        return {
            "message": "Fail tracking event published successfully",
            "tracking_id": fail_request.tracking_id,
        }
    except Exception as e:
        logger.error(f"Error publishing fail tracking event: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to publish fail tracking event"
        )


@app.post("/payments")
async def create_payment(payment_request: PaymentRequest):
    try:
        payment = Payment(**payment_request.dict())
        await publisher.publish_payment_event(payment)
        return {
            "message": "Payment event published successfully",
            "user_id": payment.user_id,
            "amount": payment.amount,
            "currency": payment.currency,
        }
    except Exception as e:
        logger.error(f"Error publishing payment event: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish payment event")
