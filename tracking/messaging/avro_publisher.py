"""
Event-driven Pulsar publisher using Avro schemas.
This publisher handles both command publishing and domain event publishing.
"""

import pulsar
import asyncio
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime

from config.pulsar_config import PulsarConfig
from messaging.schemas.avro_schemas import (
    AvroSchemaRegistry, 
    PulsarTopics,
    CreateCampaignCommandAvro,
    AddVideoUrlCommandAvro,
    CreateTrackingEventCommandAvro,
    CalculateCommissionCommandAvro,
    ProcessPaymentCommandAvro
)


class AvroPulsarPublisher:
    """Pulsar publisher with Avro schema support for event-driven architecture"""

    def __init__(self):
        self._client = None
        self._command_producers = {}  # Topic -> Producer mapping for commands
        self._event_producers = {}    # Topic -> Producer mapping for events

    async def start(self):
        """Initialize Pulsar client and producers"""
        try:
            # Create Pulsar client with DataStax Astra Streaming
            client_config = PulsarConfig.get_client_config()
            self._client = pulsar.Client(**client_config)
            
            print("✅ Started Avro Pulsar publisher with schema registry support")
            print("📡 Ready to publish commands and events with type safety")
            
        except Exception as e:
            print(f"❌ Failed to start Avro Pulsar publisher: {e}")
            raise

    async def _get_or_create_producer(self, topic: str, schema, producer_dict: dict):
        """Get existing producer or create new one with Avro schema"""
        if topic not in producer_dict:
            try:
                # Try different topic configurations
                topics_to_try = PulsarConfig.get_topic_options(topic)
                
                for full_topic in topics_to_try:
                    try:
                        print(f"📡 Creating Avro producer for topic: {full_topic}")
                        producer = self._client.create_producer(
                            full_topic,
                            schema=schema
                        )
                        producer_dict[topic] = producer
                        print(f"✅ Created Avro producer for: {full_topic}")
                        return producer
                    except Exception as topic_error:
                        print(f"❌ Failed to create producer for {full_topic}: {topic_error}")
                        continue
                
                raise Exception(f"Failed to create producer for any topic configuration: {topic}")
                
            except Exception as e:
                print(f"❌ Failed to create producer for topic {topic}: {e}")
                raise
        
        return producer_dict[topic]

    # ==========================================================================
    # COMMAND PUBLISHING - Send commands to other microservices
    # ==========================================================================

    async def send_create_campaign_command(
        self, 
        campaign_id: UUID,
        user_id: str,
        name: str,
        description: str = "",
        correlation_id: Optional[str] = None
    ) -> str:
        """Send command to Campaign Service to create a campaign"""
        try:
            correlation_id = correlation_id or str(uuid4())
            
            # Create Avro command record
            command = CreateCampaignCommandAvro(
                command_id=str(uuid4()),
                command_type="campaign.create.command.v1",
                timestamp=int(datetime.utcnow().timestamp() * 1000),
                correlation_id=correlation_id,
                campaign_id=str(campaign_id),
                user_id=user_id,
                name=name,
                description=description
            )
            
            # Get producer with Avro schema
            schema = AvroSchemaRegistry.get_command_schema("campaign.create.command.v1")
            producer = await self._get_or_create_producer(
                PulsarTopics.CAMPAIGN_COMMANDS, 
                schema, 
                self._command_producers
            )
            
            # Send command
            producer.send(command)
            print(f"📤 Sent create campaign command: {campaign_id}")
            return correlation_id
            
        except Exception as e:
            print(f"❌ Failed to send create campaign command: {e}")
            raise

    async def send_add_video_url_command(
        self,
        campaign_id: UUID,
        video_url: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Send command to Campaign Service to add video URL"""
        try:
            correlation_id = correlation_id or str(uuid4())
            
            # Create Avro command record
            command = AddVideoUrlCommandAvro(
                command_id=str(uuid4()),
                command_type="campaign.add_video.command.v1",
                timestamp=int(datetime.utcnow().timestamp() * 1000),
                correlation_id=correlation_id,
                campaign_id=str(campaign_id),
                video_url=video_url
            )
            
            # Get producer with Avro schema
            schema = AvroSchemaRegistry.get_command_schema("campaign.add_video.command.v1")
            producer = await self._get_or_create_producer(
                PulsarTopics.CAMPAIGN_COMMANDS, 
                schema, 
                self._command_producers
            )
            
            # Send command
            producer.send(command)
            print(f"📤 Sent add video URL command: {campaign_id} -> {video_url}")
            return correlation_id
            
        except Exception as e:
            print(f"❌ Failed to send add video URL command: {e}")
            raise

    async def send_create_tracking_event_command(
        self,
        partner_id: str,
        campaign_id: str,
        visitor_id: str,
        interaction_type: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Send command to Tracking Service to create tracking event"""
        try:
            correlation_id = correlation_id or str(uuid4())
            
            # Create Avro command record
            command = CreateTrackingEventCommandAvro(
                command_id=str(uuid4()),
                command_type="tracking.create_event.command.v1",
                timestamp=int(datetime.utcnow().timestamp() * 1000),
                correlation_id=correlation_id,
                partner_id=partner_id,
                campaign_id=campaign_id,
                visitor_id=visitor_id,
                interaction_type=interaction_type
            )
            
            # Get producer with Avro schema
            schema = AvroSchemaRegistry.get_command_schema("tracking.create_event.command.v1")
            producer = await self._get_or_create_producer(
                PulsarTopics.TRACKING_COMMANDS,
                schema,
                self._command_producers
            )
            
            # Send command
            producer.send(command)
            print(f"📤 Sent create tracking event command: {partner_id}/{campaign_id}")
            return correlation_id
            
        except Exception as e:
            print(f"❌ Failed to send create tracking event command: {e}")
            raise

    async def send_calculate_commission_command(
        self,
        tracking_event_id: UUID,
        partner_id: str,
        campaign_id: str,
        interaction_type: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Send command to Commission Service to calculate commission"""
        try:
            correlation_id = correlation_id or str(uuid4())
            
            # Create Avro command record
            command = CalculateCommissionCommandAvro(
                command_id=str(uuid4()),
                command_type="commission.calculate.command.v1",
                timestamp=int(datetime.utcnow().timestamp() * 1000),
                correlation_id=correlation_id,
                tracking_event_id=str(tracking_event_id),
                partner_id=partner_id,
                campaign_id=campaign_id,
                interaction_type=interaction_type
            )
            
            # Get producer with Avro schema
            schema = AvroSchemaRegistry.get_command_schema("commission.calculate.command.v1")
            producer = await self._get_or_create_producer(
                PulsarTopics.COMMISSION_COMMANDS,
                schema,
                self._command_producers
            )
            
            # Send command
            producer.send(command)
            print(f"📤 Sent calculate commission command: {tracking_event_id}")
            return correlation_id
            
        except Exception as e:
            print(f"❌ Failed to send calculate commission command: {e}")
            raise

    async def send_process_payment_command(
        self,
        user_id: str,
        amount: float,
        currency: str,
        payment_method: str,
        campaign_id: str = "",
        correlation_id: Optional[str] = None
    ) -> str:
        """Send command to Payment Service to process payment"""
        try:
            correlation_id = correlation_id or str(uuid4())
            
            # Create Avro command record
            command = ProcessPaymentCommandAvro(
                command_id=str(uuid4()),
                command_type="payment.process.command.v1",
                timestamp=int(datetime.utcnow().timestamp() * 1000),
                correlation_id=correlation_id,
                user_id=user_id,
                amount=str(amount),
                currency=currency,
                payment_method=payment_method,
                campaign_id=campaign_id
            )
            
            # Get producer with Avro schema
            schema = AvroSchemaRegistry.get_command_schema("payment.process.command.v1")
            producer = await self._get_or_create_producer(
                PulsarTopics.PAYMENT_COMMANDS,
                schema,
                self._command_producers
            )
            
            # Send command
            producer.send(command)
            print(f"📤 Sent process payment command: {user_id} -> ${amount}")
            return correlation_id
            
        except Exception as e:
            print(f"❌ Failed to send process payment command: {e}")
            raise

    # ==========================================================================
    # DOMAIN EVENT PUBLISHING - Publish events when operations complete
    # ==========================================================================

    async def publish_domain_event(self, domain_event, service_name: str):
        """Publish a domain event with Avro schema"""
        try:
            # Convert domain event to Avro record
            event_type = domain_event.event_type()
            record_class = AvroSchemaRegistry.get_record_class(event_type)
            
            # Create Avro record from domain event
            if hasattr(record_class, 'from_domain_event'):
                avro_record = record_class.from_domain_event(domain_event)
            else:
                raise ValueError(f"Record class {record_class} doesn't have from_domain_event method")
            
            # Get producer with Avro schema
            schema = AvroSchemaRegistry.get_event_schema(event_type)
            event_topic = PulsarTopics.get_event_topic(service_name)
            producer = await self._get_or_create_producer(
                event_topic,
                schema,
                self._event_producers
            )
            
            # Send event
            producer.send(avro_record)
            print(f"📤 Published domain event: {event_type}")
            
        except Exception as e:
            print(f"❌ Failed to publish domain event: {e}")
            raise

    async def stop(self):
        """Close all producers and client"""
        try:
            # Close command producers
            for producer in self._command_producers.values():
                producer.close()
            
            # Close event producers  
            for producer in self._event_producers.values():
                producer.close()
                
            # Close client
            if self._client:
                self._client.close()
                
            print("✅ Stopped Avro Pulsar publisher")
            
        except Exception as e:
            print(f"❌ Error stopping Avro Pulsar publisher: {e}")


# Global publisher instance
avro_pulsar_publisher = AvroPulsarPublisher()
