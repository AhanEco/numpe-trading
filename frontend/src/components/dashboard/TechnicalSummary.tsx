import React from 'react';
import { TechnicalIndicators } from '../../types';
import { Compass, Target, ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';

interface Props {
  data?: TechnicalIndicators;
  currentPrice?: number | null;
  isLoading?: boolean;
}

export const TechnicalSummary: React.FC<Props> = ({ data, currentPrice, isLoading }) => {
  if (isLoading || !data) {
    return (
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] animate-pulse h-64 mb-6" />
    );
  }

  const rsi = data.rsi_14;
  const rsiZone =
    rsi !== null
      ? rsi < 30
        ? 'Oversold (<30)'
        : rsi <= 42
        ? 'Target Entry Zone (30–42)'
        : rsi < 70
        ? 'Neutral/Positive Momentum (42–70)'
        : 'Overbought (>70)'
      : 'N/A';

  const rsiColor =
    rsi !== null
      ? rsi <= 42
        ? 'text-emerald-400 bg-emerald-950/40 border-emerald-500/30'
        : rsi >= 70
        ? 'text-rose-400 bg-rose-950/40 border-rose-500/30'
        : 'text-blue-400 bg-blue-950/40 border-blue-500/30'
      : 'text-slate-400';

  return (
    <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Compass className="h-4 w-4 text-blue-400" />
            <span>Technical Indicators & Momentum Profile</span>
          </h3>
          <p className="text-xs text-slate-400">
            Wilder's Smoothing RSI, Long-Term Moving Averages & 52-Week Boundaries
          </p>
        </div>
        <span className="text-xs px-2.5 py-1 rounded bg-slate-900 text-slate-300 border border-[#2a2f45]">
          14-Day Session Horizon
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {/* RSI 14 Card */}
        <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>RSI (14) Wilder's</span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${rsiColor}`}>
              {rsiZone}
            </span>
          </div>
          <div className="text-2xl font-black text-white">{rsi?.toFixed(1) ?? 'N/A'}</div>
          <p className="text-[11px] text-slate-400 mt-2">
            Target buy criteria: &lt; 42.0 (Signals oversold momentum exhaustion)
          </p>
        </div>

        {/* 200-day SMA */}
        <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>200-Day SMA</span>
            <span
              className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                (data.distance_from_sma200_pct || 0) >= 0
                  ? 'text-emerald-400 bg-emerald-950/40'
                  : 'text-rose-400 bg-rose-950/40'
              }`}
            >
              {data.distance_from_sma200_pct !== null
                ? `${data.distance_from_sma200_pct >= 0 ? '+' : ''}${data.distance_from_sma200_pct.toFixed(2)}%`
                : 'N/A'}
            </span>
          </div>
          <div className="text-2xl font-black text-white">
            ₹{data.sma_200 ? data.sma_200.toLocaleString('en-IN') : 'N/A'}
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Long-term institutional trendline. Key input for Price Valuation Anchor.
          </p>
        </div>

        {/* 50-day SMA */}
        <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>50-Day SMA</span>
            <span className="text-[10px] text-slate-400">Medium-term</span>
          </div>
          <div className="text-2xl font-black text-white">
            ₹{data.sma_50 ? data.sma_50.toLocaleString('en-IN') : 'N/A'}
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Intermediate cyclical average indicating quarterly trend direction.
          </p>
        </div>

        {/* 52-Week Low */}
        <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>52-Week Low</span>
            <span className="text-[10px] font-bold text-slate-300">
              +{data.distance_from_52w_low_pct?.toFixed(2)}% above low
            </span>
          </div>
          <div className="text-2xl font-black text-white">
            ₹{data.low_52w ? data.low_52w.toLocaleString('en-IN') : 'N/A'}
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Cyclical support floor. Second critical input for Condition 1 price threshold.
          </p>
        </div>

        {/* 52-Week High */}
        <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>52-Week High</span>
            <span className="text-[10px] font-bold text-slate-400">
              {data.distance_from_52w_high_pct !== null
                ? `${data.distance_from_52w_high_pct?.toFixed(2)}% from peak`
                : 'Peak Anchor'}
            </span>
          </div>
          <div className="text-2xl font-black text-white">
            ₹{data.high_52w ? data.high_52w.toLocaleString('en-IN') : 'N/A'}
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Historical 1-year resistance ceiling for the equal-weight basket.
          </p>
        </div>

        {/* MACD Momentum */}
        <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>MACD (12, 26, 9)</span>
            <span
              className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                (data.macd_histogram || 0) >= 0
                  ? 'text-emerald-400 bg-emerald-950/40'
                  : 'text-rose-400 bg-rose-950/40'
              }`}
            >
              {(data.macd_histogram || 0) >= 0 ? 'Bullish Bias' : 'Bearish Bias'}
            </span>
          </div>
          <div className="text-xl font-black text-white">
            MACD: {data.macd?.toFixed(1) ?? 'N/A'}
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Signal Line: {data.macd_signal?.toFixed(1) ?? 'N/A'} | Histogram:{' '}
            {data.macd_histogram?.toFixed(1) ?? 'N/A'}
          </p>
        </div>
      </div>
    </div>
  );
};

