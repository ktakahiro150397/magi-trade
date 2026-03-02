"""Unit tests for the multi-agent trading system.

All tests use MockLLMClient and an in-memory SQLite DB — no real LLM calls
and no external MySQL are required.
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agents.agent_runner import (
    run_contrarian_agent,
    run_master_agent,
    run_risk_agent,
    run_trend_agent,
)
from app.services.agents.state import AgentOpinionData, MasterDecisionData
from app.services.llm.mock import MockLLMClient

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SAMPLE_MARKET_DATA = {
    "symbol": "BTC",
    "generated_at": datetime.utcnow().isoformat(),
    "current_price": 50000.0,
    "primary_timeframe": "15m",
    "ohlcv": [
        {
            "timestamp": "2024-01-01T00:00:00",
            "open": 49900.0,
            "high": 50100.0,
            "low": 49800.0,
            "close": 50000.0,
            "volume": 1200.0,
        }
    ],
    "indicators": {
        "15m": {
            "rsi": 55.0,
            "ema_9": 49950.0,
            "ema_21": 49800.0,
            "ema_50": 49500.0,
            "atr": 250.0,
            "macd": 50.0,
            "macd_signal": 42.0,
            "macd_hist": 8.0,
            "bb_upper": 50500.0,
            "bb_middle": 50000.0,
            "bb_lower": 49500.0,
        }
    },
    "funding_rate": {"rate": 0.0010, "timestamp": "2024-01-01T00:00:00"},
}


def _mock_client(action: str = "HOLD", confidence: float = 0.65) -> MockLLMClient:
    """Return a MockLLMClient whose default response has the given action."""
    response = json.dumps(
        {
            "action": action,
            "confidence": confidence,
            "reasoning": f"テスト用: {action} を推奨",
        }
    )
    master_response = json.dumps(
        {
            "action": action,
            "confidence": confidence,
            "reasoning": f"マスター判断: {action}",
            "sl_price": None,
            "tp_price": None,
            "size_ratio": None,
        }
    )
    return MockLLMClient(responses={"default": response, "master": master_response})


# ---------------------------------------------------------------------------
# Individual agent tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestTrendAgent:
    async def test_returns_opinion_dataclass(self):
        client = _mock_client("LONG", 0.8)
        opinion = await run_trend_agent(SAMPLE_MARKET_DATA, client)
        assert isinstance(opinion, AgentOpinionData)
        assert opinion.agent_name == "trend"
        assert opinion.action == "LONG"
        assert opinion.confidence == 0.8

    async def test_invalid_action_defaults_to_hold(self):
        bad_json = json.dumps(
            {"action": "INVALID_ACTION", "confidence": 0.5, "reasoning": "bad"}
        )
        client = MockLLMClient(fixed_response=bad_json)
        opinion = await run_trend_agent(SAMPLE_MARKET_DATA, client)
        assert opinion.action == "HOLD"

    async def test_unparseable_response_defaults_to_hold(self):
        client = MockLLMClient(fixed_response="This is not JSON at all.")
        opinion = await run_trend_agent(SAMPLE_MARKET_DATA, client)
        assert opinion.action == "HOLD"
        assert opinion.confidence == 0.5

    async def test_all_valid_actions(self):
        for action in ("LONG", "SHORT", "HOLD", "CLOSE"):
            client = _mock_client(action)
            opinion = await run_trend_agent(SAMPLE_MARKET_DATA, client)
            assert opinion.action == action


@pytest.mark.asyncio
class TestContrarianAgent:
    async def test_returns_contrarian_opinion(self):
        client = _mock_client("SHORT", 0.72)
        opinion = await run_contrarian_agent(SAMPLE_MARKET_DATA, client)
        assert opinion.agent_name == "contrarian"
        assert opinion.action == "SHORT"
        assert abs(opinion.confidence - 0.72) < 1e-9

    async def test_raw_response_stored(self):
        client = _mock_client("HOLD")
        opinion = await run_contrarian_agent(SAMPLE_MARKET_DATA, client)
        assert isinstance(opinion.raw_response, dict)
        assert "action" in opinion.raw_response


@pytest.mark.asyncio
class TestRiskAgent:
    async def test_returns_risk_opinion(self):
        client = _mock_client("HOLD", 0.9)
        opinion = await run_risk_agent(SAMPLE_MARKET_DATA, client)
        assert opinion.agent_name == "risk"
        assert opinion.action == "HOLD"


@pytest.mark.asyncio
class TestMasterAgent:
    async def _make_opinions(self, action: str = "HOLD") -> tuple:
        trend = AgentOpinionData("trend", action, 0.65, "trend reasoning")
        contrarian = AgentOpinionData("contrarian", action, 0.60, "contrarian reasoning")
        risk = AgentOpinionData("risk", action, 0.70, "risk reasoning")
        return trend, contrarian, risk

    async def test_returns_master_decision(self):
        client = _mock_client("HOLD", 0.70)
        trend, contrarian, risk = await self._make_opinions("HOLD")
        decision = await run_master_agent(
            SAMPLE_MARKET_DATA, trend, contrarian, risk, client
        )
        assert isinstance(decision, MasterDecisionData)
        assert decision.action == "HOLD"
        assert decision.confidence == 0.70

    async def test_sl_tp_none_for_hold(self):
        client = _mock_client("HOLD")
        trend, contrarian, risk = await self._make_opinions("HOLD")
        decision = await run_master_agent(
            SAMPLE_MARKET_DATA, trend, contrarian, risk, client
        )
        assert decision.sl_price is None
        assert decision.tp_price is None
        assert decision.size_ratio is None

    async def test_unparseable_master_response_defaults(self):
        client = MockLLMClient(fixed_response="no json here")
        trend, contrarian, risk = await self._make_opinions()
        decision = await run_master_agent(
            SAMPLE_MARKET_DATA, trend, contrarian, risk, client
        )
        assert decision.action == "HOLD"


# ---------------------------------------------------------------------------
# Full graph workflow (DB mocked)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestRunAgentSession:
    async def test_full_workflow_with_mock_db(self):
        """Run the full LangGraph workflow with a mocked DB session."""
        from app.services.agents.graph import run_agent_session

        client = _mock_client("HOLD", 0.70)

        # Build a mock DB session that accepts all calls
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.commit = AsyncMock()

        # Mock the AgentSession to return an object with id=1
        mock_session_obj = MagicMock()
        mock_session_obj.id = 1

        with patch("app.services.agents.graph.AgentSession", return_value=mock_session_obj):
            with patch("app.services.agents.graph.AgentOpinion") as mock_opinion_cls:
                with patch("app.services.agents.graph.FinalDecision") as mock_decision_cls:
                    state = await run_agent_session(
                        market_data=SAMPLE_MARKET_DATA,
                        client=client,
                        db=mock_db,
                    )

        # Verify state has expected keys
        assert state.get("final_decision") is not None
        assert state["final_decision"].action in ("LONG", "SHORT", "HOLD", "CLOSE")
        assert state.get("trend_opinion") is not None
        assert state.get("contrarian_opinion") is not None
        assert state.get("risk_opinion") is not None

        # DB operations were called
        mock_db.flush.assert_awaited_once()
        mock_db.commit.assert_awaited_once()

    async def test_session_id_set_after_save(self):
        """session_id in state should be set to the DB session's id."""
        from app.services.agents.graph import run_agent_session

        client = _mock_client()

        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.commit = AsyncMock()

        mock_session_obj = MagicMock()
        mock_session_obj.id = 42

        with patch("app.services.agents.graph.AgentSession", return_value=mock_session_obj):
            with patch("app.services.agents.graph.AgentOpinion"):
                with patch("app.services.agents.graph.FinalDecision"):
                    state = await run_agent_session(
                        market_data=SAMPLE_MARKET_DATA,
                        client=client,
                        db=mock_db,
                    )

        assert state.get("session_id") == 42


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------


