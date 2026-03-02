"""Shared state types for the multi-agent trading workflow.

TradingState is the LangGraph state object passed between nodes.
AgentOpinionData is the structured output from each sub-agent.
"""

from dataclasses import dataclass, field
from typing import TypedDict


@dataclass
class AgentOpinionData:
    """Parsed output from a single AI agent."""

    agent_name: str
    action: str  # LONG | SHORT | HOLD | CLOSE
    confidence: float  # 0.0 – 1.0
    reasoning: str
    raw_response: dict = field(default_factory=dict)


@dataclass
class MasterDecisionData:
    """Parsed output from the Master Agent."""

    action: str  # LONG | SHORT | HOLD | CLOSE
    confidence: float
    reasoning: str
    sl_price: float | None = None
    tp_price: float | None = None
    size_ratio: float | None = None
    raw_response: dict = field(default_factory=dict)


class TradingState(TypedDict, total=False):
    """LangGraph state shared across all nodes in the trading workflow."""

    market_data: dict  # payload from generate_ai_payload()
    position: dict | None  # current open position (or None)

    # Sub-agent opinions (populated after sub_agents node)
    trend_opinion: AgentOpinionData | None
    contrarian_opinion: AgentOpinionData | None
    risk_opinion: AgentOpinionData | None

    # Master agent decision (populated after master node)
    final_decision: MasterDecisionData | None

    # DB session id (populated after save node)
    session_id: int | None
