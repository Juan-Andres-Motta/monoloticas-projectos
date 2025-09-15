#!/usr/bin/env python3
"""
Simple Pulsar Consumer for Tracking Service
Listens to tracking events and creates database records
"""

import asyncio
import json
import os
import sys
import pulsar
from uuid import UUID
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tracking_user:tracking_password@localhost:5433/trackingdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TrackingEvent(Base):
    __tablename__ = "tracking_events"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True)
    partner_id = Column(String, nullable=False)
    campaign_id = Column(String, nullable=False) 
    visitor_id = Column(String, nullable=False)
    interaction_type = Column(String, nullable=False)
    source_url = Column(String)
    destination_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
print("🗄️ Creating database tables...")
Base.metadata.create_all(bind=engine)

class SimplePulsarConsumer:
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
                service_url,
                authentication=pulsar.AuthenticationToken(token)
            )
            
            # Try different topic variations
            topics = [
                f"persistent://{tenant}/{namespace}/tracking-events",
                f"persistent://public/default/tracking-events",
                f"non-persistent://{tenant}/{namespace}/tracking-events"
            ]
            
            for topic in topics:
                try:
                    print(f"📡 Attempting to subscribe to: {topic}")
                    self.consumer = self.client.subscribe(
                        topic,
                        subscription_name="tracking-service-consumer",
                        consumer_type=pulsar.ConsumerType.Shared
                    )
                    print(f"✅ Successfully subscribed to: {topic}")
                    break
                except Exception as e:
                    print(f"❌ Failed to subscribe to {topic}: {e}")
                    continue
            
            if not self.consumer:
                raise Exception("Failed to subscribe to any topic")
                
        except Exception as e:
            print(f"❌ Failed to start consumer: {e}")
            raise
    
    async def consume_messages(self):
        """Consume and process messages"""
        print("🎧 Starting to consume messages...")
        
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
                print(f"\n❌ Error processing message: {e}")
                await asyncio.sleep(1)
    
    async def process_message(self, msg):
        """Process received message and create database record"""
        try:
            # Parse message
            data = json.loads(msg.data().decode('utf-8'))
            print(f"\n📨 Received tracking event: {data}")
            
            # Create database session
            db = SessionLocal()
            
            try:
                # Create tracking event record
                tracking_event = TrackingEvent(
                    id=UUID(data.get("tracking_event_id", data.get("id"))),
                    partner_id=data["partner_id"],
                    campaign_id=data["campaign_id"],
                    visitor_id=data["visitor_id"],
                    interaction_type=data["interaction_type"],
                    source_url=data.get("source_url"),
                    destination_url=data.get("destination_url"),
                    created_at=datetime.utcnow()
                )
                
                db.add(tracking_event)
                db.commit()
                
                print(f"✅ Created tracking record: {tracking_event.id}")
                
            except Exception as e:
                db.rollback()
                print(f"❌ Database error: {e}")
                raise
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            raise
    
    async def stop(self):
        """Stop consumer"""
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()

async def main():
    """Main function"""
    print("🚀 Starting Simple Tracking Service Consumer")
    
    consumer = SimplePulsarConsumer()
    
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
