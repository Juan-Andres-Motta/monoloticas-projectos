"""
Event-driven Pulsar consumer using Avro schemas.
This consumer listens to command events and triggers operations in the microservice.
"""

import pulsar
import asyncio
from typing import Callable, Dict, Any
from uuid import UUID

from config.pulsar_config import PulsarConfig
from messaging.schemas.avro_schemas import (
    AvroSchemaRegistry,
    PulsarTopics,
    CreateCampaignCommandAvro,
    AddVideoUrlCommandAvro,
    CreateTrackingEventCommandAvro,
    CalculateCommissionCommandAvro,
    ProcessPaymentCommandAvro,
)


class AvroPulsarConsumer:
    """Pulsar consumer with Avro schema support for event-driven architecture"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._client = None
        self._consumers = {}
        self._command_handlers = {}
        self._running = False

    async def start(self):
        """Initialize Pulsar client"""
        try:
            # Create Pulsar client with DataStax Astra Streaming
            client_config = PulsarConfig.get_client_config()
            self._client = pulsar.Client(**client_config)

            print(f"✅ Started Avro Pulsar consumer for {self.service_name} service")

        except Exception as e:
            print(f"❌ Failed to start Avro Pulsar consumer: {e}")
            raise

    def register_command_handler(self, command_type: str, handler: Callable):
        """Register a handler function for a specific command type"""
        self._command_handlers[command_type] = handler
        print(f"📋 Registered command handler for: {command_type}")

    async def subscribe_to_commands(self):
        """Subscribe to command topic for this service"""
        try:
            command_topic = PulsarTopics.get_command_topic(self.service_name)
            subscription_name = f"{self.service_name}-command-consumer"

            # Try different topic configurations
            topics_to_try = PulsarConfig.get_topic_options(command_topic)

            for full_topic in topics_to_try:
                try:
                    print(f"📡 Attempting to subscribe to command topic: {full_topic}")

                    # Create consumer with string schema for maximum flexibility
                    # Note: In production, you might want separate consumers per command type
                    consumer = self._client.subscribe(
                        full_topic,
                        subscription_name,
                        consumer_type=pulsar.ConsumerType.Shared,
                        schema=pulsar.schema.StringSchema()  # Use string schema for flexibility
                    )

                    self._consumers[command_topic] = consumer
                    print(f"✅ Subscribed to command topic: {full_topic}")
                    return consumer

                except Exception as topic_error:
                    print(f"❌ Failed to subscribe to {full_topic}: {topic_error}")
                    continue

            raise Exception(
                f"Failed to subscribe to any topic configuration: {command_topic}"
            )

        except Exception as e:
            print(f"❌ Failed to subscribe to commands: {e}")
            raise

    async def start_consuming(self):
        """Start consuming messages"""
        try:
            consumer = await self.subscribe_to_commands()
            self._running = True

            print(f"🎧 Starting to consume commands for {self.service_name} service...")

            while self._running:
                try:
                    # Receive message with timeout
                    msg = consumer.receive(timeout_millis=1000)

                    # Process message
                    await self._process_command_message(msg, consumer)

                except Exception as e:
                    if "Pulsar error: TimeOut" not in str(e):
                        print(f"⚠️ Error receiving message: {e}")
                    # Continue consuming even on timeout
                    await asyncio.sleep(0.1)

        except Exception as e:
            print(f"❌ Error in consuming loop: {e}")
            raise

    async def _process_command_message(self, msg, consumer):
        """Process a received command message"""
        try:
            # Get message data
            message_data = msg.value()

            # Extract command type from message (this depends on how Pulsar serializes Avro)
            # For now, we'll try to detect the command type from the message structure
            command_type = self._detect_command_type(message_data)

            if command_type in self._command_handlers:
                print(f"📨 Processing command: {command_type}")

                # Call the registered handler
                handler = self._command_handlers[command_type]
                await handler(message_data, msg.message_id())

                # Acknowledge message after successful processing
                consumer.acknowledge(msg)
                print(f"✅ Command processed successfully: {command_type}")

            else:
                print(f"⚠️ No handler registered for command type: {command_type}")
                consumer.acknowledge(msg)  # Acknowledge to avoid redelivery

        except Exception as e:
            print(f"❌ Error processing command message: {e}")
            # Negative acknowledge to trigger redelivery
            consumer.negative_acknowledge(msg)

    def _detect_command_type(self, message_data) -> str:
        """Detect command type from message data"""
        try:
            # If message_data has command_type field
            if hasattr(message_data, "command_type"):
                return message_data.command_type
            elif isinstance(message_data, dict) and "command_type" in message_data:
                return message_data["command_type"]
            else:
                # Fallback: try to detect from message structure
                if hasattr(message_data, "campaign_id") and hasattr(
                    message_data, "name"
                ):
                    return "campaign.create.command.v1"
                elif hasattr(message_data, "campaign_id") and hasattr(
                    message_data, "video_url"
                ):
                    return "campaign.add_video.command.v1"
                elif hasattr(message_data, "partner_id") and hasattr(
                    message_data, "visitor_id"
                ):
                    return "tracking.create_event.command.v1"
                elif hasattr(message_data, "tracking_event_id") and hasattr(
                    message_data, "partner_id"
                ):
                    return "commission.calculate.command.v1"
                elif hasattr(message_data, "user_id") and hasattr(
                    message_data, "amount"
                ):
                    return "payment.process.command.v1"
                else:
                    return "unknown"

        except Exception as e:
            print(f"⚠️ Error detecting command type: {e}")
            return "unknown"

    async def stop(self):
        """Stop consuming and close connections"""
        try:
            self._running = False

            # Close consumers
            for consumer in self._consumers.values():
                consumer.close()

            # Close client
            if self._client:
                self._client.close()

            print(f"✅ Stopped Avro Pulsar consumer for {self.service_name}")

        except Exception as e:
            print(f"❌ Error stopping Avro Pulsar consumer: {e}")


# =============================================================================
# SERVICE-SPECIFIC CONSUMER INSTANCES
# =============================================================================


# Campaign Service Consumer
class CampaignServiceConsumer(AvroPulsarConsumer):
    """Consumer specifically for Campaign Service commands"""

    def __init__(self):
        super().__init__("campaign")

    def register_handlers(self, create_campaign_handler, add_video_handler):
        """Register command handlers for campaign service"""
        self.register_command_handler(
            "campaign.create.command.v1", create_campaign_handler
        )
        self.register_command_handler(
            "campaign.add_video.command.v1", add_video_handler
        )


# Tracking Service Consumer
class TrackingServiceConsumer(AvroPulsarConsumer):
    """Consumer specifically for Tracking Service commands"""

    def __init__(self):
        super().__init__("tracking")

    def register_handlers(self, create_tracking_event_handler):
        """Register command handlers for tracking service"""
        self.register_command_handler(
            "tracking.create_event.command.v1", create_tracking_event_handler
        )


# Commission Service Consumer
class CommissionServiceConsumer(AvroPulsarConsumer):
    """Consumer specifically for Commission Service commands"""

    def __init__(self):
        super().__init__("commission")

    def register_handlers(self, calculate_commission_handler):
        """Register command handlers for commission service"""
        self.register_command_handler(
            "commission.calculate.command.v1", calculate_commission_handler
        )


# Payment Service Consumer
class PaymentServiceConsumer(AvroPulsarConsumer):
    """Consumer specifically for Payment Service commands"""

    def __init__(self):
        super().__init__("payment")

    def register_handlers(self, process_payment_handler):
        """Register command handlers for payment service"""
        self.register_command_handler(
            "payment.process.command.v1", process_payment_handler
        )
