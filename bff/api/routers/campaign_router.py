from fastapi import APIRouter, HTTPException, Depends, Request
from api.schemas.requests.campaign_requests import AcceptCampaignRequest
from api.schemas.responses.campaign_responses import AcceptCampaignResponse
from application.commands.accept_campaign_command import (
    AcceptCampaignCommand,
    AcceptanceTerms as CommandAcceptanceTerms,
)
from config.jwt_auth import JWTAuth
from uuid import uuid4


def create_campaign_router() -> APIRouter:
    """Factory function to create campaign router"""

    router = APIRouter(prefix="/api/v1/campaigns", tags=["campaigns"])

    @router.post(
        "/{campaign_id}/accept",
        response_model=AcceptCampaignResponse,
        summary="Accept Campaign Enrollment",
        description="""
        Accept enrollment in a specific campaign.

        This endpoint allows partners to accept participation in campaigns by providing
        their terms and conditions. Upon acceptance, a command is published to Pulsar
        for processing by the campaign service.

        **Required Authentication:** JWT token with valid user_id
        """,
        dependencies=[Depends(JWTAuth.extract_user_id)],
    )
    async def accept_campaign(
        campaign_id: str,
        request_data: AcceptCampaignRequest,
        request: Request,
        user_id: str = Depends(JWTAuth.extract_user_id),
    ) -> AcceptCampaignResponse:

        try:
            # Get Pulsar publisher from app state
            pulsar_publisher = getattr(request.app.state, "pulsar_publisher", None)
            if not pulsar_publisher:
                raise HTTPException(
                    status_code=503, detail="Event publishing service unavailable"
                )

            # Generate command ID for tracking
            command_id = str(uuid4())

            # Publish campaign accept command to Pulsar
            await pulsar_publisher.publish_campaign_accept_command(
                user_id=user_id,
                campaign_id=campaign_id,
                partner_id=request_data.partner_id,
                partner_type=request_data.partner_type,
                acceptance_terms={
                    "commission_type": request_data.acceptance_terms.commission_type,
                    "commission_rate": request_data.acceptance_terms.commission_rate,
                    "cookie_duration_days": request_data.acceptance_terms.cookie_duration_days,
                    "promotional_methods": request_data.acceptance_terms.promotional_methods,
                },
                estimated_monthly_reach=request_data.estimated_monthly_reach,
            )

            # Return immediate response (async processing)
            return AcceptCampaignResponse(
                command_id=command_id,
                status="accepted",
                campaign_id=campaign_id,
                partner_id=request_data.partner_id,
                message="Campaign acceptance submitted for processing",
                processing_status="async",
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get(
        "/health",
        tags=["health"],
        summary="Campaign Service Health Check",
        description="Check the health status of the campaign management endpoints.",
    )
    async def health_check():
        """Health check for campaign router"""
        return {"status": "healthy", "service": "bff-campaigns", "version": "0.1.0"}

    return router
