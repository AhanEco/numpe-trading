"""Main entry point for NUMPE TRADING SOFTWARE backend application."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base, async_session_maker
from app.routers import (
    market,
    technical,
    fundamental,
    signals,
    news,
    backtesting,
    settings as settings_router,
    system,
)
from app.services.scheduler import scheduler_service
from app.services.market_data import market_data_service
from app.services.technical_indicators import technical_indicator_service
from app.services.fundamental_valuation import fundamental_valuation_service
from app.services.news_intelligence import news_intelligence_service
from app.utils.timezone import now_ist, format_ist_timestamp

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("numpe")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: database initialization and scheduler management."""
    logger.info("Initializing NUMPE Trading Software database tables …")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified.")

    # Start automated background update scheduler
    scheduler_service.start()

    # Initial data verification & seeding if empty
    async with async_session_maker() as db:
        try:
            logger.info("Verifying market data baseline …")
            await market_data_service.update_daily_prices(db)
            await technical_indicator_service.compute_and_store_indicators(db)
            # Seed baseline valuation if missing
            await fundamental_valuation_service.get_current_valuation(db)
            # Initial news fetch
            await news_intelligence_service.process_and_store_news(db)
            await news_intelligence_service.generate_daily_briefing(db)
            logger.info("Initial market data & news pipelines initialized.")
        except Exception as exc:
            logger.warning("Initial pipeline warmup encountered non-critical error: %s", exc)

    yield

    # Shutdown
    scheduler_service.shutdown()
    await engine.dispose()
    logger.info("NUMPE backend shutdown cleanly.")


app = FastAPI(
    title="Numpecraft API",
    description="Quantitative Financial Intelligence and Investment Monitoring Platform for Nifty 100 Equal Weight Index.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(market.router)
app.include_router(technical.router)
app.include_router(fundamental.router)
app.include_router(signals.router)
app.include_router(news.router)
app.include_router(backtesting.router)
app.include_router(settings_router.router)
app.include_router(system.router)

# Mount frontend static distribution if built
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist_candidates = [
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"),
    os.path.join(os.getcwd(), "frontend", "dist"),
    "/app/frontend_dist",
]

frontend_dist = None
for candidate in frontend_dist_candidates:
    if os.path.exists(candidate) and os.path.isdir(candidate):
        frontend_dist = os.path.abspath(candidate)
        break

if frontend_dist:
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Don't hijack /api or /docs
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "brand": "Numpecraft",
            "tagline": "Data-Driven Decisions. Disciplined Investing.",
            "instrument": "Nifty 100 Equal Weight Index",
            "status": "Online",
            "timestamp_ist": format_ist_timestamp(now_ist()),
            "docs_url": "/docs",
        }
