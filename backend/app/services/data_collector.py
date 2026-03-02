"""Hyperliquid data collection module.

Fetches OHLCV, Funding Rate, and HLP data from the Hyperliquid API
and persists them to MySQL with UPSERT semantics to prevent duplicates.
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = logging.getLogger(__name__)

# Timeframes supported by Hyperliquid candle API
TIMEFRAMES = ["1m", "15m", "30m", "1h"]

# Map our timeframe strings to Hyperliquid interval codes
_TF_MAP: dict[str, str] = {
    "1m": "1",
    "15m": "15",
    "30m": "30",
    "1h": "60",
}


def _get_info_client():
    """Create a Hyperliquid Info client (mainnet)."""
    from hyperliquid.info import Info
    from hyperliquid.utils import constants

    return Info(constants.MAINNET_API_URL, skip_ws=True)


async def fetch_and_store_ohlcv(
    db: AsyncSession,
    symbol: str = "BTC",
    timeframe: str = "15m",
    lookback_bars: int = 500,
) -> int:
    """Fetch OHLCV candles from Hyperliquid and upsert into market_data.

    Args:
        db: Async SQLAlchemy session.
        symbol: Trading symbol (e.g. "BTC").
        timeframe: One of "1m", "15m", "30m", "1h".
        lookback_bars: Number of bars to fetch.

    Returns:
        Number of rows upserted.
    """
    if timeframe not in _TF_MAP:
        raise ValueError(f"Unsupported timeframe: {timeframe}. Use one of {list(_TF_MAP)}")

    info = _get_info_client()
    interval = _TF_MAP[timeframe]

    end_time = int(datetime.utcnow().timestamp() * 1000)
    # Approximate start time based on timeframe
    minutes_per_bar = {"1m": 1, "15m": 15, "30m": 30, "1h": 60}[timeframe]
    start_time = end_time - lookback_bars * minutes_per_bar * 60 * 1000

    logger.info("Fetching %s %s candles for %s", lookback_bars, timeframe, symbol)
    candles = info.candles_snapshot(symbol, interval, start_time, end_time)

    if not candles:
        logger.warning("No candles returned for %s %s", symbol, timeframe)
        return 0

    rows = []
    for c in candles:
        # Hyperliquid candle fields: t (open time ms), o, h, l, c, v
        ts = datetime.utcfromtimestamp(c["t"] / 1000)
        rows.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": ts,
                "open": float(c["o"]),
                "high": float(c["h"]),
                "low": float(c["l"]),
                "close": float(c["c"]),
                "volume": float(c["v"]),
                "created_at": datetime.utcnow(),
            }
        )

    upsert_sql = text(
        """
        INSERT INTO market_data (symbol, timeframe, timestamp, open, high, low, close, volume, created_at)
        VALUES (:symbol, :timeframe, :timestamp, :open, :high, :low, :close, :volume, :created_at)
        ON DUPLICATE KEY UPDATE
            open       = VALUES(open),
            high       = VALUES(high),
            low        = VALUES(low),
            close      = VALUES(close),
            volume     = VALUES(volume)
        """
    )

    await db.execute(upsert_sql, rows)
    await db.commit()
    logger.info("Upserted %d %s %s candles", len(rows), symbol, timeframe)
    return len(rows)


async def fetch_and_store_all_timeframes(
    db: AsyncSession,
    symbol: str = "BTC",
    lookback_bars: int = 500,
) -> dict[str, int]:
    """Fetch and store OHLCV for all supported timeframes.

    Returns:
        Dict mapping timeframe -> rows upserted.
    """
    results: dict[str, int] = {}
    for tf in TIMEFRAMES:
        try:
            count = await fetch_and_store_ohlcv(db, symbol, tf, lookback_bars)
            results[tf] = count
        except Exception as exc:
            logger.error("Failed to fetch %s %s: %s", symbol, tf, exc)
            results[tf] = 0
    return results


async def fetch_and_store_funding_rates(
    db: AsyncSession,
    symbol: str = "BTC",
    lookback_hours: int = 48,
) -> int:
    """Fetch funding rate history from Hyperliquid and upsert into funding_rates.

    Returns:
        Number of rows upserted.
    """
    info = _get_info_client()
    end_time = int(datetime.utcnow().timestamp() * 1000)
    start_time = end_time - lookback_hours * 3600 * 1000

    logger.info("Fetching funding rates for %s (%dh lookback)", symbol, lookback_hours)
    history = info.funding_history(symbol, start_time, end_time)

    if not history:
        logger.warning("No funding rate data returned for %s", symbol)
        return 0

    rows = []
    for entry in history:
        ts = datetime.utcfromtimestamp(entry["time"] / 1000)
        rows.append(
            {
                "symbol": symbol,
                "timestamp": ts,
                "rate": float(entry["fundingRate"]),
                "created_at": datetime.utcnow(),
            }
        )

    upsert_sql = text(
        """
        INSERT INTO funding_rates (symbol, timestamp, rate, created_at)
        VALUES (:symbol, :timestamp, :rate, :created_at)
        ON DUPLICATE KEY UPDATE
            rate = VALUES(rate)
        """
    )

    await db.execute(upsert_sql, rows)
    await db.commit()
    logger.info("Upserted %d funding rate records for %s", len(rows), symbol)
    return len(rows)


async def fetch_and_store_hlp_data(db: AsyncSession) -> int:
    """Fetch HLP (Hyperliquidity Provider) state and store as JSON snapshot.

    Returns:
        1 if stored, 0 if skipped.
    """
    info = _get_info_client()

    logger.info("Fetching HLP data")
    try:
        # HLP state available via clearinghouseState for the HLP vault address
        # Using meta + assetCtxs as a proxy for HLP market maker info
        meta = info.meta()
        hlp_snapshot = {
            "universe": meta.get("universe", []),
        }
    except Exception as exc:
        logger.error("Failed to fetch HLP data: %s", exc)
        return 0

    now = datetime.utcnow()
    upsert_sql = text(
        """
        INSERT INTO hlp_data (timestamp, data, created_at)
        VALUES (:timestamp, :data, :created_at)
        ON DUPLICATE KEY UPDATE
            data = VALUES(data)
        """
    )

    import json

    await db.execute(
        upsert_sql,
        {"timestamp": now, "data": json.dumps(hlp_snapshot), "created_at": now},
    )
    await db.commit()
    logger.info("Stored HLP snapshot at %s", now)
    return 1
