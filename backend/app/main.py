"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import history, logs, position, settings
from app.scheduler import create_scheduler, run_data_collection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler started.")

    # Run initial data collection immediately on startup
    logger.info("Running initial data collection...")
    try:
        await run_data_collection()
    except Exception:
        logger.exception("Initial data collection failed")

    yield

    scheduler.shutdown()
    logger.info("Scheduler stopped.")


app = FastAPI(
    title="Magi Trade API",
    description="Hyperliquid AI-Driven Multi-Agent Trading System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://magi_frontend:3000",  # Docker internal network
    ],
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
