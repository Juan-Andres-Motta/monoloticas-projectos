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
