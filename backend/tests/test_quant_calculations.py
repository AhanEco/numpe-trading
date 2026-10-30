"""Unit and verification tests for NUMPE quantitative calculations and signal logic."""

import datetime
import pytest
import numpy as np
import pandas as pd

from app.services.technical_indicators import TechnicalIndicatorService
from app.services.fundamental_valuation import FundamentalValuationService
from app.services.signal_engine import SignalEngine
from app.services.news_intelligence import NewsIntelligenceService
from app.utils.timezone import to_ist, now_ist, is_market_open, IST


def test_sma_calculation():
    """Verify Simple Moving Average formula."""
    service = TechnicalIndicatorService()
    series = pd.Series([100.0, 102.0, 104.0, 106.0, 108.0])
    sma = service.calculate_sma(series, period=3)
    
    # Expected: NaN, NaN, (100+102+104)/3=102, (102+104+106)/3=104, (104+106+108)/3=106
    assert np.isnan(sma.iloc[0])
    assert np.isnan(sma.iloc[1])
    assert round(sma.iloc[2], 2) == 102.00
    assert round(sma.iloc[3], 2) == 104.00
    assert round(sma.iloc[4], 2) == 106.00


def test_rsi_wilders_smoothing():
    """Verify RSI calculation uses Wilder's exponential smoothing."""
    service = TechnicalIndicatorService()
    # 20 sessions with steady gains
    prices = pd.Series([100 + i * 2 for i in range(25)])
    rsi = service.calculate_rsi(prices, period=14)
    # With only gains, RS should be infinite and RSI should be 100
    assert rsi.iloc[-1] == 100.0

    # Test alternating gains and losses with symmetric steady state
    alternating = pd.Series([100 if i % 2 == 0 else 105 for i in range(60)])
    rsi_alt = service.calculate_rsi(alternating, period=14)
    # Balanced oscillation oscillates symmetrically around 50 (e.g. between 35 and 65 depending on even/odd step)
    assert 30.0 <= rsi_alt.iloc[-1] <= 70.0


def test_52w_high_low_and_distances():
    """Verify 52-week high/low and distance percentages."""
    service = TechnicalIndicatorService()
    prices = pd.Series([20000.0, 24000.0, 18000.0, 22000.0])
    high_52, low_52 = service.calculate_52w_high_low(prices)
    assert high_52 == 24000.0
    assert low_52 == 18000.0

    # Distance from 200 SMA: [(Price - SMA) / SMA] * 100
    current_price = 22000.0
    sma200 = 20000.0
    dist_sma = service.calculate_distance_from_sma(current_price, sma200)
    assert dist_sma == 10.0  # +10%

    # Distance from 52w low: [(Price - Low) / Low] * 100
    dist_low = service.calculate_distance_from_52w_low(current_price, low_52)
    expected_dist_low = round(((22000 - 18000) / 18000) * 100, 2)
    assert round(dist_low, 2) == expected_dist_low


def test_earnings_yield():
    """Verify Earnings Yield = (1 / P/E) * 100."""
    service = FundamentalValuationService()
    pe = 20.0
    ey = service.calculate_earnings_yield(pe)
    assert ey == 5.0  # 1/20 * 100 = 5%

    pe_high = 25.0
    assert service.calculate_earnings_yield(pe_high) == 4.0

    # Edge cases
    assert service.calculate_earnings_yield(None) is None
    assert service.calculate_earnings_yield(0) is None


def test_signal_price_threshold_formula():
    """
    Verify Price Threshold formula:
    T = 1.10 * [(52-week low + 200-day SMA) / 2]
    """
    engine = SignalEngine()
    low_52w = 18000.0
    sma_200 = 20000.0
    # Midpoint = (18000 + 20000) / 2 = 19000
    # T = 1.10 * 19000 = 20900.0
    expected_t = 20900.0
    t = engine.calculate_price_threshold(low_52w, sma_200)
    assert t == expected_t

    # Mode A: "below"
    res_below_pass = engine.evaluate_price_condition(current_price=20500.0, threshold=t, mode="below")
    assert res_below_pass["met"] is True
    assert res_below_pass["status"] == "SATISFIED"

    res_below_fail = engine.evaluate_price_condition(current_price=21500.0, threshold=t, mode="below")
    assert res_below_fail["met"] is False
    assert res_below_fail["status"] == "NOT_SATISFIED"

    # Mode B: "band" with +/- 2%
    # Band = [20900 * 0.98, 20900 * 1.02] = [20482.0, 21318.0]
    res_band_pass = engine.evaluate_price_condition(current_price=20950.0, threshold=t, mode="band", band_pct=2.0)
    assert res_band_pass["met"] is True

    res_band_fail = engine.evaluate_price_condition(current_price=22000.0, threshold=t, mode="band", band_pct=2.0)
    assert res_band_fail["met"] is False


def test_signal_conditions_full_suite():
    """Verify evaluation of all 4 conditions and overall categorization."""
    engine = SignalEngine()

    # All conditions satisfied:
    # Price <= 20900, RSI < 42, PE < 20, PB in [2.7, 3.2]
    c1 = engine.evaluate_price_condition(20000, 20900, mode="below")
    c2 = engine.evaluate_rsi_condition(38.5, threshold=42.0)
    c3 = engine.evaluate_pe_condition(18.5, threshold=20.0)
    c4 = engine.evaluate_pb_condition(2.9, lower=2.7, upper=3.2)

    assert c1["met"] is True
    assert c2["met"] is True
    assert c3["met"] is True
    assert c4["met"] is True

    # Assessment
    assessment = engine.derive_market_assessment(
        cond_met=4, cond_total=4, rsi_met=True, pe_met=True, has_sufficient_data=True
    )
    assert assessment == "Potentially Attractive Valuation"


def test_news_deduplication_and_sentiment():
    """Verify news hashing and sentiment scoring."""
    service = NewsIntelligenceService()

    # Hash consistency
    h1 = service.compute_content_hash("Nifty rallies on strong GDP", "https://example.com/1")
    h2 = service.compute_content_hash("NIFTY rallies on strong GDP  ", "https://example.com/1")
    assert h1 == h2

    # Sentiment analysis
    pos_res = service.analyze_sentiment("Nifty surges to record high as corporate earnings rally")
    assert pos_res["sentiment"] == "positive"
    assert pos_res["sentiment_score"] > 0

    neg_res = service.analyze_sentiment("Markets crash as crude oil spikes amid geopolitical tensions and rate hike fears")
    assert neg_res["sentiment"] == "negative"
    assert neg_res["sentiment_score"] < 0


def test_ist_timezone():
    """Verify IST timezone conversion and market timings."""
    now = now_ist()
    assert str(now.tzinfo) == "Asia/Kolkata"
    
    # Test conversion
    utc_dt = datetime.datetime(2024, 6, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    ist_dt = to_ist(utc_dt)
    # IST is UTC + 5:30 -> 17:30
    assert ist_dt.hour == 17
    assert ist_dt.minute == 30
