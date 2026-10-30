import React from 'react';
import { InvestmentSignal as InvestmentSignalType } from '../../types';
import { CheckCircle2, XCircle, AlertCircle, ShieldAlert, Info } from 'lucide-react';

interface Props {
  signal?: InvestmentSignalType;
  isLoading?: boolean;
}

export const InvestmentSignal: React.FC<Props> = ({ signal, isLoading }) => {
  if (isLoading || !signal) {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-[#2a2f45] mb-6 animate-pulse h-64" />
    );
  }

  const metCount = signal.conditions_met_count;
  const isAllMet = metCount === 4;
  const isPartial = metCount >= 2 && metCount < 4;

  const badgeColor = isAllMet
    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
    : isPartial
    ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
    : 'bg-rose-500/20 text-rose-400 border-rose-500/40';

  return (
    <div className="glass-panel rounded-2xl p-6 border border-[#2a2f45] shadow-xl mb-6 relative overflow-hidden">
      {/* Background ambient glow */}
      <div
        className={`absolute -top-24 -right-24 w-72 h-72 rounded-full blur-3xl opacity-20 pointer-events-none ${
          isAllMet ? 'bg-emerald-500' : isPartial ? 'bg-amber-500' : 'bg-blue-600'
        }`}
      />

      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-[#2a2f45] gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase tracking-widest text-blue-400">
              Quantitative Strategy Engine
            </span>
            <span className="text-slate-500">•</span>
            <span className="text-xs text-slate-400">As of {signal.date}</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight mt-1">
            NUMPE INVESTMENT MONITOR
          </h2>
        </div>

        {/* Big Status Badge */}
        <div className={`flex flex-col items-start sm:items-end px-4 py-2 rounded-xl border ${badgeColor}`}>
          <span className="text-xs font-bold uppercase tracking-wider">
            {signal.signal_category}
          </span>
          <span className="text-xl sm:text-2xl font-black">
            {metCount} OF {signal.total_conditions} CONDITIONS MET
          </span>
        </div>
      </div>

      {/* Market Assessment & Plain English Narrative */}
      <div className="my-5 p-4 rounded-xl bg-slate-900/60 border border-[#2a2f45]">
        <div className="flex items-start space-x-3">
          <Info className="h-5 w-5 text-blue-400 shrink-0 mt-0.5" />
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Market Condition Assessment:
              </span>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
                {signal.market_assessment}
              </span>
            </div>
            <p className="text-sm text-slate-300 mt-1.5 leading-relaxed">
              {signal.summary}
            </p>
          </div>
        </div>
      </div>

      {/* 4 Conditions Detailed Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 mb-5">
        {signal.conditions.map((c, index) => {
          const isSatisfied = c.met;
          const isInsufficient = c.status === 'INSUFFICIENT_DATA';

          return (
            <div
              key={c.condition_id || index}
              className={`p-4 rounded-xl border transition ${
                isSatisfied
                  ? 'bg-emerald-950/20 border-emerald-500/30'
                  : isInsufficient
                  ? 'bg-slate-900/40 border-slate-700'
                  : 'bg-rose-950/20 border-rose-500/30'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {isSatisfied ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
                  ) : isInsufficient ? (
                    <AlertCircle className="h-5 w-5 text-slate-400 shrink-0" />
                  ) : (
                    <XCircle className="h-5 w-5 text-rose-400 shrink-0" />
                  )}
                  <h3 className="text-sm font-bold text-white">
                    Condition {index + 1}: {c.name}
                  </h3>
                </div>
                <span
                  className={`text-[11px] font-bold px-2 py-0.5 rounded ${
                    isSatisfied
                      ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700'
                      : isInsufficient
                      ? 'bg-slate-800 text-slate-400 border border-slate-700'
                      : 'bg-rose-900/50 text-rose-300 border border-rose-700'
                  }`}
                >
                  {isSatisfied ? 'SATISFIED' : isInsufficient ? 'PENDING' : 'NOT MET'}
                </span>
              </div>

              {/* Numerical comparison row */}
              <div className="grid grid-cols-2 gap-2 text-xs py-2 px-3 rounded-lg bg-black/30 border border-white/5 mb-2">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                    Current Observation
                  </span>
                  <span className="font-mono font-bold text-white text-sm">
                    {c.actual_value !== null ? (
                      typeof c.actual_value === 'number' && c.actual_value > 1000 ? (
                        `₹${c.actual_value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
                      ) : (
                        c.actual_value
                      )
                    ) : (
                      'N/A'
                    )}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                    Target Criteria
                  </span>
                  <span className="font-mono font-medium text-slate-300 text-xs">
                    {c.target_value}
                  </span>
                </div>
              </div>

              {/* Human-friendly explanation */}
              <p className="text-xs text-slate-300 leading-relaxed">{c.explanation}</p>
            </div>
          );
        })}
      </div>

      {/* Disciplined Investing Disclaimer */}
      <div className="flex items-center space-x-2 text-[11px] text-slate-400 pt-3 border-t border-[#2a2f45]">
        <ShieldAlert className="h-4 w-4 text-amber-400 shrink-0" />
        <p className="leading-tight">{signal.disclaimer}</p>
      </div>
    </div>
  );
};

