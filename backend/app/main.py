"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import history, logs, position, settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="Magi Trade API",
    description="Hyperliquid AI-Driven Multi-Agent Trading System",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(position.router)
app.include_router(logs.router)
app.include_router(history.router)
app.include_router(settings.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
