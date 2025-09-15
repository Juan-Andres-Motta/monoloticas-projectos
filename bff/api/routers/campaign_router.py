from fastapi import APIRouter, HTTPException, Depends
from ..schemas.requests.campaign_requests import AcceptCampaignRequest
from ..schemas.responses.campaign_responses import AcceptCampaignResponse
from ...application.commands.accept_campaign_command import (
    AcceptCampaignCommand,
    AcceptanceTerms as CommandAcceptanceTerms
)
from ...application.handlers.accept_campaign_handler import AcceptCampaignHandler
from ...config.jwt_auth import JWTAuth


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
        dependencies=[Depends(JWTAuth.extract_user_id)]
    )
    async def accept_campaign(
        campaign_id: str,
        request_data: AcceptCampaignRequest,
        user_id: str = Depends(JWTAuth.extract_user_id)
    ) -> AcceptCampaignResponse:

        try:
            # Convert request to command
            command = AcceptCampaignCommand(
                campaign_id=campaign_id,
                partner_id=request_data.partner_id,
                partner_type=request_data.partner_type,
                acceptance_terms=CommandAcceptanceTerms(
                    commission_type=request_data.acceptance_terms.commission_type,
                    commission_rate=request_data.acceptance_terms.commission_rate,
                    cookie_duration_days=request_data.acceptance_terms.cookie_duration_days,
                    promotional_methods=request_data.acceptance_terms.promotional_methods
                ),
                estimated_monthly_reach=request_data.estimated_monthly_reach
            )

            # Execute command via handler (needs Pulsar publisher injection)
            # TODO: Get Pulsar publisher from DI container
            handler = AcceptCampaignHandler(pulsar_publisher=None)  # Will be injected
            result = await handler.handle(command, user_id)

            # Convert result to response model
            return AcceptCampaignResponse(**result)

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get(
        "/health",
        tags=["health"],
        summary="Campaign Service Health Check",
        description="Check the health status of the campaign management endpoints."
    )
    async def health_check():
        """Health check for campaign router"""
        return {
            "status": "healthy",
            "service": "bff-campaigns",
            "version": "0.1.0"
        }

    return router