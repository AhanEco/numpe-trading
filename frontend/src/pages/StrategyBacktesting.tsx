import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../services/api';
import { BacktestResult } from '../types';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { Sliders, Play, TrendingUp, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const StrategyBacktesting: React.FC = () => {
  const [strategy, setStrategy] = useState('A');
  const [initialAmount, setInitialAmount] = useState(100000);
  const [sipAmount, setSipAmount] = useState(10000);
  const [costPct, setCostPct] = useState(0.1);

  const { data: strategies } = useQuery({
    queryKey: ['strategies'],
    queryFn: api.getStrategies,
  });

  const backtestMutation = useMutation({
    mutationFn: (params: any) => api.runBacktest(params),
  });

  const handleRun = () => {
    backtestMutation.mutate({
      strategy,
      initial_investment: initialAmount,
      sip_amount: sipAmount,
      rebalance_cost_pct: costPct,
    });
  };

  const result: BacktestResult | undefined = backtestMutation.data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-black text-white flex items-center space-x-2">
          <Sliders className="h-6 w-6 text-blue-400" />
          <span>Quantitative Strategy Backtesting Engine</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Simulate how the multi-factor investment rules would have performed historically on genuine index observations.
        </p>
      </div>

      {/* Control Configuration Form */}
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg">
        <h3 className="text-sm font-bold text-white mb-3">Backtest Parameters</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          {/* Strategy selector */}
          <div>
            <label className="text-slate-400 font-semibold block mb-1">Select Investment Strategy:</label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-medium"
            >
              {(strategies || []).map((s) => (
                <option key={s.code} value={s.code}>
                  Strategy {s.code}: {s.name}
                </option>
              ))}
            </select>
          </div>

          {/* Initial Capital */}
          <div>
            <label className="text-slate-400 font-semibold block mb-1">Initial Capital (₹):</label>
            <input
              type="number"
              value={initialAmount}
              onChange={(e) => setInitialAmount(Number(e.target.value))}
              className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-mono"
            />
          </div>

          {/* Monthly SIP (if Strategy D) */}
          <div>
            <label className="text-slate-400 font-semibold block mb-1">Monthly SIP (₹):</label>
            <input
              type="number"
              value={sipAmount}
              onChange={(e) => setSipAmount(Number(e.target.value))}
              disabled={strategy !== 'D'}
              className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-mono disabled:opacity-40"
            />
          </div>

          {/* Friction / Cost % */}
          <div>
            <label className="text-slate-400 font-semibold block mb-1">Expense / Transaction Friction (%):</label>
            <input
              type="number"
              step="0.05"
              value={costPct}
              onChange={(e) => setCostPct(Number(e.target.value))}
              className="w-full bg-slate-900 border border-[#2a2f45] rounded-lg p-2 text-white font-mono"
            />
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={backtestMutation.isPending}
          className="mt-4 flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs px-6 py-2.5 rounded-lg shadow-lg transition duration-150 disabled:opacity-50"
        >
          <Play className="h-4 w-4 fill-white" />
          <span>{backtestMutation.isPending ? 'Simulating Strategy...' : 'Execute Backtest'}</span>
        </button>
      </div>

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Total Invested</span>
              <div className="text-lg font-black text-white mt-1">
                ₹{result.total_invested?.toLocaleString('en-IN')}
              </div>
            </div>

            <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Final Portfolio Value</span>
              <div className="text-lg font-black text-emerald-400 mt-1">
                ₹{result.final_value?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
              </div>
            </div>

            <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Total Return</span>
              <div
                className={`text-lg font-black mt-1 ${
                  result.return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {result.return_pct >= 0 ? '+' : ''}
                {result.return_pct}%
              </div>
            </div>

            <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">CAGR</span>
              <div className="text-lg font-black text-white mt-1">
                {result.cagr_pct !== null ? `${result.cagr_pct}%` : 'N/A'}
              </div>
            </div>

            <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Max Drawdown</span>
              <div className="text-lg font-black text-rose-400 mt-1">
                {result.max_drawdown_pct}%
              </div>
            </div>

            <div className="glass-card rounded-xl p-4 border border-[#2a2f45]">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Sharpe Ratio</span>
              <div className="text-lg font-black text-blue-400 mt-1">
                {result.sharpe_ratio ?? 'N/A'}
              </div>
            </div>
          </div>

          {/* Equity Growth Curve */}
          <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg">
            <h3 className="text-base font-bold text-white mb-1">
              Portfolio Growth Curve vs Benchmark ({result.start_date} to {result.end_date})
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Comparing {result.strategy_name} against Lump Sum Buy-and-Hold
            </p>

            <div className="w-full h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={result.curve_samples} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2438" />
                  <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#141828',
                      borderColor: '#2a2f45',
                      borderRadius: '8px',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                    formatter={(v: any) => [`₹${Number(v).toLocaleString('en-IN')}`, '']}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="portfolio_value"
                    stroke="#10b981"
                    strokeWidth={2}
                    dot={false}
                    name="Strategy Portfolio (₹)"
                  />
                  <Line
                    type="monotone"
                    dataKey="benchmark_value"
                    stroke="#64748b"
                    strokeDasharray="4 4"
                    strokeWidth={1.5}
                    dot={false}
                    name="Benchmark Lump Sum (₹)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="flex items-center space-x-2 text-xs text-slate-400 p-3 rounded-lg bg-slate-900/60 border border-[#2a2f45]">
            <ShieldAlert className="h-4 w-4 text-amber-400 shrink-0" />
            <span>{result.disclaimer}</span>
          </div>
        </div>
      )}
    </div>
  );
};

