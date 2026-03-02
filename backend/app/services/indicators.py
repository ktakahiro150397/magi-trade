"""Technical indicator calculation module.

Reads OHLCV data from DB, calculates RSI / EMA / ATR / MACD / Bollinger Bands
using pandas-ta, saves results to technical_indicators table, and generates
the JSON payload consumed by AI agents.
"""

import json
import logging
from datetime import datetime

import pandas as pd
import pandas_ta as ta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Number of recent bars to load for indicator calculation
_CALC_WINDOW = 300


async def _load_ohlcv(
    db: AsyncSession, symbol: str, timeframe: str, limit: int = _CALC_WINDOW
) -> pd.DataFrame:
    """Load recent OHLCV data from DB into a DataFrame."""
    result = await db.execute(
        text(
            """
            SELECT timestamp, open, high, low, close, volume
            FROM market_data
            WHERE symbol = :symbol AND timeframe = :timeframe
            ORDER BY timestamp DESC
            LIMIT :limit
            """
        ),
        {"symbol": symbol, "timeframe": timeframe, "limit": limit},
    )
    rows = result.fetchall()
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df


def _calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add RSI, EMA, ATR, MACD, and Bollinger Bands columns to a DataFrame."""
    if df.empty or len(df) < 26:
        return df

    # RSI (14)
    df["rsi"] = ta.rsi(df["close"], length=14)

    # EMA
    df["ema_9"] = ta.ema(df["close"], length=9)
    df["ema_21"] = ta.ema(df["close"], length=21)
    df["ema_50"] = ta.ema(df["close"], length=50)

    # ATR (14)
    atr = ta.atr(df["high"], df["low"], df["close"], length=14)
    df["atr"] = atr

    # MACD (12, 26, 9)
    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    if macd is not None and not macd.empty:
        df["macd"] = macd.iloc[:, 0]
        df["macd_signal"] = macd.iloc[:, 1]
        df["macd_hist"] = macd.iloc[:, 2]

    # Bollinger Bands (20, 2)
    bb = ta.bbands(df["close"], length=20, std=2)
    if bb is not None and not bb.empty:
        df["bb_upper"] = bb.iloc[:, 0]
        df["bb_middle"] = bb.iloc[:, 1]
        df["bb_lower"] = bb.iloc[:, 2]

    return df


async def calculate_and_store_indicators(
    db: AsyncSession, symbol: str, timeframe: str
) -> int:
    """Calculate indicators for the latest bars and upsert into technical_indicators.

    Returns:
        Number of rows upserted.
    """
    df = await _load_ohlcv(db, symbol, timeframe)
    if df.empty:
        logger.warning("No OHLCV data found for %s %s", symbol, timeframe)
        return 0

    df = _calculate_indicators(df)

    indicator_cols = [
        "rsi", "ema_9", "ema_21", "ema_50",
        "atr", "macd", "macd_signal", "macd_hist",
        "bb_upper", "bb_middle", "bb_lower",
    ]
    # Only store rows that have at least one indicator calculated
    df_valid = df.dropna(subset=["rsi"], how="all")
    if df_valid.empty:
        return 0

    rows = []
    now = datetime.utcnow()
    for _, row in df_valid.iterrows():
        r: dict = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": row["timestamp"].to_pydatetime(),
            "created_at": now,
        }
        for col in indicator_cols:
            val = row.get(col)
            r[col] = None if (val is None or pd.isna(val)) else float(val)
        rows.append(r)

    upsert_sql = text(
        """
        INSERT INTO technical_indicators
            (symbol, timeframe, timestamp,
             rsi, ema_9, ema_21, ema_50,
             atr, macd, macd_signal, macd_hist,
             bb_upper, bb_middle, bb_lower, created_at)
        VALUES
            (:symbol, :timeframe, :timestamp,
             :rsi, :ema_9, :ema_21, :ema_50,
             :atr, :macd, :macd_signal, :macd_hist,
             :bb_upper, :bb_middle, :bb_lower, :created_at)
        ON DUPLICATE KEY UPDATE
            rsi         = VALUES(rsi),
            ema_9       = VALUES(ema_9),
            ema_21      = VALUES(ema_21),
            ema_50      = VALUES(ema_50),
            atr         = VALUES(atr),
            macd        = VALUES(macd),
            macd_signal = VALUES(macd_signal),
            macd_hist   = VALUES(macd_hist),
            bb_upper    = VALUES(bb_upper),
            bb_middle   = VALUES(bb_middle),
            bb_lower    = VALUES(bb_lower)
        """
    )

    await db.execute(upsert_sql, rows)
    await db.commit()
    logger.info("Upserted %d indicator rows for %s %s", len(rows), symbol, timeframe)
    return len(rows)


async def generate_ai_payload(
    db: AsyncSession,
    symbol: str = "BTC",
    primary_timeframe: str = "15m",
    n_bars: int = 50,
) -> dict:
    """Generate the JSON payload that will be passed to AI agents.

    The payload includes recent OHLCV bars, calculated indicators for multiple
    timeframes, and the latest funding rate.

    Args:
        db: Async SQLAlchemy session.
        symbol: Trading symbol.
        primary_timeframe: The main timeframe for analysis.
        n_bars: Number of recent bars to include in the payload.

    Returns:
        Dict ready to be serialised as JSON.
    """
    # ---- Recent OHLCV ----
    df_ohlcv = await _load_ohlcv(db, symbol, primary_timeframe, limit=n_bars)
    ohlcv_records: list[dict] = []
    if not df_ohlcv.empty:
        df_ohlcv = _calculate_indicators(df_ohlcv)
        for _, row in df_ohlcv.iterrows():
            ohlcv_records.append(
                {
                    "timestamp": row["timestamp"].isoformat(),
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                }
            )

    # ---- Latest indicators per timeframe ----
    indicators_by_tf: dict[str, dict] = {}
    for tf in ["1h", "15m", "1m"]:
        result = await db.execute(
            text(
                """
                SELECT rsi, ema_9, ema_21, ema_50, atr,
                       macd, macd_signal, macd_hist,
                       bb_upper, bb_middle, bb_lower
                FROM technical_indicators
                WHERE symbol = :symbol AND timeframe = :tf
                ORDER BY timestamp DESC
                LIMIT 1
                """
            ),
            {"symbol": symbol, "tf": tf},
        )
        row = result.fetchone()
        if row:
            indicators_by_tf[tf] = {
                "rsi": row[0],
                "ema_9": row[1],
                "ema_21": row[2],
                "ema_50": row[3],
                "atr": row[4],
                "macd": row[5],
                "macd_signal": row[6],
                "macd_hist": row[7],
                "bb_upper": row[8],
                "bb_middle": row[9],
                "bb_lower": row[10],
            }

    # ---- Latest funding rate ----
    fr_result = await db.execute(
        text(
            """
            SELECT rate, timestamp
            FROM funding_rates
            WHERE symbol = :symbol
            ORDER BY timestamp DESC
            LIMIT 1
            """
        ),
        {"symbol": symbol},
    )
    fr_row = fr_result.fetchone()
    funding_rate = {"rate": fr_row[0], "timestamp": fr_row[1].isoformat()} if fr_row else None

    # ---- Current price ----
    current_price: float | None = None
    if ohlcv_records:
        current_price = ohlcv_records[-1]["close"]

    payload = {
        "symbol": symbol,
        "generated_at": datetime.utcnow().isoformat(),
        "current_price": current_price,
        "primary_timeframe": primary_timeframe,
        "ohlcv": ohlcv_records,
        "indicators": indicators_by_tf,
        "funding_rate": funding_rate,
    }

    return payload
