import json
import pulsar
from typing import Dict, Any
from uuid import UUID
from config.pulsar_config import PulsarConfig


class PulsarPublisher:
    """Pulsar publisher for domain events"""

    def __init__(self):
        self._client = None
        self._producer = None
        self._topic = None

    async def start(self):
        """Initialize Pulsar client and producer"""
        try:
            # Create Pulsar client with DataStax Astra Streaming
            client_config = PulsarConfig.get_client_config()
            self._client = pulsar.Client(**client_config)

            # Try different topic configurations
            topics_to_try = PulsarConfig.get_topic_options("tracking-events")

            for topic in topics_to_try:
                try:
                    print(f"📡 Attempting to create producer for topic: {topic}")
                    self._producer = self._client.create_producer(topic)
                    self._topic = topic
                    print(
                        f"✅ Successfully started Pulsar publisher for topic: {topic}"
                    )
                    return
                except Exception as topic_error:
                    print(f"❌ Failed to create producer for {topic}: {topic_error}")
                    continue

            # If all topics failed
            raise Exception("Failed to create producer for any topic configuration")

        except Exception as e:
            print(f"❌ Failed to start Pulsar publisher: {e}")
            print("💡 Suggestions:")
            print("   1. Check PULSAR_TOKEN in .env file")
            print("   2. Verify tenant/namespace exists in DataStax Console")
            print("   3. Create topics manually in DataStax Console")
            print("   4. Check token permissions")
            raise

    async def publish_tracking_event(
        self,
        tracking_event_id: UUID,
        partner_id: str,
        campaign_id: str,
        visitor_id: str,
        interaction_type: str,
    ):
        """Publish tracking event to Pulsar"""
        try:
            # Create event payload
            event_data = {
                "tracking_event_id": str(tracking_event_id),
                "partner_id": partner_id,
                "campaign_id": campaign_id,
                "visitor_id": visitor_id,
                "interaction_type": interaction_type,
                "event_type": "tracking_event.recorded.v1",
            }

            # Send message
            message_data = json.dumps(event_data).encode("utf-8")
            self._producer.send(message_data)

            print(f"📤 Published tracking event: {tracking_event_id}")

        except Exception as e:
            print(f"❌ Failed to publish tracking event: {e}")
            raise

    async def stop(self):
        """Close producer and client"""
        if self._producer:
            self._producer.close()
        if self._client:
            self._client.close()


# Global publisher instance
pulsar_publisher = PulsarPublisher()
