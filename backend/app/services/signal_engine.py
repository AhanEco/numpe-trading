"""Investment Signal Engine for NUMPE Trading Software.

Evaluates quantitative conditions for Nifty 100 Equal Weight Index:
1. Price Threshold T = 1.10 * [(52W Low + 200-day SMA) / 2]
2. RSI(14) < 42
3. Consolidated P/E < 20
4. P/B ratio within configurable range [2.7, 3.2]

Transparently reports each condition's actual value, target, and pass/fail state.
Never provides automated execution or guaranteed return promises.
"""

from __future__ import annotations

import datetime
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market_data import (
    IndexPrice,
    TechnicalIndicator,
    ValuationMetric,
    InvestmentSignal,
    UserSettings,
)
from app.utils.timezone import today_ist, now_ist

logger = logging.getLogger(__name__)


class SignalEngine:
    INDEX_NAME = "Nifty 100 Equal Weight"

    # Default configurable thresholds
    DEFAULT_SETTINGS = {
        "rsi_threshold": 42.0,
        "pe_threshold": 20.0,
        "pb_lower": 2.7,
        "pb_upper": 3.2,
        "price_interpretation": "below",  # "below" (Price <= T) or "band" (within +/- X% of T)
        "price_band_pct": 2.0,            # +/- 2% band around T if in "band" mode
        "sma_period": 200,
    }

    def calculate_price_threshold(self, low_52w: Optional[float], sma_200: Optional[float]) -> Optional[float]:
        """
        Formula: T = 1.10 * [(52-week low + 200-day SMA) / 2]
        Represents a disciplined 10% premium above the midpoint between long-term trend (200 SMA)
        and 52-week cyclical trough.
        """
        if low_52w is None or sma_200 is None or low_52w <= 0 or sma_200 <= 0:
            return None
        return round(1.10 * ((low_52w + sma_200) / 2.0), 2)

    def evaluate_price_condition(
        self,
        current_price: Optional[float],
        threshold: Optional[float],
        mode: str = "below",
        band_pct: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Evaluate Condition 1 with selectable interpretation:
        - Mode A ("below"): Current price <= Threshold T
        - Mode B ("band"): Current price is within [T * (1 - band_pct/100), T * (1 + band_pct/100)]
        """
        if current_price is None or threshold is None:
            return {
                "name": "Price Valuation Anchor",
                "condition_id": "PRICE_THRESHOLD",
                "met": False,
                "status": "INSUFFICIENT_DATA",
                "actual_value": current_price,
                "target_value": f"<= ₹{threshold:,.2f}" if threshold else "Pending Calculation",
                "mode": mode,
                "explanation": "Insufficient historical data (52-week low or 200-day SMA missing) to compute price anchor.",
            }

        if mode == "band":
            lower_bound = round(threshold * (1.0 - band_pct / 100.0), 2)
            upper_bound = round(threshold * (1.0 + band_pct / 100.0), 2)
            met = lower_bound <= current_price <= upper_bound
            target_str = f"Within ±{band_pct}% band [₹{lower_bound:,.2f} – ₹{upper_bound:,.2f}] of ₹{threshold:,.2f}"
            if met:
                explanation = (
                    f"Current index price (₹{current_price:,.2f}) is hovering within the specified {band_pct}% "
                    f"disciplined accumulation band around ₹{threshold:,.2f}."
                )
            else:
                diff = round(((current_price - threshold) / threshold) * 100.0, 2)
                explanation = (
                    f"Current index price (₹{current_price:,.2f}) is {diff:+.2f}% away from the threshold (₹{threshold:,.2f}), "
                    f"outside the configured ±{band_pct}% accumulation band."
                )
        else:
            # Mode "below"
            met = current_price <= threshold
            target_str = f"Price ≤ ₹{threshold:,.2f} (T = 1.10 × [(52W Low + 200 SMA) / 2])"
            diff = round(((current_price - threshold) / threshold) * 100.0, 2)
            if met:
                explanation = (
                    f"Current index price (₹{current_price:,.2f}) is {abs(diff):.2f}% below the threshold (₹{threshold:,.2f}), "
                    f"satisfying the price valuation condition."
                )
            else:
                explanation = (
                    f"Current index price (₹{current_price:,.2f}) is {diff:.2f}% above the threshold anchor (₹{threshold:,.2f}). "
                    f"Price condition is currently not satisfied."
                )

        return {
            "name": "Price Valuation Anchor",
            "condition_id": "PRICE_THRESHOLD",
            "met": met,
            "status": "SATISFIED" if met else "NOT_SATISFIED",
            "actual_value": current_price,
            "target_value": target_str,
            "threshold_value": threshold,
            "mode": mode,
            "explanation": explanation,
        }

    def evaluate_rsi_condition(self, rsi: Optional[float], threshold: float = 42.0) -> Dict[str, Any]:
        """
        Evaluate Condition 2: RSI(14) < 42.
        Signals weak momentum / oversold sentiment suitable for systematic entry.
        """
        if rsi is None:
            return {
                "name": "RSI (14) Momentum",
                "condition_id": "RSI_14",
                "met": False,
                "status": "INSUFFICIENT_DATA",
                "actual_value": None,
                "target_value": f"< {threshold:.1f}",
                "explanation": "RSI (14) observation currently unavailable.",
            }

        met = rsi < threshold
        if met:
            explanation = (
                f"RSI is {rsi:.1f} (below {threshold:.1f}). This indicates weak momentum / oversold market sentiment, "
                f"aligning with the entry criteria."
            )
        else:
            explanation = (
                f"RSI is {rsi:.1f} (above {threshold:.1f}). Market momentum is not currently in the specified "
                f"cool-down/oversold entry zone."
            )

        return {
            "name": "RSI (14) Momentum",
            "condition_id": "RSI_14",
            "met": met,
            "status": "SATISFIED" if met else "NOT_SATISFIED",
            "actual_value": round(rsi, 2),
            "target_value": f"< {threshold:.1f}",
            "explanation": explanation,
        }

    def evaluate_pe_condition(self, pe: Optional[float], threshold: float = 20.0) -> Dict[str, Any]:
        """
        Evaluate Condition 3: Consolidated P/E < 20.
        Signals attractive fundamental price-to-earnings valuation.
        """
        if pe is None:
            return {
                "name": "Consolidated P/E Ratio",
                "condition_id": "CONSOLIDATED_PE",
                "met": False,
                "status": "INSUFFICIENT_DATA",
                "actual_value": None,
                "target_value": f"< {threshold:.1f}",
                "explanation": "Consolidated P/E ratio observation currently unavailable.",
            }

        met = pe < threshold
        if met:
            explanation = (
                f"Consolidated P/E is {pe:.2f} (below {threshold:.1f}). The index valuation is trading at an attractive "
                f"earnings multiple relative to historical averages."
            )
        else:
            explanation = (
                f"Consolidated P/E is {pe:.2f} (above threshold of {threshold:.1f}). Valuation is currently above "
                f"the conservative entry criteria."
            )

        return {
            "name": "Consolidated P/E Ratio",
            "condition_id": "CONSOLIDATED_PE",
            "met": met,
            "status": "SATISFIED" if met else "NOT_SATISFIED",
            "actual_value": round(pe, 2),
            "target_value": f"< {threshold:.1f}",
            "explanation": explanation,
        }

    def evaluate_pb_condition(
        self,
        pb: Optional[float],
        lower: float = 2.7,
        upper: float = 3.2,
    ) -> Dict[str, Any]:
        """
        Evaluate Condition 4: P/B approximately 3 (configurable range [lower, upper]).
        Note: Clearly marked as an experimental assumption requiring investor confirmation.
        """
        if pb is None:
            return {
                "name": "Price-to-Book (P/B) Ratio",
                "condition_id": "PB_RATIO",
                "met": False,
                "status": "INSUFFICIENT_DATA",
                "actual_value": None,
                "target_value": f"{lower:.1f} – {upper:.1f} (Approx 3.0)",
                "explanation": "P/B ratio observation currently unavailable.",
            }

        met = lower <= pb <= upper
        if met:
            explanation = (
                f"Index P/B is {pb:.2f}, sitting within the experimental range [{lower:.1f} – {upper:.1f}]. "
                f"Book value backing aligns with target expectations."
            )
        elif pb < lower:
            explanation = (
                f"Index P/B is {pb:.2f} (below {lower:.1f}), which represents very deep value or potential market distress."
            )
        else:
            explanation = (
                f"Index P/B is {pb:.2f} (above {upper:.1f}), exceeding the target band of approximately 3.0."
            )

        return {
            "name": "Price-to-Book (P/B) Ratio",
            "condition_id": "PB_RATIO",
            "met": met,
            "status": "SATISFIED" if met else "NOT_SATISFIED",
            "actual_value": round(pb, 2),
            "target_value": f"{lower:.1f} – {upper:.1f} (Experimental Range)",
            "explanation": explanation,
            "is_experimental": True,
        }

    def derive_market_assessment(
        self,
        cond_met: int,
        cond_total: int,
        rsi_met: bool,
        pe_met: bool,
        has_sufficient_data: bool,
    ) -> str:
        """Derive a qualitative descriptive market assessment."""
        if not has_sufficient_data:
            return "Insufficient Evidence"
        if cond_met == 4:
            return "Potentially Attractive Valuation"
        if rsi_met and not pe_met:
            return "Weak Market Momentum (Valuation Elevated)"
        if not rsi_met and pe_met:
            return "Attractive Valuation (Momentum Strong)"
        if not rsi_met and not pe_met:
            return "Expensive Relative Valuation"
        return "Mixed Market Signals"

    async def get_effective_settings(self, db: AsyncSession) -> Dict[str, Any]:
        """Fetch configured thresholds or return defaults."""
        stmt = select(UserSettings).where(UserSettings.key == "signal_settings")
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if record and isinstance(record.value, dict):
            settings = self.DEFAULT_SETTINGS.copy()
            settings.update(record.value)
            return settings
        return self.DEFAULT_SETTINGS.copy()

    async def compute_current_signal(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Evaluate all conditions against latest market data and return structured signal response.
        """
        settings = await self.get_effective_settings(db)

        # 1. Fetch latest price
        stmt_p = (
            select(IndexPrice)
            .where(IndexPrice.index_name == self.INDEX_NAME)
            .order_by(desc(IndexPrice.date))
            .limit(1)
        )
        price_rec = (await db.execute(stmt_p)).scalar_one_or_none()

        # 2. Fetch latest technicals
        stmt_t = (
            select(TechnicalIndicator)
            .where(TechnicalIndicator.index_name == self.INDEX_NAME)
            .order_by(desc(TechnicalIndicator.date))
            .limit(1)
        )
        tech_rec = (await db.execute(stmt_t)).scalar_one_or_none()

        # 3. Fetch latest valuation
        stmt_v = (
            select(ValuationMetric)
            .where(ValuationMetric.index_name == self.INDEX_NAME)
            .order_by(desc(ValuationMetric.date))
            .limit(1)
        )
        val_rec = (await db.execute(stmt_v)).scalar_one_or_none()

        current_price = float(price_rec.close) if price_rec and price_rec.close else None
        low_52w = float(tech_rec.low_52w) if tech_rec and tech_rec.low_52w else None
        sma_200 = float(tech_rec.sma_200) if tech_rec and tech_rec.sma_200 else None
        rsi = float(tech_rec.rsi_14) if tech_rec and tech_rec.rsi_14 else None
        pe = float(val_rec.pe_ratio) if val_rec and val_rec.pe_ratio else None
        pb = float(val_rec.pb_ratio) if val_rec and val_rec.pb_ratio else None

        obs_date = (
            price_rec.date
            if price_rec
            else (tech_rec.date if tech_rec else today_ist())
        )

        threshold = self.calculate_price_threshold(low_52w, sma_200)

        # Evaluate each condition
        c1 = self.evaluate_price_condition(
            current_price,
            threshold,
            mode=settings.get("price_interpretation", "below"),
            band_pct=float(settings.get("price_band_pct", 2.0)),
        )
        c2 = self.evaluate_rsi_condition(rsi, threshold=float(settings.get("rsi_threshold", 42.0)))
        c3 = self.evaluate_pe_condition(pe, threshold=float(settings.get("pe_threshold", 20.0)))
        c4 = self.evaluate_pb_condition(
            pb,
            lower=float(settings.get("pb_lower", 2.7)),
            upper=float(settings.get("pb_upper", 3.2)),
        )

        conditions = [c1, c2, c3, c4]
        has_sufficient = all(
            c["status"] != "INSUFFICIENT_DATA" for c in conditions
        )

        cond_met_count = sum(1 for c in conditions if c.get("met") is True)

        if not has_sufficient and cond_met_count == 0:
            category = "INSUFFICIENT DATA"
        elif cond_met_count == 4:
            category = "ALL CONDITIONS SATISFIED"
        elif cond_met_count == 3:
            category = "THREE CONDITIONS SATISFIED"
        elif cond_met_count == 2:
            category = "TWO CONDITIONS SATISFIED"
        elif cond_met_count == 1:
            category = "ONE CONDITION SATISFIED"
        else:
            category = "NO CONDITIONS SATISFIED"

        market_assessment = self.derive_market_assessment(
            cond_met_count,
            4,
            c2.get("met", False),
            c3.get("met", False),
            has_sufficient,
        )

        # Build readable summary description for display
        if cond_met_count == 4:
            summary = (
                "All 4 systematic investment conditions are currently satisfied. "
                "Valuation, price anchor, RSI momentum, and P/B are all within pre-defined target zones."
            )
        elif cond_met_count >= 2:
            satisfied_names = [c["name"] for c in conditions if c["met"]]
            pending_names = [c["name"] for c in conditions if not c["met"]]
            summary = (
                f"{cond_met_count} out of 4 conditions are currently met ({', '.join(satisfied_names)}). "
                f"Remaining conditions under observation: {', '.join(pending_names)}."
            )
        else:
            summary = (
                "Current market conditions do not currently meet the multi-factor investment entry threshold. "
                "Disciplined monitoring continues."
            )

        signal_payload = {
            "date": obs_date.isoformat(),
            "index_name": self.INDEX_NAME,
            "conditions_met_count": cond_met_count,
            "total_conditions": 4,
            "signal_category": category,
            "market_assessment": market_assessment,
            "summary": summary,
            "current_price": current_price,
            "price_threshold": threshold,
            "current_rsi": rsi,
            "rsi_threshold": float(settings.get("rsi_threshold", 42.0)),
            "current_pe": pe,
            "pe_threshold": float(settings.get("pe_threshold", 20.0)),
            "current_pb": pb,
            "pb_lower": float(settings.get("pb_lower", 2.7)),
            "pb_upper": float(settings.get("pb_upper", 3.2)),
            "sma_200": sma_200,
            "low_52w": low_52w,
            "conditions": conditions,
            "disclaimer": (
                "This monitoring signal is strictly an algorithmic indicator evaluation tool for personal research. "
                "It does NOT constitute investment advice or a guarantee of profitability. Never invest without considering "
                "your personal risk tolerance and financial situation."
            ),
        }

        return signal_payload


signal_engine = SignalEngine()