class TestPrompts:
    def test_trend_prompt_contains_market_data(self):
        from app.services.agents.prompts import trend_agent_prompts

        system, user = trend_agent_prompts(SAMPLE_MARKET_DATA)
        assert "トレンドフォロー" in system
        assert "BTC" in user
        assert "50000" in user

    def test_contrarian_prompt_contains_rsi(self):
        from app.services.agents.prompts import contrarian_agent_prompts

        system, user = contrarian_agent_prompts(SAMPLE_MARKET_DATA)
        assert "逆張り" in system
        assert "RSI" in system

    def test_risk_prompt_contains_atr(self):
        from app.services.agents.prompts import risk_agent_prompts

        system, user = risk_agent_prompts(SAMPLE_MARKET_DATA)
        assert "ATR" in system

    def test_master_prompt_includes_all_opinions(self):
        from app.services.agents.prompts import master_agent_prompts

        system, user = master_agent_prompts(
            market_data=SAMPLE_MARKET_DATA,
            trend_opinion={"action": "LONG", "confidence": 0.8, "reasoning": "up"},
            contrarian_opinion={"action": "SHORT", "confidence": 0.6, "reasoning": "down"},
            risk_opinion={"action": "HOLD", "confidence": 0.7, "reasoning": "risky"},
        )
        assert "マスター" in system
        assert "LONG" in user
        assert "SHORT" in user
        assert "HOLD" in user
