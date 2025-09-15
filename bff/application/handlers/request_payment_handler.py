from ..commands.request_payment_command import RequestPaymentCommand


class RequestPaymentHandler:
    """Handler for requesting partner payments - publishes to Pulsar"""

    def __init__(self, pulsar_publisher=None):
        self._pulsar_publisher = pulsar_publisher

    async def handle(self, command: RequestPaymentCommand, user_id: str) -> dict:
        """Handle payment request command by publishing to Pulsar"""

        if not self._pulsar_publisher:
            raise Exception("Pulsar publisher not available")

        try:
            # Convert command objects to dicts for JSON serialization
            payment_details_dict = {
                "requested_amount": float(command.payment_details.requested_amount),
                "currency": command.payment_details.currency,
                "payment_method": command.payment_details.payment_method,
                "account_info": {
                    "account_type": command.payment_details.account_info.account_type,
                    "last_four_digits": command.payment_details.account_info.last_four_digits,
                    "account_holder": command.payment_details.account_info.account_holder
                }
            }

            commission_period_dict = {
                "start_date": command.commission_period.start_date.isoformat(),
                "end_date": command.commission_period.end_date.isoformat(),
                "included_campaigns": command.commission_period.included_campaigns
            }

            invoice_details_dict = {
                "invoice_required": command.invoice_details.invoice_required,
                "tax_id": command.invoice_details.tax_id,
                "business_name": command.invoice_details.business_name
            }

            # Publish command to Pulsar
            command_id = await self._pulsar_publisher.publish_payment_request_command(
                user_id=user_id,
                partner_id=command.partner_id,
                request_type=command.request_type,
                payment_details=payment_details_dict,
                commission_period=commission_period_dict,
                invoice_details=invoice_details_dict
            )

            # Return immediate response with command tracking info
            response = {
                "command_id": command_id,
                "status": "PROCESSING",
                "message": "Payment request submitted successfully",
                "partner_id": command.partner_id,
                "user_id": user_id,
                "request_type": command.request_type,
                "requested_amount": float(command.payment_details.requested_amount),
                "currency": command.payment_details.currency
            }

            return response

        except Exception as e:
            print(f"❌ Error publishing payment request command: {e}")
            raise