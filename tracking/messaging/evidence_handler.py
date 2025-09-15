"""
Evidence Upload Event Handler for Tracking Service
Processes evidence upload commands from BFF and creates tracking records
"""

import asyncio
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any, Optional

from messaging.schemas.avro_schemas import TrackingEventCreatedAvro
from messaging.pulsar_publisher import pulsar_publisher


class EvidenceTrackingHandler:
    """Handler for evidence upload events to create tracking records"""

    def __init__(self):
        pass

    async def handle_evidence_upload_command(
        self, command_data: Dict[str, Any], message_id: str
    ) -> Dict[str, Any]:
        """Handle evidence upload command from BFF"""
        try:
            print(f"🎯 Processing evidence upload command: {command_data}")

            # Extract data from command
            user_id = command_data.get("user_id")
            payload = command_data.get("payload", {})

            partner_id = payload["partner_id"]
            campaign_id = payload["campaign_id"]
            evidence_type = payload["evidence_type"]
            evidence_details = payload["evidence_details"]
            audience_data = payload["audience_data"]
            description = payload.get("description", "")

            # Generate tracking event ID
            tracking_event_id = uuid4()

            # Create tracking record for evidence upload
            tracking_data = {
                "tracking_event_id": str(tracking_event_id),
                "partner_id": partner_id,
                "campaign_id": campaign_id,
                "visitor_id": f"evidence-{tracking_event_id}",  # Special visitor ID for evidence
                "interaction_type": "evidence_upload",
                "evidence_type": evidence_type,
                "evidence_details": evidence_details,
                "audience_data": audience_data,
                "description": description,
                "uploaded_by": user_id,
                "uploaded_at": datetime.utcnow().isoformat(),
            }

            # Store tracking record (simulate database storage)
            print(f"💾 Storing evidence tracking record: {tracking_event_id}")
            print(f"   Partner: {partner_id}")
            print(f"   Campaign: {campaign_id}")
            print(f"   Evidence Type: {evidence_type}")
            print(f"   Platform: {evidence_details.get('platform', 'N/A')}")
            print(
                f"   Views: {evidence_details.get('engagement_metrics', {}).get('views', 0)}"
            )

            # TODO: Add actual database storage here
            # await tracking_repository.save(tracking_data)

            # Publish tracking event created domain event
            await self._publish_tracking_event_created(
                tracking_event_id=tracking_event_id,
                partner_id=partner_id,
                campaign_id=campaign_id,
                interaction_type="evidence_upload",
                evidence_data=tracking_data,
            )

            # Trigger commission calculation based on evidence
            await self._trigger_commission_calculation_for_evidence(
                tracking_event_id=tracking_event_id,
                partner_id=partner_id,
                campaign_id=campaign_id,
                evidence_details=evidence_details,
                audience_data=audience_data,
            )

            print(f"✅ Evidence upload processed successfully: {tracking_event_id}")

            return {
                "success": True,
                "tracking_event_id": str(tracking_event_id),
                "partner_id": partner_id,
                "campaign_id": campaign_id,
                "evidence_type": evidence_type,
                "message": "Evidence upload processed and tracking record created",
            }

        except Exception as e:
            print(f"❌ Error handling evidence upload command: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process evidence upload",
            }

    async def _publish_tracking_event_created(
        self,
        tracking_event_id: UUID,
        partner_id: str,
        campaign_id: str,
        interaction_type: str,
        evidence_data: Dict[str, Any],
    ):
        """Publish tracking event created domain event"""
        try:
            # Use existing pulsar publisher to send the event
            await pulsar_publisher.publish_tracking_event(
                tracking_event_id=tracking_event_id,
                partner_id=partner_id,
                campaign_id=campaign_id,
                visitor_id=f"evidence-{tracking_event_id}",
                interaction_type=interaction_type,
                metadata=evidence_data,
            )

            print(f"📤 Published tracking event created: {tracking_event_id}")

        except Exception as e:
            print(f"❌ Error publishing tracking event: {e}")

    async def _trigger_commission_calculation_for_evidence(
        self,
        tracking_event_id: UUID,
        partner_id: str,
        campaign_id: str,
        evidence_details: Dict[str, Any],
        audience_data: Dict[str, Any],
    ):
        """Trigger commission calculation based on evidence metrics"""
        try:
            # Calculate commission base on evidence metrics
            engagement_metrics = evidence_details.get("engagement_metrics", {})
            views = engagement_metrics.get("views", 0)
            likes = engagement_metrics.get("likes", 0)
            shares = engagement_metrics.get("shares", 0)

            # Simple commission calculation logic
            commission_base = views * 0.001 + likes * 0.01 + shares * 0.05
            audience_reached = audience_data.get("audience_reached", 0)
            reach_bonus = audience_reached * 0.0005

            estimated_commission = commission_base + reach_bonus

            # Import here to avoid circular imports
            from messaging.avro_publisher import avro_pulsar_publisher

            # Send calculate commission command
            await avro_pulsar_publisher.send_calculate_commission_command(
                tracking_event_id=tracking_event_id,
                partner_id=partner_id,
                campaign_id=campaign_id,
                interaction_type="evidence_upload",
                commission_data={
                    "base_amount": commission_base,
                    "reach_bonus": reach_bonus,
                    "estimated_total": estimated_commission,
                    "evidence_type": evidence_details.get("content_type", "unknown"),
                    "platform": evidence_details.get("platform", "unknown"),
                    "metrics": engagement_metrics,
                    "audience_data": audience_data,
                },
            )

            print(
                f"📤 Triggered commission calculation for evidence: {tracking_event_id}"
            )
            print(f"   Estimated commission: ${estimated_commission:.2f}")

        except Exception as e:
            print(f"❌ Error triggering commission calculation: {e}")


# Integration with existing tracking service event handlers
async def setup_evidence_tracking_handler() -> EvidenceTrackingHandler:
    """Set up evidence tracking handler"""
    try:
        handler = EvidenceTrackingHandler()
        print("✅ Evidence tracking handler configured successfully")
        return handler

    except Exception as e:
        print(f"❌ Error setting up evidence tracking handler: {e}")
        raise


async def start_enhanced_tracking_service():
    """Start the tracking service with evidence handling capabilities"""
    try:
        print("🚀 Starting Enhanced Tracking Service (with Evidence Handling)")

        # 1. Set up evidence handler
        evidence_handler = await setup_evidence_tracking_handler()

        # 2. Start existing tracking service components
        from messaging.event_handlers import setup_tracking_event_handlers

        tracking_handlers = await setup_tracking_event_handlers()

        # 3. Start Pulsar publisher
        from messaging.avro_publisher import avro_pulsar_publisher

        await avro_pulsar_publisher.start()

        # 4. Set up and start consumer
        from messaging.avro_consumer import TrackingServiceConsumer

        consumer = TrackingServiceConsumer()
        await consumer.start()

        # 5. Register all command handlers
        consumer.register_handlers(
            create_tracking_event_handler=tracking_handlers.handle_create_tracking_event_command
        )

        # Register BFF command handlers
        consumer.register_command_handler(
            "upload_evidence", evidence_handler.handle_evidence_upload_command
        )

        print("✅ Enhanced Tracking Service is now listening for events!")
        print("📡 Listening for:")
        print("   - tracking.create_event.command.v1")
        print("   - upload_evidence (from BFF)")

        # 6. Start consuming (this will run indefinitely)
        await consumer.start_consuming()

    except Exception as e:
        print(f"❌ Error starting enhanced tracking service: {e}")
        raise


if __name__ == "__main__":
    # Run enhanced tracking service
    asyncio.run(start_enhanced_tracking_service())
