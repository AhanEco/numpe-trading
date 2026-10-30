import React from 'react';
import { ValuationMetrics } from '../../types';
import { Scale, PieChart, Landmark, ArrowRight, ShieldCheck } from 'lucide-react';

interface Props {
  data?: ValuationMetrics;
  isLoading?: boolean;
}

export const FundamentalSummary: React.FC<Props> = ({ data, isLoading }) => {
  if (isLoading || !data) {
    return (
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] animate-pulse h-64 mb-6" />
    );
  }

  const pe = data.pe_ratio;
  const pb = data.pb_ratio;
  const ey = data.earnings_yield;
  const gsecYield = data.benchmarks?.ind_10y_gsec_yield || 6.85;

  const yieldSpread = ey !== null && ey !== undefined ? (ey - gsecYield).toFixed(2) : null;

  return (
    <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Scale className="h-4 w-4 text-amber-400" />
            <span>Fundamental Valuation & Historical Percentiles</span>
          </h3>
          <p className="text-xs text-slate-400">
            Consolidated P/E, P/B Multiples & Earnings Yield vs Indian 10-Year G-Sec
          </p>
        </div>
        <span className="text-xs px-2.5 py-1 rounded bg-slate-900 text-slate-300 border border-[#2a2f45]">
          {data.pe_type || 'Consolidated Trailing'}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* P/E Ratio Card */}
        <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Consolidated P/E</span>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                pe && pe < 20
                  ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-500/30'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              {pe && pe < 20 ? 'Target Satisfied (<20)' : 'Above Target (≥20)'}
            </span>
          </div>
          <div className="text-3xl font-black text-white">{pe?.toFixed(2) ?? 'N/A'}</div>

          {/* Percentile Bar */}
          <div className="mt-3">
            <div className="flex justify-between text-[11px] text-slate-400 mb-1">
              <span>5-Year Percentile Rank</span>
              <span className="font-bold text-white">{data.pe_percentile?.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, Math.max(0, data.pe_percentile || 50))}%` }}
              />
            </div>
            <div className="flex justify-between text-[9px] text-slate-500 mt-0.5">
              <span>Cheap (0%)</span>
              <span>Median: {data.pe_5y_avg?.toFixed(1) || '21.4'}</span>
              <span>Expensive (100%)</span>
            </div>
          </div>
        </div>

        {/* P/B Ratio Card */}
        <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Price-to-Book (P/B)</span>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                pb && pb >= 2.7 && pb <= 3.2
                  ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-500/30'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              Target: 2.7 – 3.2
            </span>
          </div>
          <div className="text-3xl font-black text-white">{pb?.toFixed(2) ?? 'N/A'}</div>

          {/* Percentile Bar */}
          <div className="mt-3">
            <div className="flex justify-between text-[11px] text-slate-400 mb-1">
              <span>5-Year Percentile Rank</span>
              <span className="font-bold text-white">{data.pb_percentile?.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, Math.max(0, data.pb_percentile || 50))}%` }}
              />
            </div>
            <div className="flex justify-between text-[9px] text-slate-500 mt-0.5">
              <span>Value (0%)</span>
              <span>Median: {data.pb_5y_avg?.toFixed(1) || '3.1'}</span>
              <span>Premium (100%)</span>
            </div>
          </div>
        </div>

        {/* Earnings Yield vs Bond Yield Card */}
        <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Equity Yield vs 10Y G-Sec</span>
            <Landmark className="h-4 w-4 text-blue-400" />
          </div>
          <div className="text-3xl font-black text-white">
            {ey?.toFixed(2)}%
            <span className="text-xs font-normal text-slate-400 ml-1.5">Earnings Yield</span>
          </div>

          <div className="mt-3 space-y-1.5 text-xs text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-400">Indian 10-Yr G-Sec:</span>
              <span className="font-mono font-bold text-white">{gsecYield}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Equity Risk Premium Spread:</span>
              <span
                className={`font-mono font-bold ${
                  Number(yieldSpread) >= 0 ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {yieldSpread ? `${Number(yieldSpread) >= 0 ? '+' : ''}${yieldSpread}%` : 'N/A'}
              </span>
            </div>
            <p className="text-[10px] text-slate-400 pt-1 leading-tight">
              Higher equity yield relative to risk-free bonds historically favors long-term equity allocation.
            </p>
          </div>
        </div>
      </div>

      <div className="text-[11px] text-slate-400 flex flex-col sm:flex-row sm:items-center justify-between border-t border-[#2a2f45] pt-2.5">
        <span>Data Source: {data.source}</span>
        <span>Never calculates simple arithmetic company averages; follows official index methodology.</span>
      </div>
    </div>
  );
};

