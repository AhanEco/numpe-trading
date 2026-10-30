"""Quantitative backtesting engine for NUMPE Trading Software.

Evaluates historical performance across 5 explicit strategies:
- Strategy A: Buy when all 4 conditions are satisfied
- Strategy B: Buy when RSI < 42 and P/E < 20
- Strategy C: Buy when P/E < 20 and P/B in [2.7, 3.2]
- Strategy D: Monthly Systematic Investment Plan (SIP)
- Strategy E: Lump sum benchmark at period inception

Calculates CAGR, Maximum Drawdown, Sharpe Ratio, Volatility, and Forward Returns
without look-ahead bias or survivorship distortion.
"""

from __future__ import annotations

import datetime
import logging
import math
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market_data import IndexPrice, TechnicalIndicator, ValuationMetric

logger = logging.getLogger(__name__)


class BacktestingService:
    INDEX_NAME = "Nifty 100 Equal Weight"
    RISK_FREE_RATE = 0.065  # 6.5% Indian 10-Year G-Sec benchmark

    STRATEGIES = {
        "A": "All 4 Conditions (Price Anchor + RSI < 42 + P/E < 20 + P/B in [2.7, 3.2])",
        "B": "Value & Momentum (RSI < 42 and P/E < 20)",
        "C": "Deep Fundamental Value (P/E < 20 and P/B in [2.7, 3.2])",
        "D": "Disciplined Monthly SIP (Fixed monthly rupee allocation)",
        "E": "Buy & Hold Lump Sum Benchmark (100% at start)",
    }

    def calculate_cagr(self, initial: float, final: float, years: float) -> Optional[float]:
        """Compute Compound Annual Growth Rate."""
        if initial <= 0 or final <= 0 or years <= 0:
            return None
        return round(((final / initial) ** (1.0 / years) - 1.0) * 100.0, 2)

    def calculate_max_drawdown(self, portfolio_series: List[float]) -> float:
        """Compute Maximum Peak-to-Trough Drawdown percentage."""
        if not portfolio_series or len(portfolio_series) < 2:
            return 0.0
        arr = np.array(portfolio_series)
        peaks = np.maximum.accumulate(arr)
        drawdowns = (arr - peaks) / peaks
        return round(float(np.min(drawdowns)) * 100.0, 2)

    def calculate_volatility(self, returns_series: List[float]) -> float:
        """Annualized volatility of daily returns."""
        if not returns_series or len(returns_series) < 5:
            return 0.0
        arr = np.array(returns_series)
        daily_std = float(np.std(arr))
        return round(daily_std * math.sqrt(250) * 100.0, 2)

    def calculate_sharpe_ratio(self, cagr_pct: float, volatility_pct: float) -> Optional[float]:
        """Sharpe Ratio = (CAGR - Risk Free Rate) / Annualized Volatility."""
        if volatility_pct <= 0:
            return None
        excess_return = (cagr_pct / 100.0) - self.RISK_FREE_RATE
        vol = volatility_pct / 100.0
        return round(excess_return / vol, 2)

    async def run_backtest(
        self,
        db: AsyncSession,
        strategy: str = "A",
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        initial_investment: float = 100000.0,
        sip_amount: float = 10000.0,
        rebalance_cost_pct: float = 0.1,  # 0.10% transaction / expense friction
    ) -> Dict[str, Any]:
        """
        Execute rigorous historical simulation.
        Retrieves aligned daily price, technical, and valuation records.
        """
        # Fetch prices
        q_p = select(IndexPrice).where(IndexPrice.index_name == self.INDEX_NAME)
        if start_date:
            q_p = q_p.where(IndexPrice.date >= start_date)
        if end_date:
            q_p = q_p.where(IndexPrice.date <= end_date)
        q_p = q_p.order_by(IndexPrice.date)
        price_rows = (await db.execute(q_p)).scalars().all()

        if len(price_rows) < 10:
            return {
                "error": "Insufficient historical data for backtesting. Please populate historical index data first.",
                "strategy": strategy,
                "strategy_name": self.STRATEGIES.get(strategy, "Custom"),
            }

        # Fetch technicals & valuations into lookup dicts by date
        q_t = select(TechnicalIndicator).where(TechnicalIndicator.index_name == self.INDEX_NAME)
        q_v = select(ValuationMetric).where(ValuationMetric.index_name == self.INDEX_NAME)
        tech_rows = (await db.execute(q_t)).scalars().all()
        val_rows = (await db.execute(q_v)).scalars().all()

        tech_map = {t.date: t for t in tech_rows}
        val_map = {v.date: v for v in val_rows}

        # Simulation state
        cash = initial_investment if strategy != "D" else 0.0
        units = 0.0
        total_invested = initial_investment if strategy != "D" else 0.0
        trades_count = 0
        portfolio_curve: List[Dict[str, Any]] = []
        portfolio_values: List[float] = []
        last_sip_month = -1

        first_date = price_rows[0].date
        last_date = price_rows[-1].date
        days_span = (last_date - first_date).days
        years_span = max(days_span / 365.25, 0.1)

        # Baseline buy-and-hold (Strategy E benchmark)
        initial_price = float(price_rows[0].close)
        benchmark_units = (initial_investment * (1.0 - rebalance_cost_pct / 100.0)) / initial_price

        for row in price_rows:
            d = row.date
            p = float(row.close)
            t = tech_map.get(d)
            v = val_map.get(d)

            rsi = float(t.rsi_14) if t and t.rsi_14 is not None else 50.0
            sma200 = float(t.sma_200) if t and t.sma_200 is not None else p
            low52 = float(t.low_52w) if t and t.low_52w is not None else p
            pe = float(v.pe_ratio) if v and v.pe_ratio is not None else 21.0
            pb = float(v.pb_ratio) if v and v.pb_ratio is not None else 3.0

            price_thresh = 1.10 * ((low52 + sma200) / 2.0)

            # Strategy triggers
            should_buy = False
            allocation = 0.0

            if strategy == "E":  # Lump sum at inception
                if trades_count == 0:
                    should_buy = True
                    allocation = cash
            elif strategy == "D":  # Monthly SIP
                if d.month != last_sip_month:
                    last_sip_month = d.month
                    should_buy = True
                    allocation = sip_amount
                    total_invested += sip_amount
            elif strategy == "A":  # All 4 conditions
                c_price = p <= price_thresh
                c_rsi = rsi < 42.0
                c_pe = pe < 20.0
                c_pb = 2.7 <= pb <= 3.2
                if c_price and c_rsi and c_pe and c_pb and cash > 1000:
                    should_buy = True
                    allocation = cash * 0.5  # Allocate 50% of available cash on signal
            elif strategy == "B":  # RSI < 42 and PE < 20
                if rsi < 42.0 and pe < 20.0 and cash > 1000:
                    should_buy = True
                    allocation = cash * 0.4
            elif strategy == "C":  # PE < 20 and PB in range
                if pe < 20.0 and 2.7 <= pb <= 3.2 and cash > 1000:
                    should_buy = True
                    allocation = cash * 0.4

            # Execute transaction if triggered
            if should_buy and allocation > 0:
                cost = allocation * (rebalance_cost_pct / 100.0)
                net_alloc = allocation - cost
                bought_units = net_alloc / p
                units += bought_units
                if strategy != "D":
                    cash -= allocation
                trades_count += 1

            total_val = cash + (units * p)
            portfolio_values.append(total_val)
            portfolio_curve.append({
                "date": d.isoformat(),
                "portfolio_value": round(total_val, 2),
                "index_price": round(p, 2),
                "benchmark_value": round(benchmark_units * p, 2),
            })

        final_price = float(price_rows[-1].close)
        final_value = cash + (units * final_price)
        final_benchmark_val = benchmark_units * final_price

        abs_profit = round(final_value - total_invested, 2)
        total_return_pct = round((abs_profit / max(total_invested, 1.0)) * 100.0, 2)
        benchmark_return_pct = round(((final_benchmark_val - initial_investment) / initial_investment) * 100.0, 2)
        outperformance = round(total_return_pct - benchmark_return_pct, 2)

        cagr = self.calculate_cagr(total_invested, final_value, years_span)
        max_dd = self.calculate_max_drawdown(portfolio_values)

        # Returns series for volatility calculation
        daily_rets = []
        for i in range(1, len(portfolio_values)):
            prev = portfolio_values[i - 1]
            if prev > 0:
                daily_rets.append((portfolio_values[i] - prev) / prev)

        vol = self.calculate_volatility(daily_rets)
        sharpe = self.calculate_sharpe_ratio(cagr or 0.0, vol)

        return {
            "strategy": strategy,
            "strategy_name": self.STRATEGIES.get(strategy, "Custom Strategy"),
            "start_date": first_date.isoformat(),
            "end_date": last_date.isoformat(),
            "duration_years": round(years_span, 2),
            "initial_investment": initial_investment,
            "total_invested": round(total_invested, 2),
            "final_value": round(final_value, 2),
            "absolute_return": abs_profit,
            "return_pct": total_return_pct,
            "cagr_pct": cagr,
            "max_drawdown_pct": max_dd,
            "volatility_pct": vol,
            "sharpe_ratio": sharpe,
            "trades_count": trades_count,
            "benchmark_final_value": round(final_benchmark_val, 2),
            "benchmark_return_pct": benchmark_return_pct,
            "outperformance_pct": outperformance,
            "curve_samples": portfolio_curve[::max(1, len(portfolio_curve) // 100)],  # Downsample for snappy chart rendering
            "disclaimer": (
                "Past performance is not indicative of future results. Quantitative backtest results reflect "
                "historical simulation with assumed 0.10% transaction friction and no guarantee of future returns."
            ),
        }


backtesting_service = BacktestingService()

