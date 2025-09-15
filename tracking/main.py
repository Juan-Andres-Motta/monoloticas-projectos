from fastapi import FastAPI
from contextlib import asynccontextmanager

from config.container import Container
from config.database import engine, Base
from api.routers.tracking_router import create_tracking_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Initialize dependency injection container
    container = Container()
    app.state.container = container

    # Start Pulsar publisher (optional - service can work without it)
    pulsar_publisher = container.get("pulsar_publisher")
    try:
        await pulsar_publisher.start()
        print("✅ Pulsar publisher started successfully")
    except Exception as e:
        print(f"⚠️  Pulsar publisher failed to start: {e}")
        print("🔄 Service will continue without event publishing to Pulsar")
        # Set publisher to None so handlers can check if it's available
        container._services["pulsar_publisher"] = None

    yield

    # Clean up Pulsar publisher on shutdown
    pulsar_publisher = container.get("pulsar_publisher")
    if pulsar_publisher:
        await pulsar_publisher.stop()


app = FastAPI(title="Tracking Service", version="0.1.0", lifespan=lifespan)

# Add router
app.include_router(create_tracking_router())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
