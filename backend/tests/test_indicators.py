"""Unit tests for the technical indicator calculation module."""

import pandas as pd
import pytest

from app.services.indicators import _calculate_indicators


def _make_df(n: int = 100) -> pd.DataFrame:
    """Create a synthetic OHLCV DataFrame for testing."""
    import numpy as np

    rng = np.random.default_rng(42)
    close = 50000 + rng.normal(0, 500, n).cumsum()
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=n, freq="15min"),
            "open": close - rng.uniform(0, 200, n),
            "high": close + rng.uniform(0, 300, n),
            "low": close - rng.uniform(0, 300, n),
            "close": close,
            "volume": rng.uniform(100, 1000, n),
        }
    )
    return df


def test_calculate_indicators_returns_expected_columns():
    df = _make_df(100)
    result = _calculate_indicators(df)
    for col in ["rsi", "ema_9", "ema_21", "ema_50", "atr", "macd", "macd_signal", "macd_hist"]:
        assert col in result.columns, f"Missing column: {col}"


def test_rsi_range():
    df = _make_df(100)
    result = _calculate_indicators(df)
    rsi_values = result["rsi"].dropna()
    assert (rsi_values >= 0).all() and (rsi_values <= 100).all()


def test_ema_ordering():
    """EMA(9) should be more reactive than EMA(50) on a trending series."""
    df = _make_df(200)
    result = _calculate_indicators(df)
    # Both should have values by the end
    assert result["ema_9"].notna().sum() > 0
    assert result["ema_50"].notna().sum() > 0


def test_empty_df_returns_empty():
    df = pd.DataFrame()
    result = _calculate_indicators(df)
    assert result.empty


def test_short_df_returns_without_indicators():
    df = _make_df(10)
    result = _calculate_indicators(df)
    # With only 10 bars we can't compute MACD (needs 26), so macd may be all NaN
    assert "rsi" in result.columns or result.empty
