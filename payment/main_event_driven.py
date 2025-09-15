#!/usr/bin/env python3
"""
Payment Service - Event-Driven Main Entry Point
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
    logger.info("🚀 Payment Service starting up...")

    # Initialize services here
    logger.info("✅ Payment Service initialization completed")

    yield

    # Cleanup on shutdown
    logger.info("🛑 Payment Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Payment Service",
    description="Event-driven Payment microservice for affiliate marketing platform",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "payment-service",
        "mode": "event-driven",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "payment-service", "status": "running", "mode": "event-driven"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PAYMENT_SERVICE_PORT", 8005))

    logger.info(f"🚀 Starting Payment Service on port {port}")

    uvicorn.run(
        "main_event_driven:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
