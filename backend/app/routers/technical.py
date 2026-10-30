"""API router for technical indicator analysis."""

from __future__ import annotations

import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.technical_indicators import technical_indicator_service

router = APIRouter(prefix="/api/technical", tags=["Technical Analysis"])


@router.get("/current")
async def get_current_indicators(db: AsyncSession = Depends(get_db)):
    """Retrieve the latest technical indicators (RSI-14, 50 SMA, 200 SMA, 52W High/Low, MACD)."""
    return await technical_indicator_service.get_current_indicators(db)


@router.get("/rsi")
async def get_rsi_history(
    start_date: Optional[datetime.date] = Query(None),
    end_date: Optional[datetime.date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical RSI(14) series calculated via Wilder's smoothing."""
    history = await technical_indicator_service.get_rsi_history(db, start_date, end_date)
    return {
        "indicator": "RSI (14)",
        "smoothing_method": "Wilder's Exponential Smoothing",
        "entry_zone": [30.0, 42.0],
        "oversold_threshold": 30.0,
        "overbought_threshold": 70.0,
        "data": history,
    }


@router.get("/sma")
async def get_sma_history(
    start_date: Optional[datetime.date] = Query(None),
    end_date: Optional[datetime.date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical 50-day and 200-day Simple Moving Average series."""
    history = await technical_indicator_service.get_sma_history(db, start_date, end_date)
    return {
        "indicator": "Simple Moving Averages (SMA)",
        "periods": [50, 200],
        "data": history,
    }


@router.get("/macd")
async def get_macd_history(
    start_date: Optional[datetime.date] = Query(None),
    end_date: Optional[datetime.date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical MACD (12, 26, 9) series."""
    history = await technical_indicator_service.get_macd_history(db, start_date, end_date)
    return {
        "indicator": "MACD (12, 26, 9)",
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9,
        "data": history,
    }

