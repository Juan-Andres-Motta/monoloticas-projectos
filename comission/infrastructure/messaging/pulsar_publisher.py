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

    async def start(self):
        """Initialize Pulsar client and producer"""
        try:
            # Create Pulsar client with DataStax Astra Streaming
            client_config = PulsarConfig.get_client_config()
            self._client = pulsar.Client(**client_config)
            self._producer = self._client.create_producer(
                PulsarConfig.COMMISSIONS_TOPIC
            )
            print(
                f"📡 Started Pulsar publisher for topic: {PulsarConfig.COMMISSIONS_TOPIC}"
            )
        except Exception as e:
            print(f"❌ Failed to start Pulsar publisher: {e}")
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
