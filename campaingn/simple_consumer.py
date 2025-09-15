#!/usr/bin/env python3
"""
Simple Pulsar Consumer for Campaign Service
Listens to campaign events and creates database records
"""

import asyncio
import json
import os
import sys
import pulsar
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://campaign_user:campaign_password@localhost:5436/campaigndb",
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    partner_id = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
print("🗄️ Creating campaign database tables...")
Base.metadata.create_all(bind=engine)


class SimpleCampaignConsumer:
    def __init__(self):
        self.client = None
        self.consumer = None

    async def start(self):
        """Start Pulsar consumer"""
        try:
            # Pulsar configuration
            service_url = os.getenv("PULSAR_SERVICE_URL")
            token = os.getenv("PULSAR_TOKEN")
            tenant = os.getenv("PULSAR_TENANT", "miso-1-2025")
            namespace = os.getenv("PULSAR_NAMESPACE", "default")

            if not service_url or not token:
                raise ValueError("PULSAR_SERVICE_URL and PULSAR_TOKEN must be set")

            # Create client
            self.client = pulsar.Client(
                service_url, authentication=pulsar.AuthenticationToken(token)
            )

            # Try different topic variations for campaigns
            topics = [
                f"persistent://{tenant}/{namespace}/campaign-events",
                f"persistent://public/default/campaign-events",
                f"non-persistent://{tenant}/{namespace}/campaign-events",
            ]

            for topic in topics:
                try:
                    print(f"📡 Attempting to subscribe to: {topic}")
                    self.consumer = self.client.subscribe(
                        topic,
                        subscription_name="campaign-service-consumer",
                        consumer_type=pulsar.ConsumerType.Shared,
                    )
                    print(f"✅ Successfully subscribed to: {topic}")
                    break
                except Exception as e:
                    print(f"❌ Failed to subscribe to {topic}: {e}")
                    continue

            if not self.consumer:
                raise Exception("Failed to subscribe to any campaign topic")

        except Exception as e:
            print(f"❌ Failed to start campaign consumer: {e}")
            raise

    async def consume_messages(self):
        """Consume and process messages"""
        print("🎧 Starting to consume campaign messages...")

        while True:
            try:
                # Receive message with timeout
                msg = self.consumer.receive(timeout_millis=5000)

                # Process message
                await self.process_message(msg)

                # Acknowledge message
                self.consumer.acknowledge(msg)

            except pulsar.Timeout:
                print(".", end="", flush=True)  # Show we're still listening
                continue
            except Exception as e:
                print(f"\n❌ Error processing campaign message: {e}")
                await asyncio.sleep(1)

    async def process_message(self, msg):
        """Process received message and create database record"""
        try:
            # Parse message
            data = json.loads(msg.data().decode("utf-8"))
            print(f"\n📨 Received campaign event: {data}")

            # Create database session
            db = SessionLocal()

            try:
                # Create campaign record
                campaign = Campaign(
                    campaign_id=data.get("campaign_id", str(uuid4())),
                    name=data.get("name", "Unnamed Campaign"),
                    description=data.get("description", ""),
                    partner_id=data.get("partner_id", "unknown"),
                    status=data.get("status", "active"),
                    created_at=datetime.utcnow(),
                )

                db.add(campaign)
                db.commit()

                print(f"✅ Created campaign record: {campaign.campaign_id}")

            except Exception as e:
                db.rollback()
                print(f"❌ Database error: {e}")
                raise
            finally:
                db.close()

        except Exception as e:
            print(f"❌ Error processing campaign message: {e}")
            raise

    async def stop(self):
        """Stop consumer"""
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()


async def main():
    """Main function"""
    print("🚀 Starting Simple Campaign Service Consumer")

    consumer = SimpleCampaignConsumer()

    try:
        await consumer.start()
        await consumer.consume_messages()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
