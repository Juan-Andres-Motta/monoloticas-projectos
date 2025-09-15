"""
Event-driven command handlers for Tracking Service.
These handlers process commands received via Pulsar events.
"""

import asyncio
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any

from messaging.schemas.avro_schemas import TrackingEventCreatedAvro
from messaging.pulsar_publisher import pulsar_publisher


class EventDrivenTrackingHandlers:
    """Event-driven handlers for tracking operations triggered by Pulsar events"""

    def __init__(self):
        pass

    async def handle_create_tracking_event_command(
        self, command_data: Dict[str, Any], message_id: str
    ):
        """Handle create tracking event command from Pulsar event"""
        try:
            print(f"🎯 Processing create tracking event command: {command_data}")

            # Extract data from Avro message
            if hasattr(command_data, "partner_id"):
                # Avro record object
                partner_id = command_data.partner_id
                campaign_id = command_data.campaign_id
                visitor_id = command_data.visitor_id
                interaction_type = command_data.interaction_type
                correlation_id = command_data.correlation_id
            else:
                # Dictionary format
                partner_id = command_data["partner_id"]
                campaign_id = command_data["campaign_id"]
                visitor_id = command_data["visitor_id"]
                interaction_type = command_data["interaction_type"]
                correlation_id = command_data.get("correlation_id")

            # Generate tracking event ID
            tracking_event_id = uuid4()

            # Here you would normally:
            # 1. Validate the tracking event data
            # 2. Store it in the database
            # 3. Apply business rules

            # Simulate storing tracking event
            print(f"💾 Storing tracking event: {tracking_event_id}")
            print(f"   Partner: {partner_id}")
            print(f"   Campaign: {campaign_id}")
            print(f"   Visitor: {visitor_id}")
            print(f"   Interaction: {interaction_type}")

            # TODO: Add actual database storage here
            # await tracking_repository.save(tracking_event)

            # Publish domain event (tracking event created)
            await self._publish_tracking_event_created(
                tracking_event_id,
                partner_id,
                campaign_id,
                visitor_id,
                interaction_type,
                correlation_id,
            )

            # Also trigger commission calculation automatically
            await self._trigger_commission_calculation(
                tracking_event_id,
                partner_id,
                campaign_id,
                interaction_type,
                correlation_id,
            )

            print(f"✅ Tracking event created successfully: {tracking_event_id}")
            print(f"🔗 Correlation ID: {correlation_id}")

            return {
                "success": True,
                "tracking_event_id": str(tracking_event_id),
                "correlation_id": correlation_id,
                "message": f"Tracking event created successfully",
            }

        except Exception as e:
            print(f"❌ Error handling create tracking event command: {e}")

            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create tracking event",
            }

    async def _publish_tracking_event_created(
        self,
        tracking_event_id: UUID,
        partner_id: str,
        campaign_id: str,
        visitor_id: str,
        interaction_type: str,
        correlation_id: str,
    ):
        """Publish tracking event created domain event"""
        try:
            # Create Avro domain event
            event = TrackingEventCreatedAvro.create(
                tracking_event_id=tracking_event_id,
                partner_id=partner_id,
                campaign_id=campaign_id,
                visitor_id=visitor_id,
                interaction_type=interaction_type,
                correlation_id=correlation_id,
            )

            # Use existing pulsar publisher to send the event
            await pulsar_publisher.publish_tracking_event(
                tracking_event_id=tracking_event_id,
                partner_id=partner_id,
                campaign_id=campaign_id,
                visitor_id=visitor_id,
                interaction_type=interaction_type,
            )

            print(f"📤 Published tracking event created: {tracking_event_id}")

        except Exception as e:
            print(f"❌ Error publishing tracking event: {e}")

    async def _trigger_commission_calculation(
        self,
        tracking_event_id: UUID,
        partner_id: str,
        campaign_id: str,
        interaction_type: str,
        correlation_id: str,
    ):
        """Trigger commission calculation by sending command to commission service"""
        try:
            # Import here to avoid circular imports
            from messaging.avro_publisher import avro_pulsar_publisher

            # Send calculate commission command
            await avro_pulsar_publisher.send_calculate_commission_command(
                tracking_event_id=tracking_event_id,
                partner_id=partner_id,
                campaign_id=campaign_id,
                interaction_type=interaction_type,
                correlation_id=correlation_id,
            )

            print(f"📤 Triggered commission calculation for: {tracking_event_id}")

        except Exception as e:
            print(f"❌ Error triggering commission calculation: {e}")


async def setup_tracking_event_handlers() -> EventDrivenTrackingHandlers:
    """Set up event-driven handlers for tracking service"""
    try:
        event_handlers = EventDrivenTrackingHandlers()
        print("✅ Tracking event handlers configured successfully")
        return event_handlers

    except Exception as e:
        print(f"❌ Error setting up tracking event handlers: {e}")
        raise


async def start_event_driven_tracking_service():
    """Start the tracking service in event-driven mode"""
    try:
        print("🚀 Starting Tracking Service in Event-Driven Mode")

        # 1. Set up event handlers
        event_handlers = await setup_tracking_event_handlers()

        # 2. Start Pulsar publisher (for publishing domain events)
        from messaging.avro_publisher import avro_pulsar_publisher

        await avro_pulsar_publisher.start()

        # 3. Set up and start consumer
        from messaging.avro_consumer import TrackingServiceConsumer

        consumer = TrackingServiceConsumer()
        await consumer.start()

        # 4. Register command handlers
        consumer.register_handlers(
            create_tracking_event_handler=event_handlers.handle_create_tracking_event_command
        )

        print("✅ Tracking Service is now listening for events!")
        print("📡 Listening for:")
        print("   - tracking.create_event.command.v1")

        # 5. Start consuming (this will run indefinitely)
        await consumer.start_consuming()

    except Exception as e:
        print(f"❌ Error starting event-driven tracking service: {e}")
        raise


async def test_tracking_commands():
    """Test function to send sample commands to the tracking service"""
    try:
        from messaging.avro_publisher import avro_pulsar_publisher

        # Start publisher for testing
        await avro_pulsar_publisher.start()

        # Test: Create tracking event
        print("🧪 Test: Sending create tracking event command...")
        correlation_id = await avro_pulsar_publisher.send_create_tracking_event_command(
            partner_id="partner-123",
            campaign_id="campaign-456",
            visitor_id="visitor-789",
            interaction_type="click",
        )
        print(
            f"✅ Create tracking event command sent, correlation ID: {correlation_id}"
        )

        print("🧪 Test command sent successfully!")
        print("📡 Check the tracking service logs to see if it was processed")

    except Exception as e:
        print(f"❌ Error testing tracking commands: {e}")
        raise


if __name__ == "__main__":
    # Run test
    asyncio.run(test_tracking_commands())
