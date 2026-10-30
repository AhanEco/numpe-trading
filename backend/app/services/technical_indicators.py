"""
Technical Indicator Service
============================
Pure-Python calculations for RSI (Wilder's smoothing), SMA, EMA, MACD,
52-week high/low, and derived distance metrics.  Results are persisted in
the ``TechnicalIndicator`` model for quick retrieval by the dashboard.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market_data import IndexPrice, TechnicalIndicator, SystemLog

logger = logging.getLogger(__name__)


class TechnicalIndicatorService:
    """Calculate and persist technical indicators for the tracked index."""

    INDEX_NAME = "Nifty 100 Equal Weight"

    # ------------------------------------------------------------------
    # Pure calculation methods (stateless, synchronous)
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index using **Wilder's exponential smoothing**.

        RSI = 100 − 100 / (1 + RS)
        RS  = EWMA(gains, α=1/period) / EWMA(losses, α=1/period)

        The first *period* values use simple averages; subsequent values
        apply the exponential weighting as per Wilder's original method.
        """
        delta = prices.diff()
        gains = delta.clip(lower=0.0)
        losses = (-delta).clip(lower=0.0)

        # Wilder's smoothing is an EMA with alpha = 1/period
        alpha = 1.0 / period
        avg_gain = gains.ewm(alpha=alpha, min_periods=period, adjust=False).mean()
        avg_loss = losses.ewm(alpha=alpha, min_periods=period, adjust=False).mean()

        # Handle zero loss (RS -> inf => RSI -> 100) and zero gain (RS = 0 => RSI -> 0)
        rsi = pd.Series(index=prices.index, dtype=float)
        both_valid = (avg_gain.notna()) & (avg_loss.notna())

        zero_loss = both_valid & (avg_loss == 0) & (avg_gain > 0)
        zero_gain = both_valid & (avg_gain == 0) & (avg_loss > 0)
        both_zero = both_valid & (avg_gain == 0) & (avg_loss == 0)
        normal = both_valid & (avg_loss > 0)

        rsi[zero_loss] = 100.0
        rsi[zero_gain] = 0.0
        rsi[both_zero] = 50.0

        rs_normal = avg_gain[normal] / avg_loss[normal]
        rsi[normal] = 100.0 - (100.0 / (1.0 + rs_normal))
        return rsi

    @staticmethod
    def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average over *period* observations."""
        return prices.rolling(window=period, min_periods=period).mean()

    @staticmethod
    def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average with span = *period*."""
        return prices.ewm(span=period, min_periods=period, adjust=False).mean()

    def calculate_macd(
        self,
        prices: pd.Series,
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Moving Average Convergence Divergence.

        Returns:
            (macd_line, signal_line, histogram)
        """
        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, min_periods=9, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_52w_high_low(prices: pd.Series) -> tuple[float, float]:
        """52-week (252 trading-day) high and low.

        Returns:
            (high_52w, low_52w)
        """
        lookback = min(252, len(prices))
        recent = prices.iloc[-lookback:]
        return float(recent.max()), float(recent.min())

    @staticmethod
    def calculate_distance_from_sma(price: float, sma: float) -> float:
        """Percentage distance of *price* from *sma*.

        Formula: ((price − sma) / sma) × 100
        """
        if sma == 0 or np.isnan(sma):
            return np.nan
        return ((price - sma) / sma) * 100.0

    @staticmethod
    def calculate_distance_from_52w_low(price: float, low_52w: float) -> float:
        """Percentage distance of *price* from *low_52w*.

        Formula: ((price − low_52w) / low_52w) × 100
        """
        if low_52w == 0 or np.isnan(low_52w):
            return np.nan
        return ((price - low_52w) / low_52w) * 100.0

    @staticmethod
    def calculate_distance_from_52w_high(price: float, high_52w: float) -> float:
        """Percentage distance of *price* from *high_52w*.

        Formula: ((price − high_52w) / high_52w) × 100
        """
        if high_52w == 0 or np.isnan(high_52w):
            return np.nan
        return ((price - high_52w) / high_52w) * 100.0

    @staticmethod
    def interpret_rsi(rsi: float) -> dict:
        """Human-readable interpretation of an RSI value.

        Returns:
            dict with ``value``, ``zone``, ``description``, ``color``.
        """
        if rsi is None or np.isnan(rsi):
            return {
                "value": None,
                "zone": "unknown",
                "description": "RSI data unavailable",
                "color": "gray",
            }

        rsi = round(rsi, 2)

        if rsi < 30:
            return {
                "value": rsi,
                "zone": "oversold",
                "description": "Traditionally oversold — may indicate extreme fear or a potential bounce",
                "color": "green",
            }
        if rsi < 42:
            return {
                "value": rsi,
                "zone": "weak_entry",
                "description": "Weak momentum, within proposed entry zone (RSI < 42)",
                "color": "lime",
            }
        if rsi < 50:
            return {
                "value": rsi,
                "zone": "moderately_weak",
                "description": "Moderately weak momentum — below the 50 midline",
                "color": "yellow",
            }
        if rsi <= 70:
            return {
                "value": rsi,
                "zone": "positive",
                "description": "Positive momentum — price trending upward",
                "color": "orange",
            }
        return {
            "value": rsi,
            "zone": "overbought",
            "description": "Traditionally overbought — may indicate euphoria or an extended rally",
            "color": "red",
        }

    # ------------------------------------------------------------------
    # DB-backed methods (async)
    # ------------------------------------------------------------------

    async def _load_close_prices(
        self, db: AsyncSession, min_rows: int = 250
    ) -> pd.Series:
        """Load stored close prices as a pandas Series indexed by date."""
        stmt = (
            select(IndexPrice)
            .where(IndexPrice.index_name == self.INDEX_NAME)
            .order_by(IndexPrice.date)
        )
        result = await db.execute(stmt)
        rows = result.scalars().all()

        if len(rows) < min_rows:
            logger.warning(
                "Only %d stored price rows (need %d for reliable indicators)",
                len(rows),
                min_rows,
            )

        if not rows:
            return pd.Series(dtype=float)

        dates = [r.date for r in rows]
        closes = [float(r.close) for r in rows]
        return pd.Series(closes, index=pd.DatetimeIndex(dates), name="close")

    async def compute_and_store_indicators(self, db: AsyncSession) -> dict:
        """Compute all indicators from stored prices and persist the latest.

        Returns a summary dict of the computed values.
        """
        close_prices = await self._load_close_prices(db)
        if close_prices.empty:
            logger.error("No close prices available – cannot compute indicators")
            return {"error": "No price data available"}

        try:
            # Core indicators
            rsi_series = self.calculate_rsi(close_prices, 14)
            sma_50 = self.calculate_sma(close_prices, 50)
            sma_200 = self.calculate_sma(close_prices, 200)
            ema_12 = self.calculate_ema(close_prices, 12)
            ema_26 = self.calculate_ema(close_prices, 26)
            macd_line, macd_signal, macd_hist = self.calculate_macd(close_prices)
            high_52w, low_52w = self.calculate_52w_high_low(close_prices)

            latest_close = float(close_prices.iloc[-1])
            latest_date = close_prices.index[-1].date() if hasattr(close_prices.index[-1], "date") else close_prices.index[-1]

            latest_sma_200 = float(sma_200.iloc[-1]) if not np.isnan(sma_200.iloc[-1]) else None
            latest_sma_50 = float(sma_50.iloc[-1]) if not np.isnan(sma_50.iloc[-1]) else None

            dist_sma200 = (
                self.calculate_distance_from_sma(latest_close, latest_sma_200)
                if latest_sma_200 is not None
                else None
            )
            dist_52w_low = self.calculate_distance_from_52w_low(latest_close, low_52w)
            dist_52w_high = self.calculate_distance_from_52w_high(latest_close, high_52w)

            # Daily change %
            if len(close_prices) >= 2:
                prev_close = float(close_prices.iloc[-2])
                daily_change_pct = ((latest_close - prev_close) / prev_close) * 100.0 if prev_close else None
            else:
                daily_change_pct = None

            def _safe(series: pd.Series) -> Optional[float]:
                val = series.iloc[-1]
                if val is None or (isinstance(val, float) and np.isnan(val)):
                    return None
                return round(float(val), 4)

            indicator_data = {
                "date": latest_date,
                "index_name": self.INDEX_NAME,
                "rsi_14": _safe(rsi_series),
                "sma_50": round(latest_sma_50, 2) if latest_sma_50 is not None else None,
                "sma_200": round(latest_sma_200, 2) if latest_sma_200 is not None else None,
                "ema_12": _safe(ema_12),
                "ema_26": _safe(ema_26),
                "macd": _safe(macd_line),
                "macd_signal": _safe(macd_signal),
                "macd_histogram": _safe(macd_hist),
                "distance_from_sma200_pct": round(dist_sma200, 2) if dist_sma200 is not None else None,
                "distance_from_52w_low_pct": round(dist_52w_low, 2) if dist_52w_low is not None else None,
                "distance_from_52w_high_pct": round(dist_52w_high, 2) if dist_52w_high is not None else None,
                "high_52w": round(high_52w, 2),
                "low_52w": round(low_52w, 2),
                "daily_change_pct": round(daily_change_pct, 2) if daily_change_pct is not None else None,
                "source": "calculated",
            }

            # Upsert: replace if same date+index exists
            existing = await db.execute(
                select(TechnicalIndicator).where(
                    and_(
                        TechnicalIndicator.date == latest_date,
                        TechnicalIndicator.index_name == self.INDEX_NAME,
                    )
                )
            )
            row = existing.scalar_one_or_none()
            if row is not None:
                for key, val in indicator_data.items():
                    if key != "date" and key != "index_name":
                        setattr(row, key, val)
            else:
                db.add(TechnicalIndicator(**indicator_data))

            await db.commit()

            # System log
            db.add(
                SystemLog(
                    level="INFO",
                    component="TechnicalIndicatorService",
                    message=f"Indicators computed for {latest_date}",
                    details=f"RSI={indicator_data['rsi_14']}, SMA200={indicator_data['sma_200']}",
                )
            )
            await db.commit()

            # Attach interpretation
            indicator_data["rsi_interpretation"] = self.interpret_rsi(
                indicator_data["rsi_14"]
            )
            return indicator_data

        except Exception as exc:
            logger.exception("compute_and_store_indicators failed: %s", exc)
            await db.rollback()
            return {"error": str(exc)}

    async def get_current_indicators(self, db: AsyncSession) -> dict:
        """Return the most recently stored indicators."""
        stmt = (
            select(TechnicalIndicator)
            .where(TechnicalIndicator.index_name == self.INDEX_NAME)
            .order_by(TechnicalIndicator.date.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        row = result.scalar_one_or_none()

        if row is None:
            return {"error": "No indicator data available. Run compute first."}

        data = {
            "date": row.date.isoformat() if row.date else None,
            "index_name": row.index_name,
            "rsi_14": float(row.rsi_14) if row.rsi_14 is not None else None,
            "sma_50": float(row.sma_50) if row.sma_50 is not None else None,
            "sma_200": float(row.sma_200) if row.sma_200 is not None else None,
            "ema_12": float(row.ema_12) if row.ema_12 is not None else None,
            "ema_26": float(row.ema_26) if row.ema_26 is not None else None,
            "macd": float(row.macd) if row.macd is not None else None,
            "macd_signal": float(row.macd_signal) if row.macd_signal is not None else None,
            "macd_histogram": float(row.macd_histogram) if row.macd_histogram is not None else None,
            "distance_from_sma200_pct": float(row.distance_from_sma200_pct) if row.distance_from_sma200_pct is not None else None,
            "distance_from_52w_low_pct": float(row.distance_from_52w_low_pct) if row.distance_from_52w_low_pct is not None else None,
            "distance_from_52w_high_pct": float(row.distance_from_52w_high_pct) if row.distance_from_52w_high_pct is not None else None,
            "high_52w": float(row.high_52w) if row.high_52w is not None else None,
            "low_52w": float(row.low_52w) if row.low_52w is not None else None,
            "daily_change_pct": float(row.daily_change_pct) if row.daily_change_pct is not None else None,
            "source": row.source,
        }
        data["rsi_interpretation"] = self.interpret_rsi(data["rsi_14"])
        return data

    async def get_rsi_history(
        self,
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        """Return RSI history within the date range."""
        stmt = select(TechnicalIndicator).where(
            TechnicalIndicator.index_name == self.INDEX_NAME
        )
        if start_date is not None:
            stmt = stmt.where(TechnicalIndicator.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(TechnicalIndicator.date <= end_date)
        stmt = stmt.order_by(TechnicalIndicator.date)

        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "date": r.date.isoformat() if r.date else None,
                "rsi_14": float(r.rsi_14) if r.rsi_14 is not None else None,
                "interpretation": self.interpret_rsi(
                    float(r.rsi_14) if r.rsi_14 is not None else None
                ),
            }
            for r in rows
        ]

    async def get_sma_history(
        self,
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        """Return SMA-50 / SMA-200 history within the date range."""
        stmt = select(TechnicalIndicator).where(
            TechnicalIndicator.index_name == self.INDEX_NAME
        )
        if start_date is not None:
            stmt = stmt.where(TechnicalIndicator.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(TechnicalIndicator.date <= end_date)
        stmt = stmt.order_by(TechnicalIndicator.date)

        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "date": r.date.isoformat() if r.date else None,
                "sma_50": float(r.sma_50) if r.sma_50 is not None else None,
                "sma_200": float(r.sma_200) if r.sma_200 is not None else None,
            }
            for r in rows
        ]

    async def get_macd_history(
        self,
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        """Return MACD history within the date range."""
        stmt = select(TechnicalIndicator).where(
            TechnicalIndicator.index_name == self.INDEX_NAME
        )
        if start_date is not None:
            stmt = stmt.where(TechnicalIndicator.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(TechnicalIndicator.date <= end_date)
        stmt = stmt.order_by(TechnicalIndicator.date)

        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "date": r.date.isoformat() if r.date else None,
                "macd": float(r.macd) if r.macd is not None else None,
                "macd_signal": float(r.macd_signal) if r.macd_signal is not None else None,
                "macd_histogram": float(r.macd_histogram) if r.macd_histogram is not None else None,
            }
            for r in rows
        ]


technical_indicator_service = TechnicalIndicatorService()
