"""Agent runner functions.

Each function calls the LLM with the appropriate prompt template and parses
the structured JSON response into a typed dataclass.
"""

import logging

from app.services.agents.prompts import (
    contrarian_agent_prompts,
    master_agent_prompts,
    risk_agent_prompts,
    trend_agent_prompts,
)
from app.services.agents.state import AgentOpinionData, MasterDecisionData
from app.services.llm.base import LLMClient

logger = logging.getLogger(__name__)

_VALID_ACTIONS = {"LONG", "SHORT", "HOLD", "CLOSE"}


def _validate_action(action: str, agent_name: str) -> str:
    """Normalise and validate the action string."""
    normalised = action.strip().upper()
    if normalised not in _VALID_ACTIONS:
        logger.warning("[%s] Unexpected action %r, defaulting to HOLD", agent_name, action)
        normalised = "HOLD"
    return normalised


async def run_trend_agent(market_data: dict, client: LLMClient) -> AgentOpinionData:
    """Run the Trend Agent and return its opinion."""
    system, user = trend_agent_prompts(market_data)
    logger.info("[trend_agent] Calling LLM backend: %s", client.name)
    raw_text = await client.complete(system, user)

    try:
        parsed = LLMClient.extract_json(raw_text)
    except ValueError as exc:
        logger.error("[trend_agent] JSON parse error: %s | raw=%s", exc, raw_text[:300])
        parsed = {"action": "HOLD", "confidence": 0.5, "reasoning": "JSON解析エラー"}

    return AgentOpinionData(
        agent_name="trend",
        action=_validate_action(parsed.get("action", "HOLD"), "trend"),
        confidence=float(parsed.get("confidence", 0.5)),
        reasoning=str(parsed.get("reasoning", "")),
        raw_response=parsed,
    )


async def run_contrarian_agent(market_data: dict, client: LLMClient) -> AgentOpinionData:
    """Run the Contrarian Agent and return its opinion."""
    system, user = contrarian_agent_prompts(market_data)
    logger.info("[contrarian_agent] Calling LLM backend: %s", client.name)
    raw_text = await client.complete(system, user)

    try:
        parsed = LLMClient.extract_json(raw_text)
    except ValueError as exc:
        logger.error("[contrarian_agent] JSON parse error: %s | raw=%s", exc, raw_text[:300])
        parsed = {"action": "HOLD", "confidence": 0.5, "reasoning": "JSON解析エラー"}

    return AgentOpinionData(
        agent_name="contrarian",
        action=_validate_action(parsed.get("action", "HOLD"), "contrarian"),
        confidence=float(parsed.get("confidence", 0.5)),
        reasoning=str(parsed.get("reasoning", "")),
        raw_response=parsed,
    )


async def run_risk_agent(market_data: dict, client: LLMClient) -> AgentOpinionData:
    """Run the Risk Agent and return its opinion."""
    system, user = risk_agent_prompts(market_data)
    logger.info("[risk_agent] Calling LLM backend: %s", client.name)
    raw_text = await client.complete(system, user)

    try:
        parsed = LLMClient.extract_json(raw_text)
    except ValueError as exc:
        logger.error("[risk_agent] JSON parse error: %s | raw=%s", exc, raw_text[:300])
        parsed = {"action": "HOLD", "confidence": 0.5, "reasoning": "JSON解析エラー"}

    return AgentOpinionData(
        agent_name="risk",
        action=_validate_action(parsed.get("action", "HOLD"), "risk"),
        confidence=float(parsed.get("confidence", 0.5)),
        reasoning=str(parsed.get("reasoning", "")),
        raw_response=parsed,
    )


async def run_master_agent(
    market_data: dict,
    trend_opinion: AgentOpinionData,
    contrarian_opinion: AgentOpinionData,
    risk_opinion: AgentOpinionData,
    client: LLMClient,
) -> MasterDecisionData:
    """Run the Master Agent and return the final decision."""
    system, user = master_agent_prompts(
        market_data=market_data,
        trend_opinion={
            "action": trend_opinion.action,
            "confidence": trend_opinion.confidence,
            "reasoning": trend_opinion.reasoning,
        },
        contrarian_opinion={
            "action": contrarian_opinion.action,
            "confidence": contrarian_opinion.confidence,
            "reasoning": contrarian_opinion.reasoning,
        },
        risk_opinion={
            "action": risk_opinion.action,
            "confidence": risk_opinion.confidence,
            "reasoning": risk_opinion.reasoning,
        },
    )

    logger.info("[master_agent] Calling LLM backend: %s", client.name)
    raw_text = await client.complete(system, user)

    try:
        parsed = LLMClient.extract_json(raw_text)
    except ValueError as exc:
        logger.error("[master_agent] JSON parse error: %s | raw=%s", exc, raw_text[:300])
        parsed = {
            "action": "HOLD",
            "confidence": 0.5,
            "reasoning": "JSON解析エラー",
            "sl_price": None,
            "tp_price": None,
            "size_ratio": None,
        }

    return MasterDecisionData(
        action=_validate_action(parsed.get("action", "HOLD"), "master"),
        confidence=float(parsed.get("confidence", 0.5)),
        reasoning=str(parsed.get("reasoning", "")),
        sl_price=parsed.get("sl_price"),
        tp_price=parsed.get("tp_price"),
        size_ratio=parsed.get("size_ratio"),
        raw_response=parsed,
    )
