from fastapi import FastAPI
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager

# Import routers but comment out Pulsar imports for now
from api.routers.campaign_router import create_campaign_router
from api.routers.evidence_router import create_evidence_router
from api.routers.payment_router import create_payment_router

# from messaging.pulsar_command_publisher import pulsar_command_publisher
# from messaging.pulsar_response_consumer import pulsar_response_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("🚀 Starting BFF Service...")

    # Disable Pulsar for now - just set mock state
    app.state.pulsar_publisher = None
    app.state.pulsar_consumer_tasks = []
    print("⚠️ Pulsar disabled for testing - service will run without event publishing")

    yield

    # Shutdown logic
    print("🛑 Shutting down BFF Service...")


app = FastAPI(
    title="Alpes Partners BFF",
    description="Backend for Frontend service for Alpes Partners platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add routers (they already have /api/v1 prefix)
app.include_router(create_campaign_router())
app.include_router(create_evidence_router())
app.include_router(create_payment_router())


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Alpes Partners BFF",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Global health check"""
    return {"status": "healthy", "service": "bff-service", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
