"""API router for NLP financial news intelligence."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.news_intelligence import news_intelligence_service

router = APIRouter(prefix="/api/news", tags=["News Intelligence"])


@router.get("/latest")
async def get_latest_news(
    limit: int = Query(25, ge=1, le=100),
    topic: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the latest financial news articles with NLP metadata (topic, sentiment, entities, relevance)."""
    articles = await news_intelligence_service.get_latest_news(
        db, limit=limit, topic=topic, sentiment=sentiment
    )
    return {
        "count": len(articles),
        "articles": articles,
    }


@router.get("/briefing")
async def get_daily_briefing(db: AsyncSession = Depends(get_db)):
    """Retrieve Today's Indian Equity Market Intelligence daily briefing."""
    return await news_intelligence_service.generate_daily_briefing(db)


@router.get("/sentiment-summary")
async def get_sentiment_summary(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve market sentiment breakdown over the past N days."""
    return await news_intelligence_service.get_sentiment_summary(db, days=days)


@router.post("/refresh")
async def trigger_news_refresh(db: AsyncSession = Depends(get_db)):
    """Trigger manual fetch of RSS news feeds and NLP pipeline."""
    count = await news_intelligence_service.process_and_store_news(db)
    return {"message": f"Processed and stored {count} new articles."}

