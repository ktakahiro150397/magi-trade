"""Trading models: agent sessions, opinions, decisions, trades, settings."""

from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AgentSession(Base):
    """One round of AI deliberation triggered per 15m bar close."""

    __tablename__ = "agent_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    market_snapshot: Mapped[dict] = mapped_column(
        JSON, nullable=False, comment="AI に渡した市場データのスナップショット"
    )

    opinions: Mapped[list["AgentOpinion"]] = relationship(
        "AgentOpinion", back_populates="session", cascade="all, delete-orphan"
    )
    final_decision: Mapped["FinalDecision | None"] = relationship(
        "FinalDecision", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="session")

    def __repr__(self) -> str:
        return f"<AgentSession id={self.id} created_at={self.created_at}>"


class AgentOpinion(Base):
    """Opinion from a single AI agent within a session."""

    __tablename__ = "agent_opinions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False
    )
    agent_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="trend / contrarian / risk"
    )
    action: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="LONG / SHORT / HOLD / CLOSE"
    )
    confidence: Mapped[float] = mapped_column(
        Float(precision=53), nullable=False, comment="0.0 - 1.0"
    )
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    raw_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    session: Mapped["AgentSession"] = relationship("AgentSession", back_populates="opinions")

    def __repr__(self) -> str:
        return f"<AgentOpinion session={self.session_id} agent={self.agent_name} action={self.action}>"


class FinalDecision(Base):
    """Master agent's aggregated final trading decision."""

    __tablename__ = "final_decisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    action: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="LONG / SHORT / HOLD / CLOSE"
    )
    confidence: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    raw_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    session: Mapped["AgentSession"] = relationship(
        "AgentSession", back_populates="final_decision"
    )

    def __repr__(self) -> str:
        return f"<FinalDecision session={self.session_id} action={self.action}>"


class Trade(Base):
    """Individual trade records."""

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("agent_sessions.id", ondelete="SET NULL"), nullable=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False, comment="LONG / SHORT")
    size: Mapped[float] = mapped_column(Float(precision=53), nullable=False, comment="コントラクト数")
    entry_price: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    exit_price: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    stop_loss: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    take_profit: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    pnl: Mapped[float | None] = mapped_column(
        Float(precision=53), nullable=True, comment="実現損益 (USD)"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="OPEN", comment="OPEN / CLOSED / CANCELLED"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    session: Mapped["AgentSession | None"] = relationship("AgentSession", back_populates="trades")

    def __repr__(self) -> str:
        return f"<Trade id={self.id} {self.symbol} {self.side} status={self.status}>"


class TradeSetting(Base):
    """Runtime trading configuration (single-row table)."""

    __tablename__ = "trade_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    risk_percent: Mapped[float] = mapped_column(
        Float(precision=53), nullable=False, default=1.0, comment="口座残高に対するリスク率 (%)"
    )
    leverage: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    max_hold_hours: Mapped[int] = mapped_column(
        Integer, nullable=False, default=24, comment="最大ホールド時間"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<TradeSetting risk={self.risk_percent}% leverage={self.leverage}x>"
