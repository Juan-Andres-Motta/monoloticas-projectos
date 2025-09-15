#!/usr/bin/env python3
"""
Commission Service - Event-Driven Main Entry Point
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
from infrastructure.messaging.pulsar_consumer import start_pulsar_consumer


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
        logger.info("🚀 Commission Service starting up...")

        # Database setup
        logger.info("🗄️ Setting up database...")
        Base.metadata.create_all(bind=engine)

        # Initialize dependency injection container
        logger.info("🔧 Initializing dependency container...")
        app.state.container = container

        # Start Pulsar consumer for tracking events
        try:
            consumer_task = await start_pulsar_consumer(container)
            logger.info("✅ Pulsar consumer started successfully")
            # Store consumer task for cleanup
            app.state.consumer_task = consumer_task
        except Exception as e:
            logger.warning(f"⚠️  Pulsar consumer failed to start: {e}")
            logger.info(
                "🔄 Service will continue without event consumption from Pulsar"
            )
            app.state.consumer_task = None

        logger.info("✅ Commission Service initialization completed")
        yield

    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        sys.exit(1)
    finally:
        # Cleanup on shutdown
        logger.info("🛑 Commission Service shutting down...")
        consumer_task = getattr(app.state, "consumer_task", None)
        if consumer_task:
            consumer_task.cancel()


async def start_http_mode():
    """Start the service in HTTP API mode (traditional microservice)"""
    logger.info("🌐 Starting Commission Service in HTTP API mode...")

    # Create FastAPI app
    app = FastAPI(
        title="Commission Service",
        description="Event-driven Commission microservice for affiliate marketing platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add health endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "commission-service",
            "mode": "http",
            "version": "1.0.0",
        }

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"service": "commission-service", "status": "running", "mode": "http"}

    # Add commission router
    from api.routers.commission_router import create_commission_router

    app.include_router(create_commission_router())

    # Start server
    import uvicorn

    port = int(os.getenv("COMMISSION_SERVICE_PORT", 8004))

    logger.info(f"🚀 Commission Service HTTP API available at http://localhost:{port}")
    logger.info(f"📖 API Documentation: http://localhost:{port}/docs")

    uvicorn.run(app, host="0.0.0.0", port=port)


async def start_event_driven_mode():
    """Start the service in Event-Driven mode (listens to Pulsar events)"""
    logger.info("📡 Starting Commission Service in Event-Driven mode...")

    try:
        # Initialize database and container manually since we're not using FastAPI
        logger.info("🗄️ Setting up database...")
        Base.metadata.create_all(bind=engine)

        logger.info("🔧 Initializing dependency container...")
        # Container is already initialized

        # Start Pulsar consumer for tracking events
        try:
            consumer_task = await start_pulsar_consumer(container)
            logger.info("✅ Pulsar consumer started successfully")
            logger.info(
                "🎧 Commission Service is now listening for tracking events from Pulsar"
            )

            # Wait for the consumer task to complete (it runs indefinitely)
            await consumer_task

        except Exception as e:
            logger.error(f"❌ Pulsar consumer failed to start: {e}")
            logger.error("💡 Make sure PULSAR_TOKEN is set and Pulsar is accessible")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down Commission Service...")
    except Exception as e:
        logger.error(f"❌ Error in event-driven mode: {e}")
        sys.exit(1)


async def start_hybrid_mode():
    """Start the service in hybrid mode (both HTTP and Event-Driven)"""
    logger.info("🔄 Starting Commission Service in Hybrid mode...")

    # Create FastAPI app for HTTP API
    app = FastAPI(
        title="Commission Service",
        description="Event-driven Commission microservice for affiliate marketing platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "commission-service",
            "version": "1.0.0",
            "mode": "hybrid",
            "features": ["http-api", "event-driven"],
        }

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"service": "commission-service", "status": "running", "mode": "hybrid"}

    # Add commission router
    from api.routers.commission_router import create_commission_router

    app.include_router(create_commission_router())

    # Start HTTP server
    import uvicorn

    port = int(os.getenv("COMMISSION_SERVICE_PORT", 8004))

    async def run_http_server():
        config = uvicorn.Config(app, host="0.0.0.0", port=port)
        server = uvicorn.Server(config)
        await server.serve()

    async def run_event_consumer():
        # Small delay to ensure HTTP server starts first
        await asyncio.sleep(2)
        logger.info(
            "🎧 Commission Service is now listening for tracking events from Pulsar"
        )

        # The consumer will run indefinitely, which is what we want
        # The consumer task from lifespan will handle the actual consumption

    # Run both HTTP server and event consumer concurrently
    try:
        logger.info(f"🚀 Commission Service Hybrid mode:")
        logger.info(f"   📡 Event consumer: Listening for tracking events from Pulsar")
        logger.info(f"   🌐 HTTP API: http://localhost:{port}")
        logger.info(f"   📖 API Documentation: http://localhost:{port}/docs")

        await asyncio.gather(run_http_server(), run_event_consumer())

    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down Commission Service...")
    except Exception as e:
        logger.error(f"❌ Error in hybrid mode: {e}")
        sys.exit(1)


def main():
    """Main entry point - determine mode from environment variable"""

    # Get mode from environment variable
    mode = os.getenv("COMMISSION_SERVICE_MODE", "http").lower()

    logger.info(f"🎯 Commission Service starting in '{mode}' mode...")

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
