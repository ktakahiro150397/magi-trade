"""Unit tests for the data collector module (mock-based)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_fetch_and_store_ohlcv_unsupported_timeframe():
    from app.services.data_collector import fetch_and_store_ohlcv

    db = AsyncMock()
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        await fetch_and_store_ohlcv(db, "BTC", "5m")


@pytest.mark.asyncio
async def test_fetch_and_store_ohlcv_empty_response():
    from app.services.data_collector import fetch_and_store_ohlcv

    db = AsyncMock()
    mock_info = MagicMock()
    mock_info.candles_snapshot.return_value = []

    with patch("app.services.data_collector._get_info_client", return_value=mock_info):
        result = await fetch_and_store_ohlcv(db, "BTC", "15m")

    assert result == 0


@pytest.mark.asyncio
async def test_fetch_and_store_ohlcv_success():
    from app.services.data_collector import fetch_and_store_ohlcv

    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()

    fake_candles = [
        {
            "t": int(datetime(2024, 1, 1, 0, i * 15).timestamp() * 1000),
            "o": "50000",
            "h": "50500",
            "l": "49800",
            "c": "50200",
            "v": "100",
        }
        for i in range(3)
    ]

    mock_info = MagicMock()
    mock_info.candles_snapshot.return_value = fake_candles

    with patch("app.services.data_collector._get_info_client", return_value=mock_info):
        result = await fetch_and_store_ohlcv(db, "BTC", "15m", lookback_bars=3)

    assert result == 3
    db.commit.assert_awaited_once()
