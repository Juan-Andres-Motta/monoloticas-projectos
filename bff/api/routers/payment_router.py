from fastapi import APIRouter, HTTPException, Depends
from ..schemas.requests.payment_requests import RequestPaymentRequest
from ..schemas.responses.payment_responses import RequestPaymentResponse
from ...application.commands.request_payment_command import (
    RequestPaymentCommand,
    PaymentDetails as CommandPaymentDetails,
    AccountInfo as CommandAccountInfo,
    CommissionPeriod as CommandCommissionPeriod,
    InvoiceDetails as CommandInvoiceDetails
)
from ...application.handlers.request_payment_handler import RequestPaymentHandler
from ...config.jwt_auth import JWTAuth


def create_payment_router() -> APIRouter:
    """Factory function to create payment router"""

    router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

    @router.post(
        "/request",
        response_model=RequestPaymentResponse,
        summary="Request Partner Payment",
        description="""
        Submit a payment request for earned commissions.

        This endpoint allows partners to request payment for their earned commissions
        within a specific period. The request includes payment details, account information,
        and optional invoice requirements for processing.

        **Required Authentication:** JWT token with valid user_id
        """,
        dependencies=[Depends(JWTAuth.extract_user_id)]
    )
    async def request_payment(
        request_data: RequestPaymentRequest,
        user_id: str = Depends(JWTAuth.extract_user_id)
    ) -> RequestPaymentResponse:

        try:
            # Convert request to command
            command = RequestPaymentCommand(
                partner_id=request_data.partner_id,
                request_type=request_data.request_type,
                payment_details=CommandPaymentDetails(
                    requested_amount=request_data.payment_details.requested_amount,
                    currency=request_data.payment_details.currency,
                    payment_method=request_data.payment_details.payment_method,
                    account_info=CommandAccountInfo(
                        account_type=request_data.payment_details.account_info.account_type,
                        last_four_digits=request_data.payment_details.account_info.last_four_digits,
                        account_holder=request_data.payment_details.account_info.account_holder
                    )
                ),
                commission_period=CommandCommissionPeriod(
                    start_date=request_data.commission_period.start_date,
                    end_date=request_data.commission_period.end_date,
                    included_campaigns=request_data.commission_period.included_campaigns
                ),
                invoice_details=CommandInvoiceDetails(
                    invoice_required=request_data.invoice_details.invoice_required,
                    tax_id=request_data.invoice_details.tax_id,
                    business_name=request_data.invoice_details.business_name
                )
            )

            # Execute command via handler (needs Pulsar publisher injection)
            # TODO: Get Pulsar publisher from DI container
            handler = RequestPaymentHandler(pulsar_publisher=None)  # Will be injected
            result = await handler.handle(command, user_id)

            # Convert result to response model
            return RequestPaymentResponse(**result)

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    @router.get(
        "/health",
        tags=["health"],
        summary="Payment Service Health Check",
        description="Check the health status of the payment management endpoints."
    )
    async def health_check():
        """Health check for payment router"""
        return {
            "status": "healthy",
            "service": "bff-payments",
            "version": "0.1.0"
        }

    return router