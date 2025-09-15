"""
Avro schema definitions for inter-microservices communication using Pulsar.
These schemas define both command events (for triggering operations) and
domain events (for notifying about completed operations).
"""

import pulsar
from pulsar.schema import AvroSchema, Record, String, Integer, Long, Array, Boolean
from typing import Optional
from datetime import datetime
from uuid import UUID


# =============================================================================
# COMMAND EVENTS - Events that trigger operations in microservices
# =============================================================================


class CreateCampaignCommandAvro(Record):
    """Command to create a new campaign - listened by Campaign Service"""

    # Command metadata
    command_id = String()
    command_type = String(default="campaign.create.command.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds
    correlation_id = String()  # For tracking the operation across services

    # Campaign creation data
    campaign_id = String()
    user_id = String()
    name = String()
    description = String(default="")


class AddVideoUrlCommandAvro(Record):
    """Command to add video URL to campaign - listened by Campaign Service"""

    # Command metadata
    command_id = String()
    command_type = String(default="campaign.add_video.command.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds
    correlation_id = String()

    # Video addition data
    campaign_id = String()
    video_url = String()


class CreateTrackingEventCommandAvro(Record):
    """Command to create tracking event - listened by Tracking Service"""

    # Command metadata
    command_id = String()
    command_type = String(default="tracking.create_event.command.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds
    correlation_id = String()

    # Tracking event data
    partner_id = String()
    campaign_id = String()
    visitor_id = String()
    interaction_type = String()  # click, view, conversion, etc.


class CalculateCommissionCommandAvro(Record):
    """Command to calculate commission - listened by Commission Service"""

    # Command metadata
    command_id = String()
    command_type = String(default="commission.calculate.command.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds
    correlation_id = String()

    # Commission calculation data
    tracking_event_id = String()
    partner_id = String()
    campaign_id = String()
    interaction_type = String()


class ProcessPaymentCommandAvro(Record):
    """Command to process payment - listened by Payment Service"""

    # Command metadata
    command_id = String()
    command_type = String(default="payment.process.command.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds
    correlation_id = String()

    # Payment data
    user_id = String()
    amount = String()  # Using string to avoid precision issues
    currency = String(default="USD")
    payment_method = String()
    campaign_id = String(default="")


# =============================================================================
# DOMAIN EVENTS - Events that notify about completed operations
# =============================================================================


class CampaignCreatedEventAvro(Record):
    """Avro schema for campaign created events"""

    # Event metadata
    event_id = String()
    event_type = String(default="campaign.created.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds

    # Campaign data
    campaign_id = String()
    user_id = String()
    name = String()
    description = String(default="")
    status = String(default="ACTIVE")
    created_at = Integer()  # Unix timestamp in milliseconds

    @classmethod
    def from_domain_event(cls, domain_event):
        """Convert domain event to Avro record"""
        return cls(
            event_id=str(domain_event.event_id),
            event_type=domain_event.event_type(),
            timestamp=int(domain_event.timestamp.timestamp() * 1000),
            campaign_id=str(domain_event.campaign_id),
            user_id=domain_event.user_id,
            name=domain_event.name,
            description=domain_event.description or "",
            status=domain_event.status,
            created_at=int(domain_event.created_at.timestamp() * 1000),
        )


class VideoAddedEventAvro(Record):
    """Avro schema for video added events"""

    # Event metadata
    event_id = String()
    event_type = String(default="video.added.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds

    # Video event data
    campaign_id = String()
    video_url = String()
    added_at = Integer()  # Unix timestamp in milliseconds

    @classmethod
    def from_domain_event(cls, domain_event):
        """Convert domain event to Avro record"""
        return cls(
            event_id=str(domain_event.event_id),
            event_type=domain_event.event_type(),
            timestamp=int(domain_event.timestamp.timestamp() * 1000),
            campaign_id=str(domain_event.campaign_id),
            video_url=domain_event.video_url,
            added_at=int(domain_event.added_at.timestamp() * 1000),
        )


class TrackingEventCreatedAvro(Record):
    """Domain event: tracking event has been created"""

    # Event metadata
    event_id = String()
    event_type = String(default="tracking_event.created.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds
    correlation_id = String()

    # Tracking event data
    tracking_event_id = String()
    partner_id = String()
    campaign_id = String()
    visitor_id = String()
    interaction_type = String()

    @classmethod
    def create(
        cls,
        tracking_event_id: UUID,
        partner_id: str,
        campaign_id: str,
        visitor_id: str,
        interaction_type: str,
        correlation_id: str = None,
    ):
        """Create tracking event Avro record"""
        from uuid import uuid4

        now = datetime.utcnow()

        return cls(
            event_id=str(uuid4()),
            event_type="tracking_event.created.v1",
            timestamp=int(now.timestamp() * 1000),
            correlation_id=correlation_id or str(uuid4()),
            tracking_event_id=str(tracking_event_id),
            partner_id=partner_id,
            campaign_id=campaign_id,
            visitor_id=visitor_id,
            interaction_type=interaction_type,
        )


class CommissionCalculatedAvro(Record):
    """Domain event: commission has been calculated"""

    # Event metadata
    event_id = String()
    event_type = String(default="commission.calculated.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds
    correlation_id = String()

    # Commission data
    commission_id = String()
    tracking_event_id = String()
    partner_id = String()
    campaign_id = String()
    commission_amount = String()  # Using string to avoid precision issues
    commission_rate = String()
    status = String()  # calculated, paid, failed

    @classmethod
    def create(
        cls,
        commission_id: UUID,
        tracking_event_id: UUID,
        partner_id: str,
        campaign_id: str,
        commission_amount: float,
        commission_rate: float,
        correlation_id: str = None,
    ):
        """Create commission calculated event"""
        from uuid import uuid4

        now = datetime.utcnow()

        return cls(
            event_id=str(uuid4()),
            event_type="commission.calculated.v1",
            timestamp=int(now.timestamp() * 1000),
            correlation_id=correlation_id or str(uuid4()),
            commission_id=str(commission_id),
            tracking_event_id=str(tracking_event_id),
            partner_id=partner_id,
            campaign_id=campaign_id,
            commission_amount=str(commission_amount),
            commission_rate=str(commission_rate),
            status="calculated",
        )


class PaymentProcessedAvro(Record):
    """Domain event: payment has been processed"""

    # Event metadata
    event_id = String()
    event_type = String(default="payment.processed.v1")
    timestamp = Long()  # Use Long for Unix timestamps in milliseconds
    correlation_id = String()

    # Payment data
    payment_id = String()
    user_id = String()
    amount = String()
    currency = String()
    status = String()  # success, failed, pending
    transaction_id = String(default="")
    campaign_id = String(default="")


# Schema instances for reuse
# Command schemas
CREATE_CAMPAIGN_COMMAND_SCHEMA = AvroSchema(CreateCampaignCommandAvro)
ADD_VIDEO_URL_COMMAND_SCHEMA = AvroSchema(AddVideoUrlCommandAvro)
CREATE_TRACKING_EVENT_COMMAND_SCHEMA = AvroSchema(CreateTrackingEventCommandAvro)
CALCULATE_COMMISSION_COMMAND_SCHEMA = AvroSchema(CalculateCommissionCommandAvro)
PROCESS_PAYMENT_COMMAND_SCHEMA = AvroSchema(ProcessPaymentCommandAvro)

# Event schemas
CAMPAIGN_CREATED_SCHEMA = AvroSchema(CampaignCreatedEventAvro)
VIDEO_ADDED_SCHEMA = AvroSchema(VideoAddedEventAvro)
TRACKING_EVENT_CREATED_SCHEMA = AvroSchema(TrackingEventCreatedAvro)
COMMISSION_CALCULATED_SCHEMA = AvroSchema(CommissionCalculatedAvro)
PAYMENT_PROCESSED_SCHEMA = AvroSchema(PaymentProcessedAvro)


class AvroSchemaRegistry:
    """Registry for managing Avro schemas"""

    # Command schemas - for triggering operations
    COMMAND_SCHEMAS = {
        "campaign.create.command.v1": CREATE_CAMPAIGN_COMMAND_SCHEMA,
        "campaign.add_video.command.v1": ADD_VIDEO_URL_COMMAND_SCHEMA,
        "tracking.create_event.command.v1": CREATE_TRACKING_EVENT_COMMAND_SCHEMA,
        "commission.calculate.command.v1": CALCULATE_COMMISSION_COMMAND_SCHEMA,
        "payment.process.command.v1": PROCESS_PAYMENT_COMMAND_SCHEMA,
    }

    # Event schemas - for domain events
    EVENT_SCHEMAS = {
        "campaign.created.v1": CAMPAIGN_CREATED_SCHEMA,
        "video.added.v1": VIDEO_ADDED_SCHEMA,
        "tracking_event.created.v1": TRACKING_EVENT_CREATED_SCHEMA,
        "commission.calculated.v1": COMMISSION_CALCULATED_SCHEMA,
        "payment.processed.v1": PAYMENT_PROCESSED_SCHEMA,
    }

    # All schemas combined
    SCHEMAS = {**COMMAND_SCHEMAS, **EVENT_SCHEMAS}

    @classmethod
    def get_schema(cls, message_type: str) -> AvroSchema:
        """Get schema by message type"""
        schema = cls.SCHEMAS.get(message_type)
        if not schema:
            raise ValueError(f"No schema found for message type: {message_type}")
        return schema

    @classmethod
    def get_command_schema(cls, command_type: str) -> AvroSchema:
        """Get command schema by type"""
        schema = cls.COMMAND_SCHEMAS.get(command_type)
        if not schema:
            raise ValueError(f"No command schema found for type: {command_type}")
        return schema

    @classmethod
    def get_event_schema(cls, event_type: str) -> AvroSchema:
        """Get event schema by type"""
        schema = cls.EVENT_SCHEMAS.get(event_type)
        if not schema:
            raise ValueError(f"No event schema found for type: {event_type}")
        return schema

    @classmethod
    def get_record_class(cls, message_type: str):
        """Get record class by message type"""
        record_classes = {
            # Commands
            "campaign.create.command.v1": CreateCampaignCommandAvro,
            "campaign.add_video.command.v1": AddVideoUrlCommandAvro,
            "tracking.create_event.command.v1": CreateTrackingEventCommandAvro,
            "commission.calculate.command.v1": CalculateCommissionCommandAvro,
            "payment.process.command.v1": ProcessPaymentCommandAvro,
            # Events
            "campaign.created.v1": CampaignCreatedEventAvro,
            "video.added.v1": VideoAddedEventAvro,
            "tracking_event.created.v1": TrackingEventCreatedAvro,
            "commission.calculated.v1": CommissionCalculatedAvro,
            "payment.processed.v1": PaymentProcessedAvro,
        }

        record_class = record_classes.get(message_type)
        if not record_class:
            raise ValueError(f"No record class found for message type: {message_type}")
        return record_class


# =============================================================================
# TOPIC CONFIGURATION
# =============================================================================


class PulsarTopics:
    """Configuration for Pulsar topics"""

    # Command topics - each service listens to these (versioned to avoid schema conflicts)
    CAMPAIGN_COMMANDS = "campaign-commands-v0216"
    TRACKING_COMMANDS = "tracking-commands-v0216"
    COMMISSION_COMMANDS = "commission-commands-v0216"
    PAYMENT_COMMANDS = "payment-commands-v0216"

    # Event topics - for publishing domain events (versioned to avoid schema conflicts)
    CAMPAIGN_EVENTS = "campaign-events-v0216"
    TRACKING_EVENTS = "tracking-events-v0216"
    COMMISSION_EVENTS = "commission-events-v0216"
    PAYMENT_EVENTS = "payment-events-v0216"

    @classmethod
    def get_command_topic(cls, service_name: str) -> str:
        """Get command topic for a service"""
        topics = {
            "campaign": cls.CAMPAIGN_COMMANDS,
            "tracking": cls.TRACKING_COMMANDS,
            "commission": cls.COMMISSION_COMMANDS,
            "payment": cls.PAYMENT_COMMANDS,
        }
        topic = topics.get(service_name)
        if not topic:
            raise ValueError(f"No command topic found for service: {service_name}")
        return topic

    @classmethod
    def get_event_topic(cls, service_name: str) -> str:
        """Get event topic for a service"""
        topics = {
            "campaign": cls.CAMPAIGN_EVENTS,
            "tracking": cls.TRACKING_EVENTS,
            "commission": cls.COMMISSION_EVENTS,
            "payment": cls.PAYMENT_EVENTS,
        }
        topic = topics.get(service_name)
        if not topic:
            raise ValueError(f"No event topic found for service: {service_name}")
        return topic
