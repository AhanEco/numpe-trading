"""API router for Nifty 100 Equal Weight market data."""

from __future__ import annotations

import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.market_data import market_data_service
from app.services.technical_indicators import technical_indicator_service
from app.services.fundamental_valuation import fundamental_valuation_service
from app.utils.timezone import is_market_open, format_ist_timestamp

router = APIRouter(prefix="/api/market", tags=["Market Data"])


@router.get("/overview")
async def get_market_overview(db: AsyncSession = Depends(get_db)):
    """
    Get top-level dashboard market overview:
    - Current Nifty 100 Equal Weight price
    - Daily change and % change
    - Consolidated P/E
    - Current RSI (14)
    - Market open/close status
    - Timestamp in IST
    """
    latest_price = await market_data_service.get_latest_price(db)
    current_tech = await technical_indicator_service.get_current_indicators(db)
    current_val = await fundamental_valuation_service.get_current_valuation(db)
    market_status, status_desc = is_market_open()

    price = latest_price.get("close")
    prev_close = latest_price.get("previous_close")
    change = round(price - prev_close, 2) if price and prev_close else 0.0
    change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0

    return {
        "index_name": "Nifty 100 Equal Weight",
        "current_price": price,
        "previous_close": prev_close,
        "daily_change": change,
        "daily_change_pct": change_pct,
        "pe_ratio": current_val.get("pe_ratio"),
        "pb_ratio": current_val.get("pb_ratio"),
        "rsi_14": current_tech.get("rsi_14"),
        "rsi_interpretation": (
            current_tech.get("rsi_interpretation", {}).get("description")
            if isinstance(current_tech.get("rsi_interpretation"), dict)
            else (current_tech.get("rsi_interpretation") or "Neutral momentum")
        ),
        "high_52w": current_tech.get("high_52w"),
        "low_52w": current_tech.get("low_52w"),
        "sma_200": current_tech.get("sma_200"),
        "sma_50": current_tech.get("sma_50"),
        "distance_from_sma200_pct": current_tech.get("distance_from_sma200_pct"),
        "distance_from_52w_low_pct": current_tech.get("distance_from_52w_low_pct"),
        "is_market_open": market_status,
        "market_status_text": status_desc,
        "observation_date": latest_price.get("date"),
        "source": latest_price.get("source"),
        "data_quality": "Official closing/delayed market observations",
    }


@router.get("/prices")
async def get_historical_prices(
    start_date: Optional[datetime.date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical OHLCV price series."""
    prices = await market_data_service.get_stored_prices(db, start_date, end_date)
    return {
        "index_name": "Nifty 100 Equal Weight",
        "count": len(prices),
        "data": prices,
    }


@router.get("/prices/latest")
async def get_latest_price(db: AsyncSession = Depends(get_db)):
    """Retrieve latest available index price."""
    return await market_data_service.get_latest_price(db)


@router.get("/export/csv")
async def export_prices_csv(
    start_date: Optional[datetime.date] = Query(None),
    end_date: Optional[datetime.date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Export historical prices as CSV."""
    csv_data = await market_data_service.export_csv(db, start_date, end_date)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=nifty100_equal_weight_prices.csv"},
    )

