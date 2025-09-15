from fastapi import FastAPI
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager

from api.routers.campaign_router import create_campaign_router
from api.routers.evidence_router import create_evidence_router
from api.routers.payment_router import create_payment_router
from messaging.pulsar_command_publisher import pulsar_command_publisher
from messaging.pulsar_response_consumer import pulsar_response_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("🚀 Starting BFF Service...")

    # Initialize Pulsar publisher
    try:
        await pulsar_command_publisher.start()
        app.state.pulsar_publisher = pulsar_command_publisher
        print("✅ Pulsar command publisher started")
    except Exception as e:
        print(f"⚠️  Pulsar publisher failed to start: {e}")
        print("🔄 Service will continue without command publishing")
        app.state.pulsar_publisher = None

    # Initialize Pulsar response consumer
    try:
        consumer_tasks = await pulsar_response_consumer.start()
        app.state.pulsar_consumer_tasks = consumer_tasks
        print("✅ Pulsar response consumer started")
    except Exception as e:
        print(f"⚠️  Pulsar consumer failed to start: {e}")
        print("🔄 Service will continue without response consuming")
        app.state.pulsar_consumer_tasks = []

    # TODO: Initialize other services
    # - Database connections
    # - External API clients
    # - Dependency injection container

    yield

    # Shutdown logic
    print("🛑 Shutting down BFF Service...")

    # Stop Pulsar services
    if hasattr(app.state, 'pulsar_publisher') and app.state.pulsar_publisher:
        await app.state.pulsar_publisher.stop()

    if hasattr(app.state, 'pulsar_consumer_tasks'):
        await pulsar_response_consumer.stop()
        for task in app.state.pulsar_consumer_tasks:
            task.cancel()

    # TODO: Cleanup other resources
    # - Close database connections
    # - Close external clients


app = FastAPI(
    title="Alpes Partners BFF API",
    description="""
    Backend for Frontend service for Alpes Partners platform.

    This API provides unified access to campaign management, evidence upload,
    and payment request functionality. All endpoints require JWT authentication.

    ## Authentication

    All endpoints (except health checks) require a valid JWT token in the Authorization header:

    ```
    Authorization: Bearer <your-jwt-token>
    ```

    Use the JWT generation script to create test tokens:
    ```bash
    cd bff && python generate_jwt.py
    ```

    ## Event Flow

    This BFF publishes commands to Apache Pulsar topics:
    - `bff-campaign-accept-v1` - Campaign acceptance commands
    - `bff-evidence-upload-v1` - Evidence upload commands
    - `bff-payment-request-v1` - Payment request commands

    These commands are processed by future microservices (not tracking/commission).
    """,
    version="0.1.0",
    contact={
        "name": "Alpes Partners Development Team",
        "email": "dev@alpes-partners.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "campaigns",
            "description": "Campaign management operations - accept campaigns and manage participation.",
        },
        {
            "name": "evidence",
            "description": "Evidence upload operations - submit proof of campaign participation.",
        },
        {
            "name": "payments",
            "description": "Payment request operations - request payments for completed campaigns.",
        },
        {
            "name": "health",
            "description": "Service health and status endpoints.",
        },
    ]
)

# Add JWT security scheme to OpenAPI
app.openapi_schema = None  # Force regeneration

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add JWT Bearer security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for authentication. Use the JWT generation script to create test tokens: `cd bff && python generate_jwt.py`"
        }
    }

    # Apply security to all endpoints except health checks
    for path, path_item in openapi_schema["paths"].items():
        if "/health" not in path and path != "/":
            for operation in path_item.values():
                if isinstance(operation, dict) and "security" not in operation:
                    operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Security scheme for JWT
security = HTTPBearer()

# Include routers
app.include_router(create_campaign_router())
app.include_router(create_evidence_router())
app.include_router(create_payment_router())


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Alpes Partners BFF",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Global health check"""
    return {
        "status": "healthy",
        "service": "alpes-partners-bff",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)