#!/usr/bin/env python3
"""
Simple Pulsar Consumer for Payment Service
Listens to payment events and creates database records
"""

import asyncio
import json
import os
import sys
import pulsar
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, Column, String, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# Database setup - Use psycopg2 URL format
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://payment_user:payment_password@localhost:5437/paymentdb",
)
# Convert asyncpg URL to psycopg2 format if needed
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(DATABASE_URL + "?client_encoding=utf8")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Payment(Base):
    __tablename__ = "payments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    payment_id = Column(String, nullable=False, unique=True)
    partner_id = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="pending")
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
print("🗄️ Creating payment database tables...")
Base.metadata.create_all(bind=engine)


class SimplePaymentConsumer:
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

            # Try different topic variations for payments
            topics = [
                f"persistent://{tenant}/{namespace}/payment-events",
                f"persistent://public/default/payment-events",
                f"non-persistent://{tenant}/{namespace}/payment-events",
            ]

            for topic in topics:
                try:
                    print(f"📡 Attempting to subscribe to: {topic}")
                    self.consumer = self.client.subscribe(
                        topic,
                        subscription_name="payment-service-consumer",
                        consumer_type=pulsar.ConsumerType.Shared,
                    )
                    print(f"✅ Successfully subscribed to: {topic}")
                    break
                except Exception as e:
                    print(f"❌ Failed to subscribe to {topic}: {e}")
                    continue

            if not self.consumer:
                raise Exception("Failed to subscribe to any payment topic")

        except Exception as e:
            print(f"❌ Failed to start payment consumer: {e}")
            raise

    async def consume_messages(self):
        """Consume and process messages"""
        print("🎧 Starting to consume payment messages...")

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
                print(f"\n❌ Error processing payment message: {e}")
                await asyncio.sleep(1)

    async def process_message(self, msg):
        """Process received message and create database record"""
        try:
            # Parse message
            data = json.loads(msg.data().decode("utf-8"))
            print(f"\n📨 Received payment event: {data}")

            # Create database session
            db = SessionLocal()

            try:
                # Create payment record
                payment = Payment(
                    payment_id=data.get("payment_id", str(uuid4())),
                    partner_id=data.get("partner_id", "unknown"),
                    amount=Decimal(str(data.get("amount", "0.00"))),
                    currency=data.get("currency", "USD"),
                    status=data.get("status", "pending"),
                    description=data.get("description", ""),
                    created_at=datetime.utcnow(),
                )

                db.add(payment)
                db.commit()

                print(f"✅ Created payment record: {payment.payment_id}")

            except Exception as e:
                db.rollback()
                print(f"❌ Database error: {e}")
                raise
            finally:
                db.close()

        except Exception as e:
            print(f"❌ Error processing payment message: {e}")
            raise

    async def stop(self):
        """Stop consumer"""
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()


async def main():
    """Main function"""
    print("🚀 Starting Simple Payment Service Consumer")

    consumer = SimplePaymentConsumer()

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
