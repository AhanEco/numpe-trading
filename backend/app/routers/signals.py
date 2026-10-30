"""API router for NUMPE quantitative investment signals."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.signal_engine import signal_engine

router = APIRouter(prefix="/api/signals", tags=["Investment Signals"])


@router.get("/current")
async def get_current_signal(db: AsyncSession = Depends(get_db)):
    """
    Get the comprehensive NUMPE Investment Monitor signal evaluation:
    - 4 individual condition checks (Price Anchor, RSI, Consolidated P/E, P/B)
    - Condition statuses (actual value, target, pass/fail)
    - Qualitative market assessment
    - Full transparent formula breakdown and disclaimers
    """
    return await signal_engine.compute_current_signal(db)

