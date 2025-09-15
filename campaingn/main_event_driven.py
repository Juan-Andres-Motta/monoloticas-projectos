#!/usr/bin/env python3
"""
Campaign Service - Event-Driven Main Entry Point
"""

import asyncio
import os
import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Campaign Service starting up...")

    # Initialize services here
    logger.info("✅ Campaign Service initialization completed")

    yield

    # Cleanup on shutdown
    logger.info("🛑 Campaign Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Campaign Service",
    description="Event-driven Campaign microservice for affiliate marketing platform",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "campaign-service",
        "mode": "event-driven",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "campaign-service", "status": "running", "mode": "event-driven"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("CAMPAIGN_SERVICE_PORT", 8002))

    logger.info(f"🚀 Starting Campaign Service on port {port}")

    uvicorn.run(
        "main_event_driven:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
