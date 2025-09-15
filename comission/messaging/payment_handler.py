"""
Payment Request Event Handler for Commission Service
Processes payment request commands from BFF and manages commission payouts
"""

import asyncio
from uuid import UUID, uuid4
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from decimal import Decimal

from messaging.pulsar_publisher import pulsar_publisher


class PaymentRequestHandler:
    """Handler for payment request events from BFF"""

    def __init__(self):
        self.commission_records = {}  # In-memory storage for demo
        self.payment_requests = {}  # In-memory storage for demo

    async def handle_payment_request_command(
        self, command_data: Dict[str, Any], message_id: str
    ) -> Dict[str, Any]:
        """Handle payment request command from BFF"""
        try:
            print(f"🎯 Processing payment request command: {command_data}")

            # Extract data from command
            user_id = command_data.get("user_id")
            payload = command_data.get("payload", {})

            partner_id = payload["partner_id"]
            request_type = payload["request_type"]
            payment_details = payload["payment_details"]
            commission_period = payload["commission_period"]
            invoice_details = payload["invoice_details"]

            # Generate payment request ID
            payment_request_id = uuid4()

            # Calculate available commission for the period
            available_commission = await self._calculate_available_commission(
                partner_id=partner_id,
                start_date=commission_period["start_date"],
                end_date=commission_period["end_date"],
                included_campaigns=commission_period.get("included_campaigns", []),
            )

            # Validate requested amount
            requested_amount = Decimal(str(payment_details["requested_amount"]))
            if requested_amount > available_commission:
                raise ValueError(
                    f"Requested amount ${requested_amount} exceeds available commission ${available_commission}"
                )

            # Create payment request record
            payment_request = {
                "payment_request_id": str(payment_request_id),
                "partner_id": partner_id,
                "request_type": request_type,
                "requested_amount": float(requested_amount),
                "available_commission": float(available_commission),
                "currency": payment_details["currency"],
                "payment_method": payment_details["payment_method"],
                "account_info": payment_details["account_info"],
                "commission_period": commission_period,
                "invoice_details": invoice_details,
                "status": "pending_approval",
                "requested_by": user_id,
                "requested_at": datetime.utcnow().isoformat(),
                "processing_notes": [],
            }

            # Store payment request
            self.payment_requests[str(payment_request_id)] = payment_request

            print(f"💾 Payment request created: {payment_request_id}")
            print(f"   Partner: {partner_id}")
            print(f"   Amount: ${requested_amount} {payment_details['currency']}")
            print(f"   Available: ${available_commission}")
            print(f"   Method: {payment_details['payment_method']}")

            # Publish payment request created event
            await self._publish_payment_request_created(payment_request)

            # If request is for immediate payment and amount is reasonable, auto-approve
            if request_type == "immediate" and requested_amount <= Decimal("1000"):
                await self._auto_approve_payment_request(
                    payment_request_id, payment_request
                )

            print(f"✅ Payment request processed: {payment_request_id}")

            return {
                "success": True,
                "payment_request_id": str(payment_request_id),
                "partner_id": partner_id,
                "requested_amount": float(requested_amount),
                "available_commission": float(available_commission),
                "status": payment_request["status"],
                "message": f"Payment request processed successfully",
            }

        except Exception as e:
            print(f"❌ Error handling payment request command: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process payment request",
            }

    async def _calculate_available_commission(
        self,
        partner_id: str,
        start_date: str,
        end_date: str,
        included_campaigns: List[str],
    ) -> Decimal:
        """Calculate available commission for partner in given period"""
        try:
            # Simulate commission calculation
            # In real implementation, this would query the database

            # Mock commission data based on partner activity
            base_commission = Decimal("150.00")  # Base monthly commission

            # Add bonus based on included campaigns
            campaign_bonus = Decimal("25.00") * len(included_campaigns)

            # Calculate date range factor
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            days = (end - start).days

            # Pro-rate for partial months
            period_factor = Decimal(str(days)) / Decimal("30")

            total_commission = (base_commission + campaign_bonus) * period_factor

            print(f"💰 Commission calculation for {partner_id}:")
            print(f"   Base: ${base_commission}")
            print(f"   Campaign bonus: ${campaign_bonus}")
            print(f"   Period factor: {period_factor}")
            print(f"   Total available: ${total_commission}")

            return total_commission

        except Exception as e:
            print(f"❌ Error calculating commission: {e}")
            return Decimal("0.00")

    async def _publish_payment_request_created(self, payment_request: Dict[str, Any]):
        """Publish payment request created event"""
        try:
            event_data = {
                "event_type": "PaymentRequestCreated",
                "payment_request_id": payment_request["payment_request_id"],
                "partner_id": payment_request["partner_id"],
                "requested_amount": payment_request["requested_amount"],
                "currency": payment_request["currency"],
                "status": payment_request["status"],
                "created_at": payment_request["requested_at"],
            }

            # Publish to domain events topic
            await pulsar_publisher.publish_domain_event(
                event_type="PaymentRequestCreated",
                event_data=event_data,
                aggregate_id=payment_request["payment_request_id"],
            )

            print(
                f"📤 Published payment request created: {payment_request['payment_request_id']}"
            )

        except Exception as e:
            print(f"❌ Error publishing payment request event: {e}")

    async def _auto_approve_payment_request(
        self, payment_request_id: UUID, payment_request: Dict[str, Any]
    ):
        """Auto-approve small payment requests"""
        try:
            # Update status
            payment_request["status"] = "approved"
            payment_request["approved_at"] = datetime.utcnow().isoformat()
            payment_request["approved_by"] = "system"
            payment_request["processing_notes"].append("Auto-approved for small amount")

            # Simulate payment processing
            await asyncio.sleep(1)  # Simulate processing delay

            # Mark as processed
            payment_request["status"] = "processed"
            payment_request["processed_at"] = datetime.utcnow().isoformat()
            payment_request["transaction_id"] = f"txn_{uuid4().hex[:8]}"

            # Publish payment processed event
            await self._publish_payment_processed(payment_request)

            print(
                f"✅ Payment request auto-approved and processed: {payment_request_id}"
            )

        except Exception as e:
            print(f"❌ Error auto-approving payment request: {e}")

    async def _publish_payment_processed(self, payment_request: Dict[str, Any]):
        """Publish payment processed event"""
        try:
            event_data = {
                "event_type": "PaymentProcessed",
                "payment_request_id": payment_request["payment_request_id"],
                "partner_id": payment_request["partner_id"],
                "amount": payment_request["requested_amount"],
                "currency": payment_request["currency"],
                "transaction_id": payment_request["transaction_id"],
                "processed_at": payment_request["processed_at"],
            }

            # Publish to domain events topic
            await pulsar_publisher.publish_domain_event(
                event_type="PaymentProcessed",
                event_data=event_data,
                aggregate_id=payment_request["payment_request_id"],
            )

            print(
                f"📤 Published payment processed: {payment_request['payment_request_id']}"
            )

        except Exception as e:
            print(f"❌ Error publishing payment processed event: {e}")

    def get_payment_request(self, payment_request_id: str) -> Optional[Dict[str, Any]]:
        """Get payment request by ID (for testing/debugging)"""
        return self.payment_requests.get(payment_request_id)

    def list_payment_requests(
        self, partner_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List payment requests, optionally filtered by partner"""
        requests = list(self.payment_requests.values())

        if partner_id:
            requests = [r for r in requests if r["partner_id"] == partner_id]

        return requests


# Integration with existing commission service
async def setup_payment_request_handler() -> PaymentRequestHandler:
    """Set up payment request handler"""
    try:
        handler = PaymentRequestHandler()
        print("✅ Payment request handler configured successfully")
        return handler

    except Exception as e:
        print(f"❌ Error setting up payment request handler: {e}")
        raise


async def start_enhanced_commission_service():
    """Start the commission service with payment request handling"""
    try:
        print("🚀 Starting Enhanced Commission Service (with Payment Requests)")

        # 1. Set up payment request handler
        payment_handler = await setup_payment_request_handler()

        # 2. Start Pulsar publisher
        await pulsar_publisher.start()

        # 3. Set up and start consumer
        from messaging.avro_consumer import CommissionServiceConsumer

        consumer = CommissionServiceConsumer()
        await consumer.start()

        # 4. Register existing commission handlers
        # TODO: Import existing commission calculation handlers
        # consumer.register_handlers(
        #     calculate_commission_handler=existing_handler.handle_calculate_commission_command
        # )

        # Register BFF command handlers
        consumer.register_command_handler(
            "request_payment", payment_handler.handle_payment_request_command
        )

        print("✅ Enhanced Commission Service is now listening for events!")
        print("📡 Listening for:")
        print("   - commission.calculate.command.v1")
        print("   - request_payment (from BFF)")

        # 5. Start consuming (this will run indefinitely)
        await consumer.start_consuming()

    except Exception as e:
        print(f"❌ Error starting enhanced commission service: {e}")
        raise


if __name__ == "__main__":
    # Run enhanced commission service
    asyncio.run(start_enhanced_commission_service())
