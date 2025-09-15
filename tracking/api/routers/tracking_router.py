import time
from fastapi import APIRouter, Request, HTTPException
from ..schemas.tracking_requests import RecordTrackingEventRequest
from ..schemas.tracking_responses import RecordTrackingEventResponse
from ingestion.application.commands.record_tracking_event_command import (
    RecordTrackingEventCommand,
)


def create_tracking_router() -> APIRouter:
    """Factory function to create tracking router with dependencies"""

    router = APIRouter(prefix="/api/v1/tracking", tags=["tracking"])

    @router.post("/events", response_model=RecordTrackingEventResponse)
    async def record_tracking_event(
        request_data: RecordTrackingEventRequest, request: Request
    ) -> RecordTrackingEventResponse:
        """Record a new tracking event"""

        start_time = time.time()

        try:
            # Get command bus from DI container
            container = request.app.state.container
            command_bus = container.get("command_bus")

            # Create command
            command = RecordTrackingEventCommand(
                partner_id=request_data.partner_id,
                campaign_id=request_data.campaign_id,
                visitor_id=request_data.visitor_id,
                interaction_type=request_data.interaction_type,
                source_url=request_data.source_url,
                destination_url=request_data.destination_url,
            )

            # Execute command via command bus
            tracking_event_id = await command_bus.execute(
                "record_tracking_event", command
            )

            processing_time = (time.time() - start_time) * 1000

            return RecordTrackingEventResponse(
                tracking_event_id=tracking_event_id,
                status="recorded",
                message="Tracking event recorded successfully",
                processing_time_ms=processing_time,
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get("/health")
    async def health_check():
        """Simple health check"""
        return {"status": "healthy", "service": "tracking-service", "version": "0.1.0"}

    return router
