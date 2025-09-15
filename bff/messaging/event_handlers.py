"""
Event-driven command handlers for Campaign Service.
These handlers process commands received via Pulsar events instead of HTTP endpoints.
"""

import asyncio
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any

from campaign.application.handlers.create_campaign_handler import CreateCampaignHandler
from campaign.application.handlers.add_video_url_handler import AddVideoUrlHandler
from campaign.application.commands.create_campaign_command import CreateCampaignCommand
from campaign.application.commands.add_video_url_command import AddVideoUrlCommand
from messaging.avro_publisher import avro_pulsar_publisher


class EventDrivenCampaignHandlers:
    """Event-driven handlers for campaign operations triggered by Pulsar events"""

    def __init__(
        self,
        create_handler: CreateCampaignHandler,
        add_video_handler: AddVideoUrlHandler,
    ):
        self.create_handler = create_handler
        self.add_video_handler = add_video_handler

    async def handle_create_campaign_command(
        self, command_data: Dict[str, Any], message_id: str
    ):
        """Handle create campaign command from Pulsar event"""
        try:
            print(f"🎯 Processing create campaign command: {command_data}")

            # Extract data from Avro message
            if hasattr(command_data, "campaign_id"):
                # Avro record object
                campaign_id = UUID(command_data.campaign_id)
                user_id = command_data.user_id
                name = command_data.name
                description = command_data.description
                correlation_id = command_data.correlation_id
            else:
                # Dictionary format
                campaign_id = UUID(command_data["campaign_id"])
                user_id = command_data["user_id"]
                name = command_data["name"]
                description = command_data.get("description", "")
                correlation_id = command_data.get("correlation_id")

            # Create application command
            app_command = CreateCampaignCommand(
                campaign_id=campaign_id,
                user_id=user_id,
                name=name,
                description=description,
            )

            # Execute command through existing application handler
            result_campaign_id = await self.create_handler.handle(app_command)

            print(f"✅ Campaign created successfully: {result_campaign_id}")
            print(f"🔗 Correlation ID: {correlation_id}")

            return {
                "success": True,
                "campaign_id": str(result_campaign_id),
                "correlation_id": correlation_id,
                "message": f"Campaign '{name}' created successfully",
            }

        except Exception as e:
            print(f"❌ Error handling create campaign command: {e}")

            # You could publish a failure event here
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create campaign",
            }

    async def handle_add_video_url_command(
        self, command_data: Dict[str, Any], message_id: str
    ):
        """Handle add video URL command from Pulsar event"""
        try:
            print(f"🎯 Processing add video URL command: {command_data}")

            # Extract data from Avro message
            if hasattr(command_data, "campaign_id"):
                # Avro record object
                campaign_id = UUID(command_data.campaign_id)
                video_url = command_data.video_url
                correlation_id = command_data.correlation_id
            else:
                # Dictionary format
                campaign_id = UUID(command_data["campaign_id"])
                video_url = command_data["video_url"]
                correlation_id = command_data.get("correlation_id")

            # Create application command
            app_command = AddVideoUrlCommand(
                campaign_id=campaign_id, video_url=video_url
            )

            # Execute command through existing application handler
            await self.add_video_handler.handle(app_command)

            print(f"✅ Video URL added successfully: {video_url}")
            print(f"🔗 Correlation ID: {correlation_id}")

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "video_url": video_url,
                "correlation_id": correlation_id,
                "message": f"Video URL '{video_url}' added successfully",
            }

        except Exception as e:
            print(f"❌ Error handling add video URL command: {e}")

            return {
                "success": False,
                "error": str(e),
                "message": "Failed to add video URL",
            }


async def setup_campaign_event_handlers(container) -> EventDrivenCampaignHandlers:
    """Set up event-driven handlers for campaign service using dependency injection"""
    try:
        # Get handlers from container (dependency injection)
        create_handler = container.get("campaign_create_handler")
        add_video_handler = container.get("add_video_handler")

        # Create event-driven wrapper
        event_handlers = EventDrivenCampaignHandlers(create_handler, add_video_handler)

        print("✅ Campaign event handlers configured successfully")
        return event_handlers

    except Exception as e:
        print(f"❌ Error setting up campaign event handlers: {e}")
        raise


# =============================================================================
# INTEGRATION EXAMPLE - How to integrate with existing service
# =============================================================================


async def start_event_driven_campaign_service(container):
    """
    Start the campaign service in event-driven mode.
    This replaces the HTTP API endpoints with event consumers.
    """
    try:
        print("🚀 Starting Campaign Service in Event-Driven Mode")

        # 1. Set up event handlers
        event_handlers = await setup_campaign_event_handlers(container)

        # 2. Start Pulsar publisher (for publishing domain events)
        await avro_pulsar_publisher.start()

        # 3. Set up and start consumer
        from messaging.avro_consumer import CampaignServiceConsumer

        consumer = CampaignServiceConsumer()
        await consumer.start()

        # 4. Register command handlers
        consumer.register_handlers(
            create_campaign_handler=event_handlers.handle_create_campaign_command,
            add_video_handler=event_handlers.handle_add_video_url_command,
        )

        print("✅ Campaign Service is now listening for events!")
        print("📡 Listening for:")
        print("   - campaign.create.command.v1")
        print("   - campaign.add_video.command.v1")

        # 5. Start consuming (this will run indefinitely)
        await consumer.start_consuming()

    except Exception as e:
        print(f"❌ Error starting event-driven campaign service: {e}")
        raise


# =============================================================================
# TESTING UTILITY
# =============================================================================


async def test_campaign_commands():
    """Test function to send sample commands to the campaign service"""
    try:
        # Start publisher for testing
        await avro_pulsar_publisher.start()

        # Test 1: Create campaign
        print("🧪 Test 1: Sending create campaign command...")
        correlation_id_1 = await avro_pulsar_publisher.send_create_campaign_command(
            campaign_id=uuid4(),
            user_id="test-user-123",
            name="Test Campaign from Event",
            description="This campaign was created via Pulsar event",
        )
        print(f"✅ Create campaign command sent, correlation ID: {correlation_id_1}")

        # Wait a bit
        await asyncio.sleep(2)

        # Test 2: Add video URL
        print("🧪 Test 2: Sending add video URL command...")
        test_campaign_id = uuid4()
        correlation_id_2 = await avro_pulsar_publisher.send_add_video_url_command(
            campaign_id=test_campaign_id,
            video_url="https://youtube.com/watch?v=event-test-123",
        )
        print(f"✅ Add video URL command sent, correlation ID: {correlation_id_2}")

        print("🧪 Test commands sent successfully!")
        print("📡 Check the campaign service logs to see if they were processed")

    except Exception as e:
        print(f"❌ Error testing campaign commands: {e}")
        raise


if __name__ == "__main__":
    # Run test
    asyncio.run(test_campaign_commands())
