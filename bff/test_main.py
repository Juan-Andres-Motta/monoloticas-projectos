#!/usr/bin/env python3
"""
Simple BFF test script to verify basic functionality without Pulsar dependencies
"""
import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="BFF Test", description="Simple test to verify BFF basic functionality"
)


@app.get("/")
async def root():
    return {"message": "BFF Test Service is running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "bff-test"}


if __name__ == "__main__":
    print("🚀 Starting BFF Test Service...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
