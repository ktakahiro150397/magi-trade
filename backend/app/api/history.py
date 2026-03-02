"""Trade history API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.trading import Trade

router = APIRouter(prefix="/api/history", tags=["history"])


class TradeSchema(BaseModel):
    id: int
    session_id: int | None
    symbol: str
    side: str
    size: float
    entry_price: float
    exit_price: float | None
    stop_loss: float | None
    take_profit: float | None
    pnl: float | None
    status: str
    created_at: datetime
    closed_at: datetime | None

    class Config:
        from_attributes = True


@router.get("", response_model=list[TradeSchema])
async def list_trades(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Trade).order_by(Trade.created_at.desc()).limit(limit).offset(offset)
    if status:
        query = query.where(Trade.status == status.upper())

    result = await db.execute(query)
    trades = result.scalars().all()
    return trades
