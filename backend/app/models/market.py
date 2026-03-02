"""Market data models: OHLCV, Funding Rates, HLP data."""

from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MarketData(Base):
    """OHLCV candlestick data for multiple timeframes."""

    __tablename__ = "market_data"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, comment="例: BTC")
    timeframe: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="1m / 15m / 30m / 1h"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="足の開始時刻 (UTC)"
    )
    open: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    high: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    low: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    close: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    volume: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_market_data_symbol_timeframe_timestamp", "symbol", "timeframe", "timestamp", unique=True),
        Index("ix_market_data_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<MarketData {self.symbol} {self.timeframe} {self.timestamp}>"


class FundingRate(Base):
    """Funding rate history."""

    __tablename__ = "funding_rates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Funding Rate 確定時刻 (UTC)"
    )
    rate: Mapped[float] = mapped_column(Float(precision=53), nullable=False, comment="Funding Rate")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_funding_rates_symbol_timestamp", "symbol", "timestamp", unique=True),
        Index("ix_funding_rates_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<FundingRate {self.symbol} {self.timestamp} rate={self.rate}>"


class HlpData(Base):
    """Hyperliquidity Provider (HLP) data."""

    __tablename__ = "hlp_data"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="データ取得時刻 (UTC)"
    )
    data: Mapped[dict] = mapped_column(JSON, nullable=False, comment="HLP 生データ (JSON)")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (Index("ix_hlp_data_timestamp", "timestamp", unique=True),)

    def __repr__(self) -> str:
        return f"<HlpData {self.timestamp}>"


class TechnicalIndicator(Base):
    """Calculated technical indicators per symbol/timeframe."""

    __tablename__ = "technical_indicators"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # RSI
    rsi: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    # EMA
    ema_9: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    ema_21: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    ema_50: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    # ATR
    atr: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    # MACD
    macd: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    macd_signal: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    macd_hist: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    # Bollinger Bands
    bb_upper: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    bb_middle: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    bb_lower: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index(
            "ix_technical_indicators_symbol_tf_ts",
            "symbol",
            "timeframe",
            "timestamp",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return f"<TechnicalIndicator {self.symbol} {self.timeframe} {self.timestamp}>"
