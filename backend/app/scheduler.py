"""APScheduler-based main loop for the trading system.

Runs every 15 minutes to:
1. Fetch and store OHLCV / Funding Rate / HLP data
2. Calculate technical indicators
3. Generate AI payload (Step 2 onwards: trigger AI agents)
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import AsyncSessionLocal
from app.services.data_collector import (
    fetch_and_store_all_timeframes,
    fetch_and_store_funding_rates,
    fetch_and_store_hlp_data,
)
from app.services.indicators import calculate_and_store_indicators, generate_ai_payload

logger = logging.getLogger(__name__)

SYMBOL = "BTC"
TIMEFRAMES = ["1m", "15m", "30m", "1h"]


async def run_data_collection() -> None:
    """Collect all market data and update technical indicators."""
    async with AsyncSessionLocal() as db:
        logger.info("=== Data collection cycle started ===")

        # Fetch OHLCV for all timeframes
        counts = await fetch_and_store_all_timeframes(db, symbol=SYMBOL)
        logger.info("OHLCV fetch results: %s", counts)

        # Fetch funding rates
        await fetch_and_store_funding_rates(db, symbol=SYMBOL)

        # Fetch HLP data
        await fetch_and_store_hlp_data(db)

        # Recalculate indicators for all timeframes
        for tf in TIMEFRAMES:
            await calculate_and_store_indicators(db, symbol=SYMBOL, timeframe=tf)

        # Generate AI payload (logged for now; Step 2 will pass this to agents)
        payload = await generate_ai_payload(db, symbol=SYMBOL)
        logger.info(
            "AI payload ready: symbol=%s price=%s",
            payload["symbol"],
            payload.get("current_price"),
        )

        logger.info("=== Data collection cycle completed ===")


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    # Run at the start of every 15-minute mark (e.g., :00, :15, :30, :45)
    scheduler.add_job(
        run_data_collection,
        CronTrigger(minute="0,15,30,45"),
        id="data_collection",
        name="Market data collection + indicator calculation",
        misfire_grace_time=60,
    )
    return scheduler


async def main() -> None:
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler started. Waiting for jobs...")
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
