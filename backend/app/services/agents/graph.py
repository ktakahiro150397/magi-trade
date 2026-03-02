"""LangGraph multi-agent trading workflow.

Graph structure
---------------
START
  └─▶ sub_agents   (runs trend / contrarian / risk agents in parallel)
        └─▶ master  (aggregates opinions → final decision)
              └─▶ save   (persists session, opinions, decision to DB)
                    └─▶ END

The sub_agents node uses asyncio.gather to execute the three specialist
agents concurrently, respecting the LangGraph state contract.
"""

import asyncio
import logging
from datetime import datetime
from functools import partial
from typing import Any

from langgraph.graph import END, START, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trading import AgentOpinion, AgentSession, FinalDecision
from app.services.agents.agent_runner import (
    run_contrarian_agent,
    run_master_agent,
    run_risk_agent,
    run_trend_agent,
)
from app.services.agents.state import TradingState
from app.services.llm.base import LLMClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Node functions
# ---------------------------------------------------------------------------


async def sub_agents_node(state: TradingState, client: LLMClient) -> dict[str, Any]:
    """Run the three specialist agents in parallel and update state."""
    market_data = state["market_data"]

    trend_op, contrarian_op, risk_op = await asyncio.gather(
        run_trend_agent(market_data, client),
        run_contrarian_agent(market_data, client),
        run_risk_agent(market_data, client),
    )

    logger.info(
        "Sub-agents: trend=%s(%.2f) contrarian=%s(%.2f) risk=%s(%.2f)",
        trend_op.action, trend_op.confidence,
        contrarian_op.action, contrarian_op.confidence,
        risk_op.action, risk_op.confidence,
    )

    return {
        "trend_opinion": trend_op,
        "contrarian_opinion": contrarian_op,
        "risk_opinion": risk_op,
    }


async def master_node(state: TradingState, client: LLMClient) -> dict[str, Any]:
    """Run the master agent to produce the final decision."""
    decision = await run_master_agent(
        market_data=state["market_data"],
        trend_opinion=state["trend_opinion"],
        contrarian_opinion=state["contrarian_opinion"],
        risk_opinion=state["risk_opinion"],
        client=client,
    )

    logger.info(
        "Master decision: action=%s confidence=%.2f",
        decision.action,
        decision.confidence,
    )

    return {"final_decision": decision}


async def save_node(state: TradingState, db: AsyncSession) -> dict[str, Any]:
    """Persist the agent session, individual opinions, and final decision to DB."""
    now = datetime.utcnow()

    # 1. Create agent session
    session = AgentSession(
        created_at=now,
        market_snapshot=state["market_data"],
    )
    db.add(session)
    await db.flush()  # get session.id before inserting children

    # 2. Save individual opinions
    for opinion in [
        state.get("trend_opinion"),
        state.get("contrarian_opinion"),
        state.get("risk_opinion"),
    ]:
        if opinion is None:
            continue
        db.add(
            AgentOpinion(
                session_id=session.id,
                agent_name=opinion.agent_name,
                action=opinion.action,
                confidence=opinion.confidence,
                reasoning=opinion.reasoning,
                raw_response=opinion.raw_response,
                created_at=now,
            )
        )

    # 3. Save final decision
    decision = state.get("final_decision")
    if decision:
        db.add(
            FinalDecision(
                session_id=session.id,
                action=decision.action,
                confidence=decision.confidence,
                reasoning=decision.reasoning,
                raw_response=decision.raw_response,
                created_at=now,
            )
        )

    await db.commit()
    logger.info("Saved agent session id=%d to DB", session.id)

    return {"session_id": session.id}


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------


def build_graph(client: LLMClient, db: AsyncSession) -> Any:
    """Compile and return the LangGraph CompiledGraph.

    Args:
        client: LLM backend to use for all agents.
        db: Async DB session used by the save node.

    Returns:
        Compiled LangGraph graph ready for ``.ainvoke()``.
    """
    graph = StateGraph(TradingState)

    graph.add_node("sub_agents", partial(sub_agents_node, client=client))
    graph.add_node("master", partial(master_node, client=client))
    graph.add_node("save", partial(save_node, db=db))

    graph.add_edge(START, "sub_agents")
    graph.add_edge("sub_agents", "master")
    graph.add_edge("master", "save")
    graph.add_edge("save", END)

    return graph.compile()


async def run_agent_session(
    market_data: dict,
    client: LLMClient,
    db: AsyncSession,
    position: dict | None = None,
) -> TradingState:
    """Execute the full multi-agent trading workflow.

    Args:
        market_data: Output of ``generate_ai_payload()``.
        client: LLM backend.
        db: Async DB session.
        position: Current open position, or None.

    Returns:
        Final :class:`TradingState` after all nodes have executed.
    """
    compiled = build_graph(client, db)

    initial_state: TradingState = {
        "market_data": market_data,
        "position": position,
        "trend_opinion": None,
        "contrarian_opinion": None,
        "risk_opinion": None,
        "final_decision": None,
        "session_id": None,
    }

    result: TradingState = await compiled.ainvoke(initial_state)
    return result
