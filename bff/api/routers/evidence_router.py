from fastapi import APIRouter, HTTPException, Depends
from ..schemas.requests.evidence_requests import UploadEvidenceRequest
from ..schemas.responses.evidence_responses import UploadEvidenceResponse
from ...application.commands.upload_evidence_command import (
    UploadEvidenceCommand,
    EvidenceDetails as CommandEvidenceDetails,
    EngagementMetrics as CommandEngagementMetrics,
    Demographics as CommandDemographics,
    AudienceData as CommandAudienceData
)
from ...application.handlers.upload_evidence_handler import UploadEvidenceHandler
from ...config.jwt_auth import JWTAuth


def create_evidence_router() -> APIRouter:
    """Factory function to create evidence router"""

    router = APIRouter(prefix="/api/v1/campaigns", tags=["evidence"])

    @router.post(
        "/{campaign_id}/evidence",
        response_model=UploadEvidenceResponse,
        summary="Upload Campaign Evidence",
        description="""
        Upload evidence of campaign participation for validation.

        This endpoint allows partners to submit proof of their campaign execution,
        including engagement metrics, audience data, and content details. The evidence
        is processed asynchronously via Pulsar messaging.

        **Required Authentication:** JWT token with valid user_id
        """,
        dependencies=[Depends(JWTAuth.extract_user_id)]
    )
    async def upload_evidence(
        campaign_id: str,
        request_data: UploadEvidenceRequest,
        user_id: str = Depends(JWTAuth.extract_user_id)
    ) -> UploadEvidenceResponse:

        try:
            # Convert request to command
            command = UploadEvidenceCommand(
                partner_id=request_data.partner_id,
                campaign_id=campaign_id,
                evidence_type=request_data.evidence_type,
                evidence_details=CommandEvidenceDetails(
                    platform=request_data.evidence_details.platform,
                    post_url=request_data.evidence_details.post_url,
                    post_date=request_data.evidence_details.post_date,
                    content_type=request_data.evidence_details.content_type,
                    engagement_metrics=CommandEngagementMetrics(
                        views=request_data.evidence_details.engagement_metrics.views,
                        likes=request_data.evidence_details.engagement_metrics.likes,
                        comments=request_data.evidence_details.engagement_metrics.comments,
                        shares=request_data.evidence_details.engagement_metrics.shares
                    )
                ),
                audience_data=CommandAudienceData(
                    followers_count=request_data.audience_data.followers_count,
                    audience_reached=request_data.audience_data.audience_reached,
                    demographics=CommandDemographics(
                        primary_country=request_data.audience_data.demographics.primary_country,
                        age_range=request_data.audience_data.demographics.age_range
                    )
                ),
                description=request_data.description
            )

            # Execute command via handler (needs Pulsar publisher injection)
            # TODO: Get Pulsar publisher from DI container
            handler = UploadEvidenceHandler(pulsar_publisher=None)  # Will be injected
            result = await handler.handle(command, user_id)

            # Convert result to response model
            return UploadEvidenceResponse(**result)

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get(
        "/evidence/health",
        tags=["health"],
        summary="Evidence Service Health Check",
        description="Check the health status of the evidence management endpoints."
    )
    async def health_check():
        """Health check for evidence router"""
        return {
            "status": "healthy",
            "service": "bff-evidence",
            "version": "0.1.0"
        }

    return router