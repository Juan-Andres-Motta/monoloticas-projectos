"""
Event-driven command handlers for Campaign Service.
These handlers process commands received via Pulsar events from the BFF.
"""

import asyncio
import json
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any, Optional

from campaign.domain.aggregates.campaign import (
    Campaign,
    PartnerType,
    CommissionType,
    AcceptanceTerms,
)
from campaign.domain.repositories.campaign_repository import CampaignRepository
from messaging.pulsar_publisher import PulsarPublisher


class EventDrivenCampaignHandlers:
    """Event-driven handlers for campaign operations triggered by Pulsar events"""

    def __init__(
        self, campaign_repository: CampaignRepository, publisher: PulsarPublisher
    ):
        self.campaign_repository = campaign_repository
        self.publisher = publisher

    async def handle_campaign_accept_command(
        self, command_data: Dict[str, Any], message_id: str
    ) -> Dict[str, Any]:
        """Handle campaign accept command from BFF"""
        try:
            print(f"🎯 Processing campaign accept command: {command_data}")

            # Extract data from command
            user_id = command_data.get("user_id")
            payload = command_data.get("payload", {})

            campaign_id = UUID(payload["campaign_id"])
            partner_id = payload["partner_id"]
            partner_type = PartnerType(payload["partner_type"])
            acceptance_terms_data = payload["acceptance_terms"]
            estimated_monthly_reach = payload["estimated_monthly_reach"]

            # Convert acceptance terms
            acceptance_terms = AcceptanceTerms(
                commission_type=CommissionType(
                    acceptance_terms_data["commission_type"]
                ),
                commission_rate=acceptance_terms_data["commission_rate"],
                cookie_duration_days=acceptance_terms_data["cookie_duration_days"],
                promotional_methods=acceptance_terms_data["promotional_methods"],
            )

            # Get or create campaign
            campaign = await self.campaign_repository.get_by_id(campaign_id)
            if not campaign:
                # Create new campaign if it doesn't exist
                campaign = Campaign.create(
                    campaign_id=campaign_id,
                    name=f"Campaign {campaign_id}",
                    description="Campaign created via partner acceptance",
                )

            # Accept partner for campaign
            campaign.accept_partner(
                partner_id=partner_id,
                partner_type=partner_type,
                acceptance_terms=acceptance_terms,
                estimated_monthly_reach=estimated_monthly_reach,
                user_id=user_id,
            )

            # Save campaign (this should also publish domain events)
            await self.campaign_repository.save(campaign)

            # Publish domain events
            await self._publish_domain_events(campaign)

            print(f"✅ Campaign acceptance processed successfully: {campaign_id}")
            print(f"   Partner: {partner_id}")
            print(f"   Type: {partner_type}")

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "partner_id": partner_id,
                "message": "Campaign acceptance processed successfully",
            }

        except Exception as e:
            print(f"❌ Error handling campaign accept command: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process campaign acceptance",
            }

    async def handle_create_campaign_command(
        self, command_data: Dict[str, Any], message_id: str
    ) -> Dict[str, Any]:
        """Handle create campaign command"""
        try:
            print(f"🎯 Processing create campaign command: {command_data}")

            # Extract data from command (Avro format)
            if hasattr(command_data, "campaign_id"):
                # Avro record object
                campaign_id = UUID(command_data.campaign_id)
                name = command_data.name
                description = getattr(command_data, "description", "")
                user_id = getattr(command_data, "user_id", None)
            else:
                # Dictionary format
                payload = command_data.get("payload", command_data)
                campaign_id = UUID(payload["campaign_id"])
                name = payload["name"]
                description = payload.get("description", "")
                user_id = command_data.get("user_id")

            # Create campaign
            campaign = Campaign.create(
                campaign_id=campaign_id, name=name, description=description
            )

            # Save campaign
            await self.campaign_repository.save(campaign)

            # Publish domain events
            await self._publish_domain_events(campaign)

            print(f"✅ Campaign created successfully: {campaign_id}")

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "name": name,
                "message": "Campaign created successfully",
            }

        except Exception as e:
            print(f"❌ Error handling create campaign command: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create campaign",
            }

    async def handle_add_video_command(
        self, command_data: Dict[str, Any], message_id: str
    ) -> Dict[str, Any]:
        """Handle add video URL command"""
        try:
            print(f"🎯 Processing add video command: {command_data}")

            # Extract data from command
            if hasattr(command_data, "campaign_id"):
                # Avro record object
                campaign_id = UUID(command_data.campaign_id)
                video_url = command_data.video_url
                user_id = getattr(command_data, "user_id", "system")
            else:
                # Dictionary format
                payload = command_data.get("payload", command_data)
                campaign_id = UUID(payload["campaign_id"])
                video_url = payload["video_url"]
                user_id = command_data.get("user_id", "system")

            # Get campaign
            campaign = await self.campaign_repository.get_by_id(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")

            # Add video URL
            campaign.add_video_url(video_url, user_id)

            # Save campaign
            await self.campaign_repository.save(campaign)

            # Publish domain events
            await self._publish_domain_events(campaign)

            print(f"✅ Video added successfully to campaign: {campaign_id}")

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "video_url": video_url,
                "message": "Video URL added successfully",
            }

        except Exception as e:
            print(f"❌ Error handling add video command: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to add video URL",
            }

    async def _publish_domain_events(self, campaign: Campaign) -> None:
        """Publish domain events for the campaign"""
        try:
            for event in campaign.events:
                # Convert domain event to publishable format
                event_data = event.to_dict()

                # Publish to appropriate topic based on event type
                await self.publisher.publish_domain_event(
                    event_type=event_data["event_type"],
                    event_data=event_data,
                    aggregate_id=str(event.aggregate_id),
                )

            # Clear events after publishing
            campaign.clear_events()

        except Exception as e:
            print(f"❌ Error publishing domain events: {e}")


