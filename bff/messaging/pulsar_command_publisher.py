import json
import pulsar
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from config.pulsar_config import PulsarConfig


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal types"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class PulsarCommandPublisher:
    """Pulsar publisher for BFF commands with response handling"""

    def __init__(self):
        self._client = None
        self._producers = {}  # topic -> producer mapping
        self._initialized_topics = set()

    async def start(self):
        """Initialize Pulsar client and producers"""
        try:
            # Create Pulsar client
            client_config = PulsarConfig.get_client_config()
            self._client = pulsar.Client(**client_config)

            # Initialize producers for all command topics
            command_topics = PulsarConfig.get_all_command_topics()

            for topic in command_topics:
                await self._create_producer_for_topic(topic)

            print(
                f"✅ BFF Pulsar publisher started with {len(self._producers)} producers"
            )

        except Exception as e:
            print(f"❌ Failed to start BFF Pulsar publisher: {e}")
            raise

    async def _create_producer_for_topic(self, base_topic: str):
        """Create producer for a specific topic with fallback options"""
        topic_name = base_topic.split("/")[-1]  # Extract topic name
        topics_to_try = PulsarConfig.get_topic_options(topic_name)

        for topic in topics_to_try:
            try:
                print(f"📡 Attempting to create producer for topic: {topic}")
                producer = self._client.create_producer(topic)
                self._producers[base_topic] = producer
                self._initialized_topics.add(topic)
                print(f"✅ Producer created for: {topic}")
                return
            except Exception as topic_error:
                print(f"❌ Failed to create producer for {topic}: {topic_error}")
                continue

        raise Exception(f"Failed to create producer for any variation of {base_topic}")

    async def publish_campaign_accept_command(
        self,
        user_id: str,
        campaign_id: str,
        partner_id: str,
        partner_type: str,
        acceptance_terms: Dict[str, Any],
        estimated_monthly_reach: int,
    ) -> str:
        """Publish campaign accept command"""

        command_id = str(uuid4())

        command_data = {
            "command_id": command_id,
            "command_type": "accept_campaign",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "campaign_id": campaign_id,
                "partner_id": partner_id,
                "partner_type": partner_type,
                "acceptance_terms": acceptance_terms,
                "estimated_monthly_reach": estimated_monthly_reach,
            },
            # TODO: In future, this will be Avro schema version
            "schema_version": "v1",
        }

        await self._publish_command(PulsarConfig.CAMPAIGN_ACCEPT_COMMANDS, command_data)
        return command_id

    async def publish_evidence_upload_command(
        self,
        user_id: str,
        partner_id: str,
        campaign_id: str,
        evidence_type: str,
        evidence_details: Dict[str, Any],
        audience_data: Dict[str, Any],
        description: str,
    ) -> str:
        """Publish evidence upload command"""

        command_id = str(uuid4())

        command_data = {
            "command_id": command_id,
            "command_type": "upload_evidence",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "partner_id": partner_id,
                "campaign_id": campaign_id,
                "evidence_type": evidence_type,
                "evidence_details": evidence_details,
                "audience_data": audience_data,
                "description": description,
            },
            "schema_version": "v1",
        }

        await self._publish_command(PulsarConfig.EVIDENCE_UPLOAD_COMMANDS, command_data)
        return command_id

    async def publish_payment_request_command(
        self,
        user_id: str,
        partner_id: str,
        request_type: str,
        payment_details: Dict[str, Any],
        commission_period: Dict[str, Any],
        invoice_details: Dict[str, Any],
    ) -> str:
        """Publish payment request command"""

        command_id = str(uuid4())

        command_data = {
            "command_id": command_id,
            "command_type": "request_payment",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "partner_id": partner_id,
                "request_type": request_type,
                "payment_details": payment_details,
                "commission_period": commission_period,
                "invoice_details": invoice_details,
            },
            "schema_version": "v1",
        }

        await self._publish_command(PulsarConfig.PAYMENT_REQUEST_COMMANDS, command_data)
        return command_id

    async def _publish_command(self, topic: str, command_data: Dict[str, Any]):
        """Publish command to specific topic"""
        try:
            producer = self._producers.get(topic)
            if not producer:
                raise Exception(f"No producer available for topic: {topic}")

            # Serialize command data (JSON for now, Avro in future)
            message_data = json.dumps(command_data, cls=DecimalEncoder).encode("utf-8")

            # Add message properties for routing and tracing
            properties = {
                "command_id": command_data["command_id"],
                "command_type": command_data["command_type"],
                "user_id": command_data["user_id"],
                "schema_version": command_data["schema_version"],
            }

            producer.send(message_data, properties=properties)

            print(
                f"📤 Published {command_data['command_type']} command: {command_data['command_id']}"
            )

        except Exception as e:
            print(f"❌ Failed to publish command to {topic}: {e}")
            raise

    async def stop(self):
        """Close all producers and client"""
        for producer in self._producers.values():
            if producer:
                producer.close()

        if self._client:
            self._client.close()

        print("🛑 BFF Pulsar publisher stopped")


# Global publisher instance
pulsar_command_publisher = PulsarCommandPublisher()
