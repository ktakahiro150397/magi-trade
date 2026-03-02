"""Settings API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.trading import TradeSetting

router = APIRouter(prefix="/api/settings", tags=["settings"])


class TradeSettingSchema(BaseModel):
    id: int
    risk_percent: float
    leverage: int
    max_hold_hours: int
    updated_at: datetime

    class Config:
        from_attributes = True


class TradeSettingUpdate(BaseModel):
    risk_percent: float = Field(gt=0, le=100)
    leverage: int = Field(gt=0, le=100)
    max_hold_hours: int = Field(gt=0)


@router.get("", response_model=TradeSettingSchema)
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TradeSetting).limit(1))
    setting = result.scalar_one_or_none()
    if setting is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return setting


@router.put("", response_model=TradeSettingSchema)
async def update_settings(body: TradeSettingUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TradeSetting).limit(1))
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = TradeSetting()
        db.add(setting)

    setting.risk_percent = body.risk_percent
    setting.leverage = body.leverage
    setting.max_hold_hours = body.max_hold_hours
    setting.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(setting)
    return setting
