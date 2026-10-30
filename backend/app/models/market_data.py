"""SQLAlchemy ORM models for all market-data related tables."""

from __future__ import annotations

import datetime
from typing import Optional, Any

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# ═══════════════════════════════════════════════════════════════════════════
#  Index Price (OHLCV)
# ═══════════════════════════════════════════════════════════════════════════
class IndexPrice(Base):
    """Daily OHLCV data for a tracked index."""

    __tablename__ = "index_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    open: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    close: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    index_name: Mapped[str] = mapped_column(String(128), nullable=False, default="NIFTY100_EQUAL_WEIGHT")
    source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_index_prices_date_index", "date", "index_name"),
        Index("ix_index_prices_date", "date"),
        Index("ix_index_prices_index_name", "index_name"),
    )

    def __repr__(self) -> str:
        return f"<IndexPrice {self.index_name} {self.date} close={self.close}>"


# ═══════════════════════════════════════════════════════════════════════════
#  Technical Indicators
# ═══════════════════════════════════════════════════════════════════════════
class TechnicalIndicator(Base):
    """Computed technical indicators for an index on a given date."""

    __tablename__ = "technical_indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    index_name: Mapped[str] = mapped_column(String(128), nullable=False, default="NIFTY100_EQUAL_WEIGHT")

    # RSI
    rsi_14: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Moving averages
    sma_50: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sma_200: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ema_12: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ema_26: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # MACD
    macd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    macd_signal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    macd_histogram: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Distance metrics
    distance_from_sma200_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_from_52w_low_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_from_52w_high_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # 52-week range
    high_52w: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    low_52w: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Daily change
    daily_change_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_tech_date_index", "date", "index_name"),
        Index("ix_tech_date", "date"),
        Index("ix_tech_index_name", "index_name"),
    )

    def __repr__(self) -> str:
        return f"<TechnicalIndicator {self.index_name} {self.date} rsi={self.rsi_14}>"


# ═══════════════════════════════════════════════════════════════════════════
#  Valuation Metrics
# ═══════════════════════════════════════════════════════════════════════════
class ValuationMetric(Base):
    """Fundamental valuation metrics (PE, PB) for an index on a given date."""

    __tablename__ = "valuation_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    index_name: Mapped[str] = mapped_column(String(128), nullable=False, default="NIFTY100_EQUAL_WEIGHT")

    # Current ratios
    pe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pb_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    earnings_yield: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # PE averages
    pe_1y_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pe_3y_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pe_5y_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pe_percentile: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # PB averages
    pb_1y_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pb_3y_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pb_5y_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pb_percentile: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    pe_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, default="trailing")
    source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_val_date_index", "date", "index_name"),
        Index("ix_val_date", "date"),
        Index("ix_val_index_name", "index_name"),
    )

    def __repr__(self) -> str:
        return f"<ValuationMetric {self.index_name} {self.date} PE={self.pe_ratio}>"


# ═══════════════════════════════════════════════════════════════════════════
#  Investment Signals
# ═══════════════════════════════════════════════════════════════════════════
class InvestmentSignal(Base):
    """Generated investment signal combining multiple conditions."""

    __tablename__ = "investment_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    index_name: Mapped[str] = mapped_column(String(128), nullable=False, default="NIFTY100_EQUAL_WEIGHT")

    # Condition flags
    price_condition_met: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    rsi_condition_met: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    pe_condition_met: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    pb_condition_met: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)

    conditions_met_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    signal_category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    market_assessment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Current values
    current_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_rsi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rsi_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_pe: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pe_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_pb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pb_lower: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pb_upper: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sma_200: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    low_52w: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    details_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_signal_date_index", "date", "index_name"),
        Index("ix_signal_date", "date"),
        Index("ix_signal_category", "signal_category"),
    )

    def __repr__(self) -> str:
        return f"<InvestmentSignal {self.index_name} {self.date} cat={self.signal_category}>"


# ═══════════════════════════════════════════════════════════════════════════
#  News Articles
# ═══════════════════════════════════════════════════════════════════════════
class NewsArticle(Base):
    """Parsed and sentiment-analysed news article."""

    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    publisher: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    published_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topic: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Sentiment
    sentiment: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # positive/negative/neutral
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    named_entities: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    market_relevance: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    is_duplicate: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    raw_content_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_news_published_at", "published_at"),
        Index("ix_news_sentiment", "sentiment"),
        Index("ix_news_topic", "topic"),
        Index("ix_news_hash", "raw_content_hash"),
    )

    def __repr__(self) -> str:
        return f"<NewsArticle id={self.id} sentiment={self.sentiment}>"


# ═══════════════════════════════════════════════════════════════════════════
#  Daily Briefing
# ═══════════════════════════════════════════════════════════════════════════
class DailyBriefing(Base):
    """AI-generated daily market briefing."""

    __tablename__ = "daily_briefings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, unique=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    key_positives: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    key_negatives: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    macro_risks: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    rbi_developments: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    fii_dii_developments: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    nifty_implications: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_briefing_date", "date"),
    )

    def __repr__(self) -> str:
        return f"<DailyBriefing {self.date}>"


# ═══════════════════════════════════════════════════════════════════════════
#  System Log
# ═══════════════════════════════════════════════════════════════════════════
class SystemLog(Base):
    """Application-level log entries."""

    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    level: Mapped[str] = mapped_column(String(16), nullable=False, default="INFO")
    component: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_syslog_timestamp", "timestamp"),
        Index("ix_syslog_level", "level"),
        Index("ix_syslog_component", "component"),
    )

    def __repr__(self) -> str:
        return f"<SystemLog [{self.level}] {self.component}: {self.message[:40]}>"


# ═══════════════════════════════════════════════════════════════════════════
#  User Settings (key-value store)
# ═══════════════════════════════════════════════════════════════════════════
class UserSettings(Base):
    """Key-value settings store (thresholds, preferences, etc.)."""

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_settings_key", "key"),
    )

    def __repr__(self) -> str:
        return f"<UserSettings {self.key}>"


# ═══════════════════════════════════════════════════════════════════════════
#  Data Source Info
# ═══════════════════════════════════════════════════════════════════════════
class DataSourceInfo(Base):
    """Health / status tracking for each external data source."""

    __tablename__ = "data_source_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    data_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_success: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, default="unknown")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_datasource_name", "source_name"),
    )

    def __repr__(self) -> str:
        return f"<DataSourceInfo {self.source_name} status={self.status}>"
