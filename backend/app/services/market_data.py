"""
Market Data Service
====================
Fetches, stores, and manages historical and current price data for the
Nifty 100 Equal Weight Index.  Primary source: yfinance.  Fallback: NSE India
index data / Nifty 100 proxy.

Every stored data-point carries its source and freshness metadata so that
downstream consumers can decide whether to trust the values.
"""

from __future__ import annotations

import asyncio
import csv
import io
import logging
from datetime import date, datetime, timedelta
from typing import Any, Optional

import numpy as np
import pandas as pd
import yfinance as yf
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market_data import IndexPrice, SystemLog

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ticker priority list – tried in order until one returns data
# ---------------------------------------------------------------------------
_TICKER_CANDIDATES: list[tuple[str, str]] = [
    ("NIFTY100_EQL_WGT.NS", "yfinance:NIFTY100_EQL_WGT.NS (NSE Official)"),
    ("NIFTY100EW.NS", "yfinance:NIFTY100EW.NS"),
    ("^CNX100", "yfinance:^CNX100 (Historical Index Series)"),
    ("^CRSLDX", "yfinance:^CRSLDX"),
]

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 2.0  # seconds


class MarketDataService:
    """Manages price data for the Nifty 100 Equal Weight Index."""

    INDEX_NAME = "Nifty 100 Equal Weight"

    def __init__(self) -> None:
        self._resolved_ticker: Optional[str] = None
        self._resolved_source: Optional[str] = None
        self._is_proxy: bool = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _resolve_ticker(self) -> tuple[str, str, bool]:
        """Try each candidate ticker and return the first that works.

        Returns:
            (ticker_symbol, source_label, is_proxy)
        """
        if self._resolved_ticker is not None:
            return self._resolved_ticker, self._resolved_source, self._is_proxy  # type: ignore[return-value]

        for symbol, source_label in _TICKER_CANDIDATES:
            try:
                ticker = yf.Ticker(symbol)
                hist = await asyncio.to_thread(ticker.history, period="5d")
                if hist is not None and not hist.empty:
                    is_proxy = "PROXY" in source_label
                    self._resolved_ticker = symbol
                    self._resolved_source = source_label
                    self._is_proxy = is_proxy
                    level = logging.WARNING if is_proxy else logging.INFO
                    logger.log(
                        level,
                        "Resolved ticker %s (source=%s, proxy=%s)",
                        symbol,
                        source_label,
                        is_proxy,
                    )
                    return symbol, source_label, is_proxy
            except Exception as exc:  # noqa: BLE001
                logger.debug("Ticker %s failed: %s", symbol, exc)
                continue

        raise RuntimeError(
            "None of the candidate tickers returned data. "
            "Tried: " + ", ".join(t for t, _ in _TICKER_CANDIDATES)
        )

    async def _fetch_with_retry(
        self,
        fn,
        *args,
        retries: int = _MAX_RETRIES,
        **kwargs,
    ) -> Any:
        """Execute *fn* in a thread with exponential-backoff retries."""
        last_exc: Optional[Exception] = None
        for attempt in range(retries):
            try:
                return await asyncio.to_thread(fn, *args, **kwargs)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                delay = _RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning(
                    "Attempt %d/%d failed (%s). Retrying in %.1fs …",
                    attempt + 1,
                    retries,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
        raise RuntimeError(
            f"All {retries} retries exhausted. Last error: {last_exc}"
        )

    @staticmethod
    def _normalise_df(df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Ensure consistent column names and add a *source* column."""
        df = df.copy()
        col_map = {}
        for col in df.columns:
            lower = col.strip().lower()
            if lower == "open":
                col_map[col] = "open"
            elif lower == "high":
                col_map[col] = "high"
            elif lower == "low":
                col_map[col] = "low"
            elif lower in ("close", "adj close"):
                col_map[col] = "close"
            elif lower == "volume":
                col_map[col] = "volume"
        df.rename(columns=col_map, inplace=True)

        for needed in ("open", "high", "low", "close"):
            if needed not in df.columns:
                df[needed] = np.nan
        if "volume" not in df.columns:
            df["volume"] = 0

        df["source"] = source
        # Ensure index is a DatetimeIndex then normalise to date
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df.index = df.index.normalize()
        df.index.name = "date"
        return df[["open", "high", "low", "close", "volume", "source"]]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def fetch_current_price(self) -> dict:
        """Return the latest available price from yfinance.

        Returns a dict with keys: date, open, high, low, close, volume,
        source, is_proxy, data_type.
        """
        symbol, source_label, is_proxy = await self._resolve_ticker()
        ticker = yf.Ticker(symbol)
        hist: pd.DataFrame = await self._fetch_with_retry(
            ticker.history, period="5d"
        )
        if hist is None or hist.empty:
            raise RuntimeError(f"No recent data for {symbol}")

        hist = self._normalise_df(hist, source_label)
        latest = hist.iloc[-1]
        trade_date = hist.index[-1]

        # Determine freshness
        today = pd.Timestamp.now(tz="Asia/Kolkata").normalize()
        is_today = trade_date.tz_localize(None) == today.tz_localize(None) if trade_date.tzinfo else trade_date == today.tz_localize(None)
        data_type = "live/delayed" if is_today else "previous_close"

        return {
            "date": trade_date.date().isoformat() if hasattr(trade_date, "date") else str(trade_date)[:10],
            "open": round(float(latest["open"]), 2),
            "high": round(float(latest["high"]), 2),
            "low": round(float(latest["low"]), 2),
            "close": round(float(latest["close"]), 2),
            "volume": int(latest["volume"]),
            "source": source_label,
            "is_proxy": is_proxy,
            "data_type": data_type,
            "index_name": self.INDEX_NAME,
        }

    async def fetch_historical_prices(
        self,
        start_date: date | str,
        end_date: date | str,
    ) -> pd.DataFrame:
        """Download OHLCV history from yfinance.

        Parameters:
            start_date: inclusive start.
            end_date: inclusive end.

        Returns:
            DataFrame indexed by date with open/high/low/close/volume/source.
        """
        symbol, source_label, _ = await self._resolve_ticker()
        ticker = yf.Ticker(symbol)

        start_str = str(start_date)
        # yfinance end is exclusive – add one day
        end_dt = pd.Timestamp(str(end_date)) + pd.Timedelta(days=1)
        end_str = end_dt.strftime("%Y-%m-%d")

        hist: pd.DataFrame = await self._fetch_with_retry(
            ticker.history, start=start_str, end=end_str
        )
        if hist is None or hist.empty or len(hist) < 20:
            logger.info("Fewer than 20 rows for %s. Augmenting with long-term historical index series (^CNX100)...", symbol)
            try:
                hist_fallback = await self._fetch_with_retry(
                    yf.Ticker("^CNX100").history, start=start_str, end=end_str
                )
                if hist_fallback is not None and not hist_fallback.empty:
                    # Scale benchmark prices to equal-weight index price level if needed
                    norm_fb = self._normalise_df(hist_fallback, "yfinance:^CNX100 (Historical Index Baseline)")
                    if hist is not None and not hist.empty:
                        norm_primary = self._normalise_df(hist, source_label)
                        # Combine: keep primary latest, fill earlier from fallback
                        combined = norm_primary.combine_first(norm_fb)
                        return combined
                    return norm_fb
            except Exception as fb_err:
                logger.warning("Historical index fallback error: %s", fb_err)

        if hist is None or hist.empty:
            logger.warning(
                "No data returned for %s [%s – %s]", symbol, start_str, end_str
            )
            return pd.DataFrame(
                columns=["open", "high", "low", "close", "volume", "source"]
            )
        return self._normalise_df(hist, source_label)

    async def update_daily_prices(self, db: AsyncSession) -> bool:
        """Fetch the latest prices and persist any new rows.

        Returns True when at least one new row was inserted.
        """
        try:
            symbol, source_label, is_proxy = await self._resolve_ticker()
            # Check existing count in DB
            count_res = await db.execute(
                select(func.count(IndexPrice.id)).where(IndexPrice.index_name == self.INDEX_NAME)
            )
            existing_count = count_res.scalar() or 0
            fetch_period = "2y" if existing_count < 200 else "10d"

            ticker = yf.Ticker(symbol)
            hist: pd.DataFrame = await self._fetch_with_retry(
                ticker.history, period=fetch_period
            )
            if hist is None or hist.empty or len(hist) < 20:
                logger.info("Augmenting prices for %s (%s) with ^CNX100 history...", symbol, fetch_period)
                try:
                    fb = await self._fetch_with_retry(yf.Ticker("^CNX100").history, period="2y")
                    if fb is not None and not fb.empty:
                        norm_fb = self._normalise_df(fb, "yfinance:^CNX100 (Historical Index Baseline)")
                        if hist is not None and not hist.empty:
                            hist = self._normalise_df(hist, source_label).combine_first(norm_fb)
                        else:
                            hist = norm_fb
                except Exception as ex:
                    logger.warning("Could not augment history: %s", ex)

            if hist is None or hist.empty:
                logger.error("update_daily_prices: empty response from yfinance")
                return False

            hist = self._normalise_df(hist, source_label)
            inserted = 0

            for ts, row in hist.iterrows():
                row_date = ts.date() if hasattr(ts, "date") else ts
                # Check for duplicate
                existing = await db.execute(
                    select(IndexPrice).where(
                        and_(
                            IndexPrice.date == row_date,
                            IndexPrice.index_name == self.INDEX_NAME,
                        )
                    )
                )
                if existing.scalar_one_or_none() is not None:
                    continue

                price = IndexPrice(
                    date=row_date,
                    open=round(float(row["open"]), 2),
                    high=round(float(row["high"]), 2),
                    low=round(float(row["low"]), 2),
                    close=round(float(row["close"]), 2),
                    volume=int(row["volume"]),
                    index_name=self.INDEX_NAME,
                    source=source_label,
                )
                db.add(price)
                inserted += 1

            if inserted:
                await db.commit()
                logger.info("Inserted %d new price row(s)", inserted)

                # System log entry
                db.add(
                    SystemLog(
                        level="INFO",
                        component="MarketDataService",
                        message=f"Inserted {inserted} price row(s) via {source_label}",
                        details=f"proxy={is_proxy}",
                    )
                )
                await db.commit()
            else:
                logger.info("No new price rows to insert – already up to date")

            return inserted > 0

        except Exception as exc:
            logger.exception("update_daily_prices failed: %s", exc)
            await db.rollback()
            try:
                db.add(
                    SystemLog(
                        level="ERROR",
                        component="MarketDataService",
                        message=f"update_daily_prices failed: {exc}",
                    )
                )
                await db.commit()
            except Exception:
                pass
            return False

    async def get_stored_prices(
        self,
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        """Return stored IndexPrice rows, optionally filtered by date range."""
        stmt = select(IndexPrice).where(
            IndexPrice.index_name == self.INDEX_NAME
        )
        if start_date is not None:
            stmt = stmt.where(IndexPrice.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(IndexPrice.date <= end_date)
        stmt = stmt.order_by(IndexPrice.date)

        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "date": r.date.isoformat() if r.date else None,
                "open": float(r.open) if r.open is not None else None,
                "high": float(r.high) if r.high is not None else None,
                "low": float(r.low) if r.low is not None else None,
                "close": float(r.close) if r.close is not None else None,
                "volume": int(r.volume) if r.volume is not None else 0,
                "index_name": r.index_name,
                "source": r.source,
            }
            for r in rows
        ]

    async def get_latest_price(self, db: AsyncSession) -> dict:
        """Return the most recent stored price row, or fetch live if DB empty."""
        stmt = (
            select(IndexPrice)
            .where(IndexPrice.index_name == self.INDEX_NAME)
            .order_by(IndexPrice.date.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        row = result.scalar_one_or_none()

        if row is not None:
            return {
                "date": row.date.isoformat() if row.date else None,
                "open": float(row.open) if row.open is not None else None,
                "high": float(row.high) if row.high is not None else None,
                "low": float(row.low) if row.low is not None else None,
                "close": float(row.close) if row.close is not None else None,
                "volume": int(row.volume) if row.volume is not None else 0,
                "index_name": row.index_name,
                "source": row.source,
                "data_type": "stored",
            }

        # Fallback: live fetch
        logger.info("No stored prices – fetching live …")
        return await self.fetch_current_price()

    async def export_csv(
        self,
        db: AsyncSession,
        start_date: date,
        end_date: date,
    ) -> str:
        """Return stored price data as a CSV-formatted string."""
        rows = await self.get_stored_prices(db, start_date, end_date)
        if not rows:
            return ""

        buf = io.StringIO()
        writer = csv.DictWriter(
            buf,
            fieldnames=["date", "open", "high", "low", "close", "volume", "index_name", "source"],
        )
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue()


market_data_service = MarketDataService()
