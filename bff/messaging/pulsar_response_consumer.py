import json
import asyncio
import pulsar
from typing import Dict, Any, Callable
from uuid import UUID
from config.pulsar_config import PulsarConfig


class PulsarResponseConsumer:
    """Pulsar consumer for BFF command responses"""

    def __init__(self):
        self._client = None
        self._consumers = {}  # topic -> consumer mapping
        self._response_handlers = {}  # command_id -> handler mapping
        self._running = False

    async def start(self):
        """Initialize Pulsar client and consumers for response topics"""
        try:
            # Create Pulsar client
            client_config = PulsarConfig.get_client_config()
            self._client = pulsar.Client(**client_config)

            # Initialize consumers for all response topics
            response_topics = PulsarConfig.get_all_response_topics()

            for topic in response_topics:
                await self._create_consumer_for_topic(topic)

            self._running = True
            print(f"✅ BFF Pulsar response consumer started with {len(self._consumers)} consumers")

            # Start consuming in background tasks
            tasks = []
            for topic, consumer in self._consumers.items():
                task = asyncio.create_task(self._consume_loop(topic, consumer))
                tasks.append(task)

            return tasks

        except Exception as e:
            print(f"❌ Failed to start BFF Pulsar response consumer: {e}")
            raise

    async def _create_consumer_for_topic(self, base_topic: str):
        """Create consumer for a specific response topic"""
        topic_name = base_topic.split("/")[-1]  # Extract topic name
        topics_to_try = PulsarConfig.get_topic_options(topic_name)

        for topic in topics_to_try:
            try:
                print(f"🎧 Attempting to create consumer for topic: {topic}")
                consumer = self._client.subscribe(
                    topic,
                    subscription_name=PulsarConfig.BFF_RESPONSES_SUBSCRIPTION,
                    consumer_type=pulsar.ConsumerType.Shared,
                )
                self._consumers[base_topic] = consumer
                print(f"✅ Consumer created for: {topic}")
                return
            except Exception as topic_error:
                print(f"❌ Failed to create consumer for {topic}: {topic_error}")
                continue

        print(f"⚠️  Could not create consumer for {base_topic} - will continue without it")

    async def _consume_loop(self, topic: str, consumer):
        """Main consumption loop for a specific topic"""
        print(f"🔄 Starting consumption loop for topic: {topic}")

        while self._running:
            try:
                # Receive message with timeout
                msg = consumer.receive(timeout_millis=2000)

                # Process response message
                await self._process_response_message(topic, msg)

                # Acknowledge message
                consumer.acknowledge(msg)
                print(f"✅ Response message acknowledged: {msg.message_id()}")

            except pulsar.Timeout:
                # Timeout is normal, continue loop
                continue
            except Exception as e:
                print(f"❌ Error processing response message from {topic}: {e}")
                await asyncio.sleep(1)

    async def _process_response_message(self, topic: str, msg):
        """Process received response message"""
        try:
            # Parse message data
            data = json.loads(msg.data().decode("utf-8"))

            print(f"📥 Received response from {topic}: {data.get('command_id', 'unknown')}")

            # Extract command ID and find registered handler
            command_id = data.get("command_id")
            if command_id and command_id in self._response_handlers:
                handler = self._response_handlers[command_id]
                await handler(data)

                # Remove handler after processing (one-time use)
                del self._response_handlers[command_id]
            else:
                print(f"⚠️  No handler found for command_id: {command_id}")

        except Exception as e:
            print(f"❌ Error processing response message: {e}")
            raise

    def register_response_handler(self, command_id: str, handler: Callable):
        """Register a handler for a specific command response"""
        self._response_handlers[command_id] = handler
        print(f"📝 Registered response handler for command: {command_id}")

    async def wait_for_response(self, command_id: str, timeout_seconds: int = 30) -> Dict[str, Any]:
        """Wait for a response to a specific command (for synchronous-like behavior)"""
        response_data = None
        response_received = asyncio.Event()

        def response_handler(data):
            nonlocal response_data
            response_data = data
            response_received.set()

        # Register temporary handler
        self.register_response_handler(command_id, response_handler)

        try:
            # Wait for response with timeout
            await asyncio.wait_for(response_received.wait(), timeout=timeout_seconds)
            return response_data
        except asyncio.TimeoutError:
            # Remove handler on timeout
            self._response_handlers.pop(command_id, None)
            raise TimeoutError(f"Response timeout for command: {command_id}")

    async def stop(self):
        """Stop all consumers and close connections"""
        self._running = False

        for consumer in self._consumers.values():
            if consumer:
                consumer.close()

        if self._client:
            self._client.close()

        print("🛑 BFF Pulsar response consumer stopped")


# Global response consumer instance
pulsar_response_consumer = PulsarResponseConsumer()