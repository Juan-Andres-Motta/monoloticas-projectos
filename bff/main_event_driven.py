"""
Campaign Service Main Entry Point
Supports both HTTP API mode and Event-Driven mode for microservice communication.
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

from config.container import Container
from config.database import engine, Base


# Global container for dependency injection
container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    try:
        # Database setup
        print("🗄️ Setting up database...")
        # Create database tables synchronously
        Base.metadata.create_all(bind=engine)

        # Initialize container (no async init needed)
        print("🔧 Initializing dependency container...")

        print("✅ Campaign service started successfully")
        yield

    except Exception as e:
        print(f"❌ Error during startup: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        print("🧹 Cleaning up resources...")
        # No async cleanup needed for now


async def start_http_mode():
    """Start the service in HTTP API mode (traditional microservice)"""
    print("🌐 Starting Campaign Service in HTTP API mode...")

    # Create FastAPI app
    app = FastAPI(title="Campaign Service", version="0.1.0", lifespan=lifespan)

    # Add health endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "campaign-service",
            "version": "0.1.0",
            "mode": "http",
        }

    # Add campaign router
    from api.routers.campaign_router import create_campaign_router

    app.include_router(create_campaign_router())

    # Start server
    import uvicorn

    port = int(os.getenv("CAMPAIGN_SERVICE_PORT", 8002))
    print(f"🚀 Campaign Service HTTP API available at http://localhost:{port}")
    print(f"📖 API Documentation: http://localhost:{port}/docs")

    uvicorn.run(app, host="0.0.0.0", port=port)


async def start_event_driven_mode():
    """Start the service in Event-Driven mode (listens to Pulsar events)"""
    print("📡 Starting Campaign Service in Event-Driven mode...")

    try:
        # Initialize database and container manually since we're not using FastAPI
        print("🗄️ Setting up database...")
        # Create database tables synchronously
        Base.metadata.create_all(bind=engine)

        print("🔧 Initializing dependency container...")
        # Container is already initialized

        # Start event-driven service
        from messaging.event_handlers import start_event_driven_campaign_service

        await start_event_driven_campaign_service(container)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Campaign Service...")
        # No async cleanup needed
    except Exception as e:
        print(f"❌ Error in event-driven mode: {e}")
        # No async cleanup needed
        sys.exit(1)


async def start_hybrid_mode():
    """Start the service in hybrid mode (both HTTP and Event-Driven)"""
    print("🔄 Starting Campaign Service in Hybrid mode...")

    # Create FastAPI app for health checks and monitoring
    app = FastAPI(title="Campaign Service", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "campaign-service",
            "version": "0.1.0",
            "mode": "hybrid",
            "features": ["http-api", "event-driven"],
        }

    # Add minimal API router (for backwards compatibility or admin operations)
    from api.routers.campaign_router import create_campaign_router

    app.include_router(create_campaign_router())

    # Start HTTP server in background
    import uvicorn

    port = int(os.getenv("CAMPAIGN_SERVICE_PORT", 8002))

    async def run_http_server():
        config = uvicorn.Config(app, host="0.0.0.0", port=port)
        server = uvicorn.Server(config)
        await server.serve()

    async def run_event_consumer():
        # Small delay to ensure HTTP server starts first
        await asyncio.sleep(2)
        from messaging.event_handlers import start_event_driven_campaign_service

        await start_event_driven_campaign_service(container)

    # Run both HTTP server and event consumer concurrently
    try:
        print(f"🚀 Campaign Service Hybrid mode:")
        print(f"   📡 Event consumer: Listening for Pulsar events")
        print(f"   🌐 HTTP API: http://localhost:{port}")
        print(f"   📖 API Documentation: http://localhost:{port}/docs")

        await asyncio.gather(run_http_server(), run_event_consumer())

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Campaign Service...")
    except Exception as e:
        print(f"❌ Error in hybrid mode: {e}")
        sys.exit(1)


def main():
    """Main entry point - determine mode from environment variable"""

    # Get mode from environment variable
    mode = os.getenv("CAMPAIGN_SERVICE_MODE", "http").lower()

    print(f"🎯 Campaign Service starting in '{mode}' mode...")

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
