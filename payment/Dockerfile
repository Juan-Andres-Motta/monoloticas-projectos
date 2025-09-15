# ===========================================
# PAYMENT SERVICE DOCKERFILE
# ===========================================
# Multi-stage build for Python microservice

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies required for building
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root \
    && rm -rf /tmp/poetry_cache

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
    && chown -R user:user /app

USER user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PAYMENT_SERVICE_PORT:-8005}/health || exit 1

# Default command
CMD ["python", "main_event_driven.py"]
