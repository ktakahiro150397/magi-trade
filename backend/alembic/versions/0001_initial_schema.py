"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # market_data
    op.create_table(
        "market_data",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("timeframe", sa.String(length=10), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("open", sa.Float(precision=53), nullable=False),
        sa.Column("high", sa.Float(precision=53), nullable=False),
        sa.Column("low", sa.Float(precision=53), nullable=False),
        sa.Column("close", sa.Float(precision=53), nullable=False),
        sa.Column("volume", sa.Float(precision=53), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_market_data_symbol_timeframe_timestamp",
        "market_data",
        ["symbol", "timeframe", "timestamp"],
        unique=True,
    )
    op.create_index("ix_market_data_timestamp", "market_data", ["timestamp"])

    # funding_rates
    op.create_table(
        "funding_rates",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("rate", sa.Float(precision=53), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_funding_rates_symbol_timestamp",
        "funding_rates",
        ["symbol", "timestamp"],
        unique=True,
    )
    op.create_index("ix_funding_rates_timestamp", "funding_rates", ["timestamp"])

    # hlp_data
    op.create_table(
        "hlp_data",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hlp_data_timestamp", "hlp_data", ["timestamp"], unique=True)

    # technical_indicators
    op.create_table(
        "technical_indicators",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("timeframe", sa.String(length=10), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("rsi", sa.Float(precision=53), nullable=True),
        sa.Column("ema_9", sa.Float(precision=53), nullable=True),
        sa.Column("ema_21", sa.Float(precision=53), nullable=True),
        sa.Column("ema_50", sa.Float(precision=53), nullable=True),
        sa.Column("atr", sa.Float(precision=53), nullable=True),
        sa.Column("macd", sa.Float(precision=53), nullable=True),
        sa.Column("macd_signal", sa.Float(precision=53), nullable=True),
        sa.Column("macd_hist", sa.Float(precision=53), nullable=True),
        sa.Column("bb_upper", sa.Float(precision=53), nullable=True),
        sa.Column("bb_middle", sa.Float(precision=53), nullable=True),
        sa.Column("bb_lower", sa.Float(precision=53), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_technical_indicators_symbol_tf_ts",
        "technical_indicators",
        ["symbol", "timeframe", "timestamp"],
        unique=True,
    )

    # agent_sessions
    op.create_table(
        "agent_sessions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("market_snapshot", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # agent_opinions
    op.create_table(
        "agent_opinions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("agent_name", sa.String(length=50), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.Float(precision=53), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("raw_response", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["agent_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # final_decisions
    op.create_table(
        "final_decisions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.Float(precision=53), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("raw_response", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["agent_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )

    # trades
    op.create_table(
        "trades",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.BigInteger(), nullable=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("size", sa.Float(precision=53), nullable=False),
        sa.Column("entry_price", sa.Float(precision=53), nullable=False),
        sa.Column("exit_price", sa.Float(precision=53), nullable=True),
        sa.Column("stop_loss", sa.Float(precision=53), nullable=True),
        sa.Column("take_profit", sa.Float(precision=53), nullable=True),
        sa.Column("pnl", sa.Float(precision=53), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["agent_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # trade_settings
    op.create_table(
        "trade_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("risk_percent", sa.Float(precision=53), nullable=False),
        sa.Column("leverage", sa.Integer(), nullable=False),
        sa.Column("max_hold_hours", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("trade_settings")
    op.drop_table("trades")
    op.drop_table("final_decisions")
    op.drop_table("agent_opinions")
    op.drop_table("agent_sessions")
    op.drop_index("ix_technical_indicators_symbol_tf_ts", table_name="technical_indicators")
    op.drop_table("technical_indicators")
    op.drop_index("ix_hlp_data_timestamp", table_name="hlp_data")
    op.drop_table("hlp_data")
    op.drop_index("ix_funding_rates_symbol_timestamp", table_name="funding_rates")
    op.drop_index("ix_funding_rates_timestamp", table_name="funding_rates")
    op.drop_table("funding_rates")
    op.drop_index("ix_market_data_symbol_timeframe_timestamp", table_name="market_data")
    op.drop_index("ix_market_data_timestamp", table_name="market_data")
    op.drop_table("market_data")
