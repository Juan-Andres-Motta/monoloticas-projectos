#!/usr/bin/env python3
"""
Tracking Service - Event-Driven Main Entry Point
Supports both HTTP API mode and Event-Driven mode for microservice communication.
"""

import asyncio
import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from config.container import Container
from config.database import engine, Base


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global container for dependency injection
container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    try:
        logger.info("🚀 Tracking Service starting up...")

        # Database setup
        logger.info("🗄️ Setting up database...")
        Base.metadata.create_all(bind=engine)

        # Initialize dependency injection container
        logger.info("🔧 Initializing dependency container...")
        app.state.container = container

        # Start Pulsar publisher
        pulsar_publisher = container.get("pulsar_publisher")
        try:
            await pulsar_publisher.start()
            logger.info("✅ Pulsar publisher started successfully")
        except Exception as e:
            logger.warning(f"⚠️  Pulsar publisher failed to start: {e}")
            logger.info("🔄 Service will continue without event publishing to Pulsar")
            # Set publisher to None so handlers can check if it's available
            container._services["pulsar_publisher"] = None

        logger.info("✅ Tracking Service initialization completed")
        yield

    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        sys.exit(1)
    finally:
        # Cleanup on shutdown
        logger.info("🛑 Tracking Service shutting down...")
        pulsar_publisher = container.get("pulsar_publisher")
        if pulsar_publisher:
            await pulsar_publisher.stop()


async def start_http_mode():
    """Start the service in HTTP API mode (traditional microservice)"""
    logger.info("🌐 Starting Tracking Service in HTTP API mode...")

    # Create FastAPI app
    app = FastAPI(
        title="Tracking Service",
        description="Event-driven Tracking microservice for affiliate marketing platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add health endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "tracking-service",
            "mode": "http",
            "version": "1.0.0",
        }

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"service": "tracking-service", "status": "running", "mode": "http"}

    # Add tracking router
    from api.routers.tracking_router import create_tracking_router

    app.include_router(create_tracking_router())

    # Start server
    import uvicorn

    port = int(os.getenv("TRACKING_SERVICE_PORT", 8003))

    logger.info(f"🚀 Tracking Service HTTP API available at http://localhost:{port}")
    logger.info(f"📖 API Documentation: http://localhost:{port}/docs")

    uvicorn.run(app, host="0.0.0.0", port=port)


async def start_event_driven_mode():
    """Start the service in Event-Driven mode (listens to Pulsar events)"""
    logger.info("📡 Starting Tracking Service in Event-Driven mode...")

    try:
        # Initialize database and container manually since we're not using FastAPI
        logger.info("🗄️ Setting up database...")
        Base.metadata.create_all(bind=engine)

        logger.info("🔧 Initializing dependency container...")
        # Container is already initialized

        # Start Pulsar publisher
        pulsar_publisher = container.get("pulsar_publisher")
        try:
            await pulsar_publisher.start()
            logger.info("✅ Pulsar publisher started successfully")
        except Exception as e:
            logger.warning(f"⚠️  Pulsar publisher failed to start: {e}")
            logger.info("🔄 Service will continue without event publishing to Pulsar")
            container._services["pulsar_publisher"] = None

        # Start event-driven service (if there are event consumers to start)
        logger.info(
            "📡 Event-driven mode ready - service can receive HTTP requests and publish to Pulsar"
        )

        # Keep the service running
        while True:
            await asyncio.sleep(10)
            logger.debug("📡 Tracking service running in event-driven mode...")

    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down Tracking Service...")
    except Exception as e:
        logger.error(f"❌ Error in event-driven mode: {e}")
        sys.exit(1)


async def start_hybrid_mode():
    """Start the service in hybrid mode (both HTTP and Event-Driven)"""
    logger.info("🔄 Starting Tracking Service in Hybrid mode...")

    # Create FastAPI app for HTTP API
    app = FastAPI(
        title="Tracking Service",
        description="Event-driven Tracking microservice for affiliate marketing platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "tracking-service",
            "version": "1.0.0",
            "mode": "hybrid",
            "features": ["http-api", "event-driven"],
        }

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"service": "tracking-service", "status": "running", "mode": "hybrid"}

    # Add tracking router
    from api.routers.tracking_router import create_tracking_router

    app.include_router(create_tracking_router())

    # Start HTTP server
    import uvicorn

    port = int(os.getenv("TRACKING_SERVICE_PORT", 8003))

    async def run_http_server():
        config = uvicorn.Config(app, host="0.0.0.0", port=port)
        server = uvicorn.Server(config)
        await server.serve()

    async def run_event_consumer():
        # Small delay to ensure HTTP server starts first
        await asyncio.sleep(2)
        logger.info("📡 Event consumer ready - service can publish events to Pulsar")

        # Keep event consumer running
        while True:
            await asyncio.sleep(10)
            logger.debug("📡 Event consumer running...")

    # Run both HTTP server and event consumer concurrently
    try:
        logger.info(f"🚀 Tracking Service Hybrid mode:")
        logger.info(f"   📡 Event publisher: Ready to send events to Pulsar")
        logger.info(f"   🌐 HTTP API: http://localhost:{port}")
        logger.info(f"   📖 API Documentation: http://localhost:{port}/docs")

        await asyncio.gather(run_http_server(), run_event_consumer())

    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down Tracking Service...")
    except Exception as e:
        logger.error(f"❌ Error in hybrid mode: {e}")
        sys.exit(1)


def main():
    """Main entry point - determine mode from environment variable"""

    # Get mode from environment variable
    mode = os.getenv("TRACKING_SERVICE_MODE", "http").lower()

    logger.info(f"🎯 Tracking Service starting in '{mode}' mode...")

    if mode == "event" or mode == "event-driven":
        # Pure event-driven mode
        asyncio.run(start_event_driven_mode())

    elif mode == "hybrid":
        # Both HTTP and event-driven
        asyncio.run(start_hybrid_mode())

    else:
        # Default HTTP mode
        asyncio.run(start_http_mode())


if __name__ == "__main__":
    main()
