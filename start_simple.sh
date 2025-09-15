#!/bin/bash

# Simple Event-Driven Setup Script
# Starts all services with one command

set -e

echo "🚀 Starting Simple Event-Driven Microservices"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check environment variables
if [ -z "$PULSAR_SERVICE_URL" ] || [ -z "$PULSAR_TOKEN" ]; then
    echo "❌ Please set PULSAR_SERVICE_URL and PULSAR_TOKEN environment variables"
    exit 1
fi

# Create simple docker-compose file
cat > docker-compose.simple.yml << 'EOF'
version: '3.8'

services:
  # Database for tracking service
  tracking-db:
    image: postgres:15
    environment:
      POSTGRES_DB: trackingdb
      POSTGRES_USER: tracking_user
      POSTGRES_PASSWORD: tracking_password
    ports:
      - "5432:5432"
    volumes:
      - tracking_db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tracking_user -d trackingdb"]
      interval: 10s
      timeout: 5s
      retries: 5

  # BFF Service - Receives HTTP requests and publishes to Pulsar
  bff-service:
    build:
      context: ./bff
      dockerfile: Dockerfile
    environment:
      - BFF_SERVICE_PORT=8001
      - PULSAR_SERVICE_URL=${PULSAR_SERVICE_URL}
      - PULSAR_TOKEN=${PULSAR_TOKEN}
      - PULSAR_TENANT=${PULSAR_TENANT:-miso-1-2025}
      - PULSAR_NAMESPACE=${PULSAR_NAMESPACE:-default}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-simple-secret-key}
      - JWT_ALGORITHM=HS256
    ports:
      - "8001:8001"
    restart: unless-stopped
    command: python -m uvicorn main:app --host 0.0.0.0 --port 8001
    volumes:
      - ./bff:/app
    working_dir: /app

  # Tracking Service - Listens to Pulsar and creates DB records
  tracking-service:
    build:
      context: ./tracking
      dockerfile: Dockerfile
    environment:
      - TRACKING_SERVICE_MODE=event
      - DATABASE_URL=postgresql://tracking_user:tracking_password@tracking-db:5432/trackingdb
      - PULSAR_SERVICE_URL=${PULSAR_SERVICE_URL}
      - PULSAR_TOKEN=${PULSAR_TOKEN}
      - PULSAR_TENANT=${PULSAR_TENANT:-miso-1-2025}
      - PULSAR_NAMESPACE=${PULSAR_NAMESPACE:-default}
    depends_on:
      tracking-db:
        condition: service_healthy
    restart: unless-stopped
    command: python simple_consumer.py
    volumes:
      - ./tracking:/app
    working_dir: /app

volumes:
  tracking_db_data:
EOF

echo -e "${BLUE}📝 Creating simple Pulsar consumer for tracking service...${NC}"

# Create simple consumer script
cat > tracking/simple_consumer.py << 'EOF'
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
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tracking_user:tracking_password@localhost:5432/trackingdb")
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
EOF

echo -e "${BLUE}📝 Creating simple Pulsar publisher for BFF service...${NC}"

# Create simple publisher for BFF
cat > bff/simple_publisher.py << 'EOF'
#!/usr/bin/env python3
"""
Simple Pulsar Publisher for BFF Service
Publishes tracking events to Pulsar
"""

import json
import os
import pulsar
from uuid import uuid4
from datetime import datetime

class SimplePulsarPublisher:
    def __init__(self):
        self.client = None
        self.producer = None
        
    async def start(self):
        """Start Pulsar publisher"""
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
                    print(f"📡 Attempting to create producer for: {topic}")
                    self.producer = self.client.create_producer(topic)
                    print(f"✅ Successfully created producer for: {topic}")
                    break
                except Exception as e:
                    print(f"❌ Failed to create producer for {topic}: {e}")
                    continue
            
            if not self.producer:
                raise Exception("Failed to create producer for any topic")
                
        except Exception as e:
            print(f"❌ Failed to start publisher: {e}")
            raise
    
    async def publish_tracking_event(self, event_data):
        """Publish tracking event"""
        try:
            # Add event ID and timestamp
            event_data["tracking_event_id"] = str(uuid4())
            event_data["timestamp"] = datetime.utcnow().isoformat()
            event_data["event_type"] = "tracking_event.created"
            
            # Send message
            message_data = json.dumps(event_data).encode('utf-8')
            self.producer.send(message_data)
            
            print(f"📤 Published tracking event: {event_data['tracking_event_id']}")
            return event_data["tracking_event_id"]
            
        except Exception as e:
            print(f"❌ Failed to publish event: {e}")
            raise
    
    async def stop(self):
        """Stop publisher"""
        if self.producer:
            self.producer.close()
        if self.client:
            self.client.close()

# Global publisher instance
publisher = SimplePulsarPublisher()
EOF

echo -e "${BLUE}📝 Creating simple BFF main file...${NC}"

# Create simple BFF main
cat > bff/simple_main.py << 'EOF'
#!/usr/bin/env python3
"""
Simple BFF Service
Receives HTTP requests and publishes to Pulsar
"""

import asyncio
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from simple_publisher import publisher

class TrackingEventRequest(BaseModel):
    partner_id: str
    campaign_id: str
    visitor_id: str
    interaction_type: str
    source_url: str = None
    destination_url: str = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    print("🚀 Starting BFF Service...")
    
    # Start Pulsar publisher
    try:
        await publisher.start()
        print("✅ Pulsar publisher started")
    except Exception as e:
        print(f"⚠️ Pulsar publisher failed: {e}")
    
    yield
    
    # Cleanup
    print("🛑 Shutting down BFF Service...")
    await publisher.stop()

app = FastAPI(
    title="Simple BFF Service",
    description="Receives requests and publishes to Pulsar",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bff-service"}

@app.post("/api/v1/tracking/events")
async def create_tracking_event(request: TrackingEventRequest):
    """Create tracking event via Pulsar"""
    try:
        # Publish to Pulsar
        event_id = await publisher.publish_tracking_event(request.dict())
        
        return {
            "tracking_event_id": event_id,
            "status": "published",
            "message": "Event published to Pulsar successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish event: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BFF_SERVICE_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

echo -e "${GREEN}✅ Simple setup files created!${NC}"
echo ""
echo -e "${BLUE}🚀 Starting services...${NC}"

# Start services
docker-compose -f docker-compose.simple.yml up -d

echo ""
echo -e "${GREEN}🎉 Simple Event-Driven Services Started!${NC}"
echo ""
echo "📊 Service Status:"
echo "  BFF Service:     http://localhost:8001"
echo "  API Docs:        http://localhost:8001/docs" 
echo "  Database:        localhost:5432"
echo ""
echo "🧪 Test the flow:"
echo 'curl -X POST "http://localhost:8001/api/v1/tracking/events" \'
echo '     -H "Content-Type: application/json" \'
echo '     -d "{\"partner_id\":\"partner-123\",\"campaign_id\":\"campaign-456\",\"visitor_id\":\"visitor-789\",\"interaction_type\":\"click\"}"'
echo ""
echo "📋 Check logs:"
echo "  docker-compose -f docker-compose.simple.yml logs -f"
echo ""
echo "🛑 Stop services:"
echo "  docker-compose -f docker-compose.simple.yml down"
