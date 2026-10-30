"""API router for system health, data pipeline sync, and status."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.market_data import IndexPrice, TechnicalIndicator, ValuationMetric, NewsArticle
from app.services.market_data import market_data_service
from app.services.technical_indicators import technical_indicator_service
from app.services.signal_engine import signal_engine
from app.services.news_intelligence import news_intelligence_service
from app.utils.timezone import now_ist, is_market_open, format_ist_timestamp

router = APIRouter(prefix="/api/system", tags=["System & Health"])


@router.get("/health")
async def health_check():
    """Application health probe."""
    m_open, m_desc = is_market_open()
    return {
        "status": "healthy",
        "app": "NUMPE TRADING SOFTWARE",
        "version": "1.0.0",
        "timestamp_ist": format_ist_timestamp(now_ist()),
        "market_status": m_desc,
    }


@router.get("/status")
async def system_status(db: AsyncSession = Depends(get_db)):
    """Summary of database records and data pipeline state."""
    p_count = (await db.execute(select(func.count(IndexPrice.id)))).scalar() or 0
    t_count = (await db.execute(select(func.count(TechnicalIndicator.id)))).scalar() or 0
    v_count = (await db.execute(select(func.count(ValuationMetric.id)))).scalar() or 0
    n_count = (await db.execute(select(func.count(NewsArticle.id)))).scalar() or 0

    return {
        "tracked_index": "Nifty 100 Equal Weight Index",
        "database_records": {
            "index_prices": p_count,
            "technical_indicators": t_count,
            "valuation_metrics": v_count,
            "news_articles": n_count,
        },
        "market_hours": is_market_open()[1],
        "timezone": "Asia/Kolkata (IST)",
    }


@router.post("/sync")
async def trigger_full_sync(db: AsyncSession = Depends(get_db)):
    """Trigger on-demand data pipeline synchronization."""
    # 1. Update prices
    await market_data_service.update_daily_prices(db)
    # 2. Update technical indicators
    await technical_indicator_service.compute_and_store_indicators(db)
    # 3. Update news
    news_count = await news_intelligence_service.process_and_store_news(db)
    # 4. Generate daily briefing
    await news_intelligence_service.generate_daily_briefing(db)
    # 5. Compute signal
    sig = await signal_engine.compute_current_signal(db)

    return {
        "status": "success",
        "message": "Full synchronization completed.",
        "news_added": news_count,
        "signal_summary": sig.get("summary"),
    }

