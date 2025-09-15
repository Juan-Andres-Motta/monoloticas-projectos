import json
import asyncio
import pulsar
from typing import Dict, Any
from uuid import UUID
from datetime import datetime

from seedwork.application.command_bus import CommandBus
from commission.application.commands.calculate_commission_command import (
    CalculateCommissionCommand,
)
from config.pulsar_config import PulsarConfig


class PulsarConsumer:
    """Pulsar consumer for tracking events"""

    def __init__(self, command_bus: CommandBus):
        self._command_bus = command_bus
        self._consumer = None
        self._client = None

    async def start(self) -> asyncio.Task:
        """Start consuming tracking events from Pulsar"""
        try:
            # Create Pulsar client with DataStax Astra Streaming
            client_config = PulsarConfig.get_client_config()
            self._client = pulsar.Client(**client_config)

            # Create consumer for tracking events
            self._consumer = self._client.subscribe(
                PulsarConfig.TRACKING_EVENTS_TOPIC,
                subscription_name=PulsarConfig.COMMISSION_SUBSCRIPTION,
                consumer_type=pulsar.ConsumerType.Shared,
            )

            print(
                f"🎧 Started Pulsar consumer for topic: {PulsarConfig.TRACKING_EVENTS_TOPIC}"
            )

            # Start consuming in background task
            task = asyncio.create_task(self._consume_loop())
            return task

        except Exception as e:
            print(f"❌ Failed to start Pulsar consumer: {e}")
            raise

    async def _consume_loop(self):
        """Main consumption loop"""
        while True:
            try:
                # Receive message with timeout (2 seconds like in your example)
                msg = self._consumer.receive(timeout_millis=2000)

                # Process message
                await self._process_message(msg)

                # Acknowledge message to remove from backlog
                self._consumer.acknowledge(msg)
                print(f"✅ Message acknowledged: {msg.message_id()}")

            except pulsar.Timeout:
                # Timeout is normal, continue loop
                print("Still waiting for a message...")
                continue
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, msg):
        """Process received tracking event message"""
        try:
            # Parse message data
            data = json.loads(msg.data().decode("utf-8"))

            print(
                "📨 Received message '{}' id='{}'".format(msg.data(), msg.message_id())
            )
            print(f"📨 Parsed tracking event: {data}")

            # Create commission calculation command
            command = CalculateCommissionCommand(
                tracking_event_id=UUID(data["tracking_event_id"]),
                partner_id=data["partner_id"],
                campaign_id=data["campaign_id"],
                visitor_id=data["visitor_id"],
                interaction_type=data["interaction_type"],
            )

            # Execute command
            commission_id = await self._command_bus.execute(
                "calculate_commission", command
            )

            print(f"✅ Commission calculated with ID: {commission_id}")

        except Exception as e:
            print(f"❌ Error processing tracking event: {e}")
            raise

    async def stop(self):
        """Stop consumer and close connections"""
        if self._consumer:
            self._consumer.close()
        if self._client:
            self._client.close()


async def start_pulsar_consumer(container) -> asyncio.Task:
    """Factory function to start Pulsar consumer"""
    command_bus = container.get("command_bus")
    consumer = PulsarConsumer(command_bus)
    return await consumer.start()
