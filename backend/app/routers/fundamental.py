"""API router for fundamental valuation analysis."""

from __future__ import annotations

import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.fundamental_valuation import fundamental_valuation_service

router = APIRouter(prefix="/api/fundamental", tags=["Fundamental Analysis"])


@router.get("/current")
async def get_current_valuation(db: AsyncSession = Depends(get_db)):
    """Retrieve the latest consolidated P/E, P/B, earnings yield, and historical percentile ranks."""
    return await fundamental_valuation_service.get_current_valuation(db)


@router.get("/history")
async def get_valuation_history(
    start_date: Optional[datetime.date] = Query(None),
    end_date: Optional[datetime.date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical P/E and P/B valuation series."""
    history = await fundamental_valuation_service.get_history(db, start_date, end_date)
    return {
        "index_name": "Nifty 100 Equal Weight",
        "count": len(history),
        "data": history,
    }