async def setup_campaign_event_handlers(
    campaign_repository: CampaignRepository, publisher: PulsarPublisher
) -> EventDrivenCampaignHandlers:
    """Set up event-driven handlers for campaign service"""
    try:
        event_handlers = EventDrivenCampaignHandlers(campaign_repository, publisher)
        print("✅ Campaign event handlers configured successfully")
        return event_handlers

    except Exception as e:
        print(f"❌ Error setting up campaign event handlers: {e}")
        raise


async def start_event_driven_campaign_service():
    """Start the campaign service in event-driven mode"""
    try:
        print("🚀 Starting Campaign Service in Event-Driven Mode")

        # 1. Initialize dependencies (repository, publisher)
        # TODO: Get these from DI container
        from campaign.infrastructure.repositories.memory_campaign_repository import (
            MemoryCampaignRepository,
        )
        from messaging.pulsar_publisher import pulsar_publisher

        campaign_repository = MemoryCampaignRepository()
        await pulsar_publisher.start()

        # 2. Set up event handlers
        event_handlers = await setup_campaign_event_handlers(
            campaign_repository, pulsar_publisher
        )

        # 3. Set up and start consumer
        from messaging.avro_consumer import CampaignServiceConsumer

        consumer = CampaignServiceConsumer()
        await consumer.start()

        # 4. Register command handlers
        consumer.register_handlers(
            create_campaign_handler=event_handlers.handle_create_campaign_command,
            add_video_handler=event_handlers.handle_add_video_command,
        )

        # 5. Register BFF command handlers
        consumer.register_command_handler(
            "accept_campaign", event_handlers.handle_campaign_accept_command
        )

        print("✅ Campaign Service is now listening for events!")
        print("📡 Listening for:")
        print("   - campaign.create.command.v1")
        print("   - campaign.add_video.command.v1")
        print("   - accept_campaign (from BFF)")

        # 6. Start consuming (this will run indefinitely)
        await consumer.start_consuming()

    except Exception as e:
        print(f"❌ Error starting event-driven campaign service: {e}")
        raise


if __name__ == "__main__":
    # Run campaign service in event-driven mode
    asyncio.run(start_event_driven_campaign_service())
