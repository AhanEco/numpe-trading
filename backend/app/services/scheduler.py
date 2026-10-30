"""Background scheduler service for automated daily updates."""

from __future__ import annotations

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.database import async_session_maker
from app.services.market_data import market_data_service
from app.services.technical_indicators import technical_indicator_service
from app.services.news_intelligence import news_intelligence_service
from app.services.signal_engine import signal_engine
from app.utils.timezone import IST

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=IST)

    async def run_market_pipeline(self):
        """Fetch daily closing prices, update technical indicators, and refresh investment signals."""
        logger.info("Executing scheduled market data pipeline ...")
        async with async_session_maker() as db:
            try:
                # 1. Update prices
                await market_data_service.update_daily_prices(db)
                # 2. Recompute technical indicators
                await technical_indicator_service.compute_and_store_indicators(db)
                # 3. Compute investment signal
                await signal_engine.compute_current_signal(db)
                logger.info("Market data pipeline completed successfully.")
            except Exception as exc:
                logger.error("Error in scheduled market pipeline: %s", exc, exc_info=True)

    async def run_news_pipeline(self):
        """Fetch latest Indian financial news RSS feeds, run NLP classification, and store."""
        logger.info("Executing scheduled financial news NLP pipeline ...")
        async with async_session_maker() as db:
            try:
                count = await news_intelligence_service.process_and_store_news(db)
                logger.info("News pipeline processed %d new articles.", count)
            except Exception as exc:
                logger.error("Error in scheduled news pipeline: %s", exc, exc_info=True)

    async def run_daily_briefing(self):
        """Generate AI daily market intelligence briefing."""
        logger.info("Generating daily market intelligence briefing ...")
        async with async_session_maker() as db:
            try:
                await news_intelligence_service.generate_daily_briefing(db)
                logger.info("Daily briefing generated successfully.")
            except Exception as exc:
                logger.error("Error generating daily briefing: %s", exc, exc_info=True)

    def start(self):
        """Register cron jobs and start scheduler."""
        if not self.scheduler.running:
            # 1. Market data update: Monday to Friday at 15:45 IST (after 15:30 market close)
            self.scheduler.add_job(
                self.run_market_pipeline,
                CronTrigger(day_of_week="mon-fri", hour=15, minute=45, timezone=IST),
                id="market_close_update",
                replace_existing=True,
            )

            # 2. News refresh: every 60 minutes
            self.scheduler.add_job(
                self.run_news_pipeline,
                IntervalTrigger(minutes=60, timezone=IST),
                id="news_hourly_update",
                replace_existing=True,
            )

            # 3. Daily briefing: Monday to Friday at 17:00 IST
            self.scheduler.add_job(
                self.run_daily_briefing,
                CronTrigger(day_of_week="mon-fri", hour=17, minute=0, timezone=IST),
                id="daily_briefing_evening",
                replace_existing=True,
            )

            self.scheduler.start()
            logger.info("Background update scheduler started successfully.")

    def shutdown(self):
        """Graceful shutdown of scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Background update scheduler stopped.")


scheduler_service = SchedulerService()

