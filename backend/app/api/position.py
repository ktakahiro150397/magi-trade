"""Current position API endpoint."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.trading import Trade

router = APIRouter(prefix="/api/position", tags=["position"])


class PositionSchema(BaseModel):
    id: int
    symbol: str
    side: str
    size: float
    entry_price: float
    stop_loss: float | None
    take_profit: float | None
    status: str

    class Config:
        from_attributes = True


@router.get("", response_model=list[PositionSchema])
async def get_open_positions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Trade)
        .where(Trade.status == "OPEN")
        .order_by(Trade.created_at.desc())
    )
    trades = result.scalars().all()
    return trades
