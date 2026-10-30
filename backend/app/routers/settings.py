"""API router for user thresholds and administrative settings."""

from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.market_data import UserSettings
from app.services.signal_engine import signal_engine
from app.utils.auth import verify_password, create_access_token, get_current_admin

router = APIRouter(prefix="/api/settings", tags=["Settings & Authentication"])


class LoginPayload(BaseModel):
    password: str


class SettingsPayload(BaseModel):
    rsi_threshold: float
    pe_threshold: float
    pb_lower: float
    pb_upper: float
    price_interpretation: str  # "below" or "band"
    price_band_pct: float
    sma_period: int


@router.post("/auth/login")
async def admin_login(payload: LoginPayload):
    """Admin login endpoint returning JWT bearer token."""
    if not verify_password(payload.password, ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    token = create_access_token(data={"role": "admin"})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/")
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Retrieve current signal evaluation thresholds (publicly visible for transparency)."""
    return await signal_engine.get_effective_settings(db)


@router.put("/")
async def update_settings(
    payload: SettingsPayload,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update investment signal thresholds (requires Admin authentication)."""
    stmt = select(UserSettings).where(UserSettings.key == "signal_settings")
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    new_vals = payload.dict()
    if record:
        record.value = new_vals
    else:
        record = UserSettings(key="signal_settings", value=new_vals)
        db.add(record)

    await db.commit()
    return {"message": "Settings updated successfully", "settings": new_vals}

