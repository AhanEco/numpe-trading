"""Pydantic request / response schemas for the API."""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ═══════════════════════════════════════════════════════════════════════════
#  Index Price
# ═══════════════════════════════════════════════════════════════════════════
class IndexPriceBase(BaseModel):
    date: datetime.date
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    index_name: str = "NIFTY100_EQUAL_WEIGHT"
    source: Optional[str] = None


class IndexPriceCreate(IndexPriceBase):
    pass


class IndexPriceResponse(IndexPriceBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Technical Indicator
# ═══════════════════════════════════════════════════════════════════════════
class TechnicalIndicatorBase(BaseModel):
    date: datetime.date
    index_name: str = "NIFTY100_EQUAL_WEIGHT"
    rsi_14: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    distance_from_sma200_pct: Optional[float] = None
    distance_from_52w_low_pct: Optional[float] = None
    distance_from_52w_high_pct: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    daily_change_pct: Optional[float] = None
    source: Optional[str] = None


class TechnicalIndicatorCreate(TechnicalIndicatorBase):
    pass


class TechnicalIndicatorResponse(TechnicalIndicatorBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Valuation Metric
# ═══════════════════════════════════════════════════════════════════════════
class ValuationMetricBase(BaseModel):
    date: datetime.date
    index_name: str = "NIFTY100_EQUAL_WEIGHT"
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    earnings_yield: Optional[float] = None
    pe_1y_avg: Optional[float] = None
    pe_3y_avg: Optional[float] = None
    pe_5y_avg: Optional[float] = None
    pe_percentile: Optional[float] = None
    pb_1y_avg: Optional[float] = None
    pb_3y_avg: Optional[float] = None
    pb_5y_avg: Optional[float] = None
    pb_percentile: Optional[float] = None
    pe_type: Optional[str] = "trailing"
    source: Optional[str] = None


class ValuationMetricCreate(ValuationMetricBase):
    pass


class ValuationMetricResponse(ValuationMetricBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Investment Signal
# ═══════════════════════════════════════════════════════════════════════════
class InvestmentSignalBase(BaseModel):
    date: datetime.date
    index_name: str = "NIFTY100_EQUAL_WEIGHT"
    price_condition_met: Optional[bool] = False
    rsi_condition_met: Optional[bool] = False
    pe_condition_met: Optional[bool] = False
    pb_condition_met: Optional[bool] = False
    conditions_met_count: Optional[int] = 0
    signal_category: Optional[str] = None
    market_assessment: Optional[str] = None
    current_price: Optional[float] = None
    price_threshold: Optional[float] = None
    current_rsi: Optional[float] = None
    rsi_threshold: Optional[float] = None
    current_pe: Optional[float] = None
    pe_threshold: Optional[float] = None
    current_pb: Optional[float] = None
    pb_lower: Optional[float] = None
    pb_upper: Optional[float] = None
    sma_200: Optional[float] = None
    low_52w: Optional[float] = None
    details_json: Optional[Any] = None


class InvestmentSignalCreate(InvestmentSignalBase):
    pass


class InvestmentSignalResponse(InvestmentSignalBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
#  News Article
# ═══════════════════════════════════════════════════════════════════════════
class NewsArticleBase(BaseModel):
    headline: str
    publisher: Optional[str] = None
    published_at: Optional[datetime.datetime] = None
    source_url: Optional[str] = None
    topic: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    named_entities: Optional[Any] = None
    summary: Optional[str] = None
    market_relevance: Optional[str] = None
    confidence_score: Optional[float] = None
    is_duplicate: Optional[bool] = False
    raw_content_hash: Optional[str] = None


class NewsArticleCreate(NewsArticleBase):
    pass


class NewsArticleResponse(NewsArticleBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Daily Briefing
# ═══════════════════════════════════════════════════════════════════════════
class DailyBriefingBase(BaseModel):
    date: datetime.date
    content: Optional[str] = None
    key_positives: Optional[Any] = None
    key_negatives: Optional[Any] = None
    macro_risks: Optional[Any] = None
    rbi_developments: Optional[Any] = None
    fii_dii_developments: Optional[Any] = None
    nifty_implications: Optional[Any] = None


class DailyBriefingCreate(DailyBriefingBase):
    pass


class DailyBriefingResponse(DailyBriefingBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
#  System Log
# ═══════════════════════════════════════════════════════════════════════════
class SystemLogResponse(BaseModel):
    id: int
    timestamp: datetime.datetime
    level: str
    component: Optional[str] = None
    message: str
    details: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
#  User Settings
# ═══════════════════════════════════════════════════════════════════════════
class UserSettingsResponse(BaseModel):
    id: int
    key: str
    value: Optional[Any] = None
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class SettingsUpdate(BaseModel):
    """Payload for updating one or more settings keys."""
    settings: Dict[str, Any] = Field(
        ...,
        description="Mapping of setting key → new value (JSON-compatible).",
        examples=[{"pe_threshold": 22.0, "rsi_threshold": 40}],
    )


# ═══════════════════════════════════════════════════════════════════════════
#  Data Source Info
# ═══════════════════════════════════════════════════════════════════════════
class DataSourceInfoResponse(BaseModel):
    id: int
    source_name: str
    data_type: Optional[str] = None
    last_success: Optional[datetime.datetime] = None
    last_failure: Optional[datetime.datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Composite / convenience schemas
# ═══════════════════════════════════════════════════════════════════════════
class MarketOverview(BaseModel):
    """Snapshot combining price, valuation, and technical highlights."""
    index_name: str = "NIFTY100_EQUAL_WEIGHT"
    date: Optional[datetime.date] = None
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    daily_change: Optional[float] = None
    daily_change_pct: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    earnings_yield: Optional[float] = None
    rsi_14: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    signal_category: Optional[str] = None
    conditions_met_count: Optional[int] = None
    market_assessment: Optional[str] = None


class SignalResponse(BaseModel):
    """Detailed signal with every condition spelled out."""
    signal: Optional[InvestmentSignalResponse] = None
    conditions: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class NewsResponse(BaseModel):
    """Paginated list of news articles."""
    articles: List[NewsArticleResponse] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class HistoricalDataResponse(BaseModel):
    """Generic wrapper for historical data with metadata."""
    data: List[Any] = []
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    count: int = 0
    index_name: str = "NIFTY100_EQUAL_WEIGHT"


class SentimentSummary(BaseModel):
    """Aggregated sentiment distribution."""
    total_articles: int = 0
    positive: int = 0
    negative: int = 0
    neutral: int = 0
    positive_pct: float = 0.0
    negative_pct: float = 0.0
    neutral_pct: float = 0.0
    avg_sentiment_score: Optional[float] = None
    period_start: Optional[datetime.date] = None
    period_end: Optional[datetime.date] = None


# ═══════════════════════════════════════════════════════════════════════════
#  Backtesting
# ═══════════════════════════════════════════════════════════════════════════
class BacktestRequest(BaseModel):
    """Parameters for running a backtest."""
    strategy: str = Field(
        ...,
        description="Strategy name, e.g. 'sip_on_signal', 'fixed_sip', 'lumpsum'.",
        examples=["sip_on_signal"],
    )
    start_date: datetime.date = Field(..., description="Backtest start date.")
    end_date: datetime.date = Field(..., description="Backtest end date.")
    initial_investment: float = Field(default=100000.0, ge=0)
    monthly_sip: float = Field(default=10000.0, ge=0)
    pe_threshold: Optional[float] = Field(default=22.0, description="PE below which to invest more.")
    rsi_threshold: Optional[float] = Field(default=40.0, description="RSI below which to invest more.")
    extra_params: Optional[Dict[str, Any]] = Field(default=None, description="Strategy-specific params.")


class BacktestResult(BaseModel):
    """Per-period result inside a backtest."""
    date: datetime.date
    action: str
    amount_invested: float
    units_bought: float
    price: float
    cumulative_investment: float
    cumulative_units: float
    portfolio_value: float


class BacktestResponse(BaseModel):
    """Full backtest output."""
    strategy: str
    start_date: datetime.date
    end_date: datetime.date
    initial_investment: float
    total_invested: float
    final_value: float
    absolute_return: float
    return_pct: float
    cagr_pct: Optional[float] = None
    max_drawdown_pct: Optional[float] = None
    num_investments: int = 0
    results: List[BacktestResult] = []
    benchmark_return_pct: Optional[float] = None
    outperformance_pct: Optional[float] = None


# ═══════════════════════════════════════════════════════════════════════════
#  Auth
# ═══════════════════════════════════════════════════════════════════════════
class LoginRequest(BaseModel):
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
