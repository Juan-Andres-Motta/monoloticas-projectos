from fastapi import FastAPI
from contextlib import asynccontextmanager

from config.container import Container
from config.database import engine, Base
from api.routers.commission_router import create_commission_router
from infrastructure.messaging.pulsar_consumer import start_pulsar_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Initialize dependency injection container
    container = Container()
    app.state.container = container

    # Start Pulsar consumer for tracking events
    consumer_task = await start_pulsar_consumer(container)

    yield

    # Clean up consumer on shutdown
    if consumer_task:
        consumer_task.cancel()


app = FastAPI(title="Commission Service", version="0.1.0", lifespan=lifespan)

# Add router
app.include_router(create_commission_router())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
