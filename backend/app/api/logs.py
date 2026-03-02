"""AI discussion logs API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.trading import AgentOpinion, AgentSession, FinalDecision

router = APIRouter(prefix="/api/logs", tags=["logs"])


class AgentOpinionSchema(BaseModel):
    id: int
    agent_name: str
    action: str
    confidence: float
    reasoning: str
    created_at: datetime

    class Config:
        from_attributes = True


class FinalDecisionSchema(BaseModel):
    id: int
    action: str
    confidence: float
    reasoning: str
    created_at: datetime

    class Config:
        from_attributes = True


class AgentSessionSchema(BaseModel):
    id: int
    created_at: datetime
    opinions: list[AgentOpinionSchema]
    final_decision: FinalDecisionSchema | None

    class Config:
        from_attributes = True


@router.get("", response_model=list[AgentSessionSchema])
async def list_logs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AgentSession)
        .options(
            selectinload(AgentSession.opinions),
            selectinload(AgentSession.final_decision),
        )
        .order_by(AgentSession.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    sessions = result.scalars().all()
    return sessions
