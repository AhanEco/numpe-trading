import React from 'react';
import { MarketOverview as MarketOverviewType } from '../../types';
import { TrendingUp, TrendingDown, HelpCircle, Activity, Scale, Percent } from 'lucide-react';

interface Props {
  data?: MarketOverviewType;
  isLoading?: boolean;
}

export const MarketOverview: React.FC<Props> = ({ data, isLoading }) => {
  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="glass-card rounded-xl p-5 animate-pulse h-32" />
        ))}
      </div>
    );
  }

  const isPositive = (data.daily_change || 0) >= 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* 1. Index Price */}
      <div className="glass-card rounded-xl p-5 border border-[#2a2f45] hover:border-blue-500/40 transition">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Index Level</span>
          <Activity className="h-4 w-4 text-blue-400" />
        </div>
        <div className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
          ₹{data.current_price?.toLocaleString('en-IN', { minimumFractionDigits: 2 }) ?? 'N/A'}
        </div>
        <p className="text-[11px] text-slate-400 mt-2 flex items-center justify-between">
          <span>{data.index_name}</span>
          <span className="text-slate-500">{data.data_quality}</span>
        </p>
      </div>

      {/* 2. Daily Change */}
      <div className="glass-card rounded-xl p-5 border border-[#2a2f45] hover:border-blue-500/40 transition">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Daily Movement</span>
          {isPositive ? (
            <TrendingUp className="h-4 w-4 text-emerald-400" />
          ) : (
            <TrendingDown className="h-4 w-4 text-rose-400" />
          )}
        </div>
        <div
          className={`text-2xl lg:text-3xl font-extrabold tracking-tight ${
            isPositive ? 'text-emerald-400' : 'text-rose-400'
          }`}
        >
          {isPositive ? '+' : ''}
          {data.daily_change_pct?.toFixed(2)}%
        </div>
        <p className="text-[11px] text-slate-400 mt-2">
          {isPositive ? '+' : ''}
          ₹{data.daily_change?.toFixed(2)} vs previous close (₹
          {data.previous_close?.toLocaleString('en-IN')})
        </p>
      </div>

      {/* 3. Consolidated P/E */}
      <div className="glass-card rounded-xl p-5 border border-[#2a2f45] hover:border-blue-500/40 transition">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Consolidated P/E</span>
          <Scale className="h-4 w-4 text-amber-400" />
        </div>
        <div className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
          {data.pe_ratio ? data.pe_ratio.toFixed(2) : 'N/A'}
        </div>
        <p className="text-[11px] mt-2">
          {data.pe_ratio && data.pe_ratio < 20 ? (
            <span className="text-emerald-400 font-medium">✓ Below target threshold of 20</span>
          ) : (
            <span className="text-slate-400">Target entry threshold: &lt; 20.0</span>
          )}
        </p>
      </div>

      {/* 4. RSI (14) */}
      <div className="glass-card rounded-xl p-5 border border-[#2a2f45] hover:border-blue-500/40 transition">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">RSI (14) Wilder's</span>
          <Percent className="h-4 w-4 text-indigo-400" />
        </div>
        <div className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
          {data.rsi_14 ? data.rsi_14.toFixed(1) : 'N/A'}
        </div>
        <p className="text-[11px] mt-2 truncate text-slate-400" title={data.rsi_interpretation}>
          {data.rsi_interpretation || 'Target entry zone: < 42.0'}
        </p>
      </div>
    </div>
  );
};

