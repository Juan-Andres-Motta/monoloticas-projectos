import time
from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional
from uuid import UUID

from ..schemas.commission_requests import CalculateCommissionRequest
from ..schemas.commission_responses import (
    CalculateCommissionResponse,
    CommissionResponse,
    CommissionListResponse,
)
from commission.application.commands.calculate_commission_command import (
    CalculateCommissionCommand,
)


def create_commission_router() -> APIRouter:
    """Factory function to create commission router with dependencies"""

    router = APIRouter(prefix="/api/v1/commissions", tags=["commissions"])

    @router.post("/calculate", response_model=CalculateCommissionResponse)
    async def calculate_commission(
        request_data: CalculateCommissionRequest, request: Request
    ) -> CalculateCommissionResponse:
        """Calculate commission for a tracking event"""

        start_time = time.time()

        try:
            # Get command bus from DI container
            container = request.app.state.container
            command_bus = container.get("command_bus")

            # Create command
            command = CalculateCommissionCommand(
                tracking_event_id=request_data.tracking_event_id,
                partner_id=request_data.partner_id,
                campaign_id=request_data.campaign_id,
                visitor_id=request_data.visitor_id,
                interaction_type=request_data.interaction_type,
            )

            # Execute command via command bus
            commission_id = await command_bus.execute("calculate_commission", command)

            processing_time = (time.time() - start_time) * 1000

            return CalculateCommissionResponse(
                commission_id=commission_id,
                status="calculated",
                message="Commission calculated successfully",
                processing_time_ms=processing_time,
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get("/{commission_id}", response_model=CommissionResponse)
    async def get_commission(
        commission_id: UUID, request: Request
    ) -> CommissionResponse:
        """Get commission by ID"""

        try:
            container = request.app.state.container
            repository = container.get("commission_repository")

            commission = await repository.find_by_id(commission_id)
            if not commission:
                raise HTTPException(status_code=404, detail="Commission not found")

            return CommissionResponse(
                commission_id=commission.commission_id,
                tracking_event_id=commission.tracking_event_id,
                partner_id=commission.partner_id,
                campaign_id=commission.campaign_id,
                visitor_id=commission.visitor_id,
                interaction_type=commission.interaction_type,
                commission_amount=commission.commission_amount,
                commission_rate=commission.commission_rate,
                currency=commission.currency,
                status=commission.status,
                calculated_at=commission.calculated_at,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get("/partner/{partner_id}", response_model=CommissionListResponse)
    async def get_commissions_by_partner(
        partner_id: str,
        request: Request,
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100),
    ) -> CommissionListResponse:
        """Get commissions by partner ID"""

        try:
            container = request.app.state.container
            repository = container.get("commission_repository")

            commissions = await repository.find_by_partner_id(partner_id, page_size)

            commission_responses = [
                CommissionResponse(
                    commission_id=c.commission_id,
                    tracking_event_id=c.tracking_event_id,
                    partner_id=c.partner_id,
                    campaign_id=c.campaign_id,
                    visitor_id=c.visitor_id,
                    interaction_type=c.interaction_type,
                    commission_amount=c.commission_amount,
                    commission_rate=c.commission_rate,
                    currency=c.currency,
                    status=c.status,
                    calculated_at=c.calculated_at,
                )
                for c in commissions
            ]

            return CommissionListResponse(
                commissions=commission_responses,
                total_count=len(commission_responses),
                page=page,
                page_size=page_size,
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get("/campaign/{campaign_id}", response_model=CommissionListResponse)
    async def get_commissions_by_campaign(
        campaign_id: str,
        request: Request,
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100),
    ) -> CommissionListResponse:
        """Get commissions by campaign ID"""

        try:
            container = request.app.state.container
            repository = container.get("commission_repository")

            commissions = await repository.find_by_campaign_id(campaign_id, page_size)

            commission_responses = [
                CommissionResponse(
                    commission_id=c.commission_id,
                    tracking_event_id=c.tracking_event_id,
                    partner_id=c.partner_id,
                    campaign_id=c.campaign_id,
                    visitor_id=c.visitor_id,
                    interaction_type=c.interaction_type,
                    commission_amount=c.commission_amount,
                    commission_rate=c.commission_rate,
                    currency=c.currency,
                    status=c.status,
                    calculated_at=c.calculated_at,
                )
                for c in commissions
            ]

            return CommissionListResponse(
                commissions=commission_responses,
                total_count=len(commission_responses),
                page=page,
                page_size=page_size,
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get("/health")
    async def health_check():
        """Simple health check"""
        return {
            "status": "healthy",
            "service": "commission-service",
            "version": "0.1.0",
        }

    return router
