import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import { Scale, Landmark, ShieldCheck, HelpCircle } from 'lucide-react';

export const FundamentalAnalysis: React.FC = () => {
  const { data: valData } = useQuery({
    queryKey: ['valuation'],
    queryFn: api.getCurrentValuation,
  });

  const { data: historyData } = useQuery({
    queryKey: ['valHistory'],
    queryFn: () => api.getValuationHistory(),
  });

  const chartData = (historyData?.data || []).map((d) => ({
    date: d.date,
    pe_ratio: d.pe_ratio,
    pb_ratio: d.pb_ratio,
  }));

  const benchmarks = valData?.benchmarks || {
    pe_median_5y: 21.4,
    pb_median_5y: 3.1,
    ind_10y_gsec_yield: 6.85,
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-black text-white flex items-center space-x-2">
          <Scale className="h-6 w-6 text-amber-400" />
          <span>Fundamental Valuation & Earnings Yield Dashboard</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Tracking official Consolidated P/E, P/B multiples, and risk premium relative to Indian 10-Year G-Sec yields.
        </p>
      </div>

      {/* Main 3 Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel rounded-xl p-5 border border-[#2a2f45]">
          <span className="text-xs text-slate-400 font-semibold uppercase">Consolidated P/E</span>
          <div className="text-3xl font-black text-white mt-1">
            {valData?.pe_ratio?.toFixed(2) ?? 'N/A'}
          </div>
          <div className="mt-2 text-xs text-slate-400 flex items-center justify-between">
            <span>5Y Historical Median:</span>
            <span className="font-bold text-white">{benchmarks.pe_median_5y}</span>
          </div>
          <div className="mt-1 text-xs text-slate-400 flex items-center justify-between">
            <span>Target Threshold:</span>
            <span className="font-bold text-emerald-400">&lt; 20.0</span>
          </div>
        </div>

        <div className="glass-panel rounded-xl p-5 border border-[#2a2f45]">
          <span className="text-xs text-slate-400 font-semibold uppercase">Price-to-Book (P/B)</span>
          <div className="text-3xl font-black text-white mt-1">
            {valData?.pb_ratio?.toFixed(2) ?? 'N/A'}
          </div>
          <div className="mt-2 text-xs text-slate-400 flex items-center justify-between">
            <span>5Y Historical Median:</span>
            <span className="font-bold text-white">{benchmarks.pb_median_5y}</span>
          </div>
          <div className="mt-1 text-xs text-slate-400 flex items-center justify-between">
            <span>Target Range:</span>
            <span className="font-bold text-emerald-400">2.7 – 3.2</span>
          </div>
        </div>

        <div className="glass-panel rounded-xl p-5 border border-[#2a2f45]">
          <span className="text-xs text-slate-400 font-semibold uppercase">Earnings Yield</span>
          <div className="text-3xl font-black text-white mt-1">
            {valData?.earnings_yield?.toFixed(2)}%
          </div>
          <div className="mt-2 text-xs text-slate-400 flex items-center justify-between">
            <span>Indian 10-Yr G-Sec:</span>
            <span className="font-bold text-white">{benchmarks.ind_10y_gsec_yield}%</span>
          </div>
          <div className="mt-1 text-xs text-slate-400 flex items-center justify-between">
            <span>Equity Yield Spread:</span>
            <span className="font-bold text-slate-300">
              {valData?.earnings_yield
                ? `${(valData.earnings_yield - benchmarks.ind_10y_gsec_yield).toFixed(2)}%`
                : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* P/E Trend Chart */}
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-base font-bold text-white">Consolidated P/E Valuation History</h3>
            <p className="text-xs text-slate-400">
              Green line represents the systematic investment condition threshold (P/E &lt; 20.0).
            </p>
          </div>
        </div>

        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData.length > 0 ? chartData : [{ date: valData?.date || 'Today', pe_ratio: valData?.pe_ratio || 21.2, pb_ratio: valData?.pb_ratio || 3.1 }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2438" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
              <YAxis domain={[12, 30]} stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#141828',
                  borderColor: '#2a2f45',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '12px',
                }}
              />
              <ReferenceLine y={20.0} stroke="#10b981" strokeWidth={1.5} label={{ value: 'BUY THRESHOLD (PE < 20)', fill: '#10b981', fontSize: 10 }} />
              <ReferenceLine y={benchmarks.pe_median_5y} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: '5Y Median (21.4)', fill: '#f59e0b', fontSize: 10 }} />
              <Line type="monotone" dataKey="pe_ratio" stroke="#3b82f6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Methodology Note */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-[#2a2f45] text-xs text-slate-300 space-y-2">
        <div className="flex items-center space-x-1.5 font-bold text-white">
          <HelpCircle className="h-4 w-4 text-blue-400" />
          <span>Understanding Nifty 100 Equal Weight Valuation Ratios:</span>
        </div>
        <p className="leading-relaxed">
          Unlike market-cap weighted indices which can be heavily skewed by top 5 mega-cap companies,
          the Nifty 100 Equal Weight Index provides true median exposure across Indian large-caps.
          Our system monitors the official consolidated trailing P/E published by NSE Indices rather than synthetic company arithmetic averages.
        </p>
      </div>
    </div>
  );
};
