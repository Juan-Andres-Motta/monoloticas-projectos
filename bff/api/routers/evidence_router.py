from fastapi import APIRouter, HTTPException, Depends, Request
from api.schemas.requests.evidence_requests import UploadEvidenceRequest
from api.schemas.responses.evidence_responses import UploadEvidenceResponse
from config.jwt_auth import JWTAuth
from uuid import uuid4


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
        dependencies=[Depends(JWTAuth.extract_user_id)],
    )
    async def upload_evidence(
        campaign_id: str,
        request_data: UploadEvidenceRequest,
        request: Request,
        user_id: str = Depends(JWTAuth.extract_user_id),
    ) -> UploadEvidenceResponse:

        try:
            # Get Pulsar publisher from app state
            pulsar_publisher = getattr(request.app.state, "pulsar_publisher", None)
            if not pulsar_publisher:
                raise HTTPException(
                    status_code=503, detail="Event publishing service unavailable"
                )

            # Generate command ID for tracking
            command_id = str(uuid4())

            # Publish evidence upload command to Pulsar
            await pulsar_publisher.publish_evidence_upload_command(
                user_id=user_id,
                partner_id=request_data.partner_id,
                campaign_id=campaign_id,
                evidence_type=request_data.evidence_type,
                evidence_details={
                    "platform": request_data.evidence_details.platform,
                    "post_url": request_data.evidence_details.post_url,
                    "post_date": (
                        request_data.evidence_details.post_date.isoformat()
                        if request_data.evidence_details.post_date
                        else None
                    ),
                    "content_type": request_data.evidence_details.content_type,
                    "engagement_metrics": {
                        "views": request_data.evidence_details.engagement_metrics.views,
                        "likes": request_data.evidence_details.engagement_metrics.likes,
                        "comments": request_data.evidence_details.engagement_metrics.comments,
                        "shares": request_data.evidence_details.engagement_metrics.shares,
                    },
                },
                audience_data={
                    "followers_count": request_data.audience_data.followers_count,
                    "audience_reached": request_data.audience_data.audience_reached,
                    "demographics": {
                        "primary_country": request_data.audience_data.demographics.primary_country,
                        "age_range": request_data.audience_data.demographics.age_range,
                    },
                },
                description=request_data.description,
            )

            # Return immediate response (async processing)
            return UploadEvidenceResponse(
                command_id=command_id,
                status="submitted",
                message="Evidence upload submitted for processing",
                partner_id=request_data.partner_id,
                campaign_id=campaign_id,
                evidence_type=request_data.evidence_type,
                processing_status="async",
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get(
        "/evidence/health",
        tags=["health"],
        summary="Evidence Service Health Check",
        description="Check the health status of the evidence management endpoints.",
    )
    async def health_check():
        """Health check for evidence router"""
        return {"status": "healthy", "service": "bff-evidence", "version": "0.1.0"}

    return router
