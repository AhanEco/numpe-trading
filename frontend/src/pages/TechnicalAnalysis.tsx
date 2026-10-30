import React, { useState } from 'react';
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
  ReferenceArea,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';
import { TrendingUp, Compass, Activity, Info } from 'lucide-react';

export const TechnicalAnalysis: React.FC = () => {
  const { data: technicals } = useQuery({
    queryKey: ['technicals'],
    queryFn: api.getCurrentTechnicals,
  });

  const { data: rsiData, isLoading: loadingRsi } = useQuery({
    queryKey: ['rsiHistory'],
    queryFn: () => api.getRsiHistory(),
  });

  const { data: macdData, isLoading: loadingMacd } = useQuery({
    queryKey: ['macdHistory'],
    queryFn: () => api.getMacdHistory(),
  });

  const rsiChartData = (rsiData?.data || []).slice(-120);
  const macdChartData = (macdData?.data || []).slice(-120);

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div>
        <h2 className="text-2xl font-black text-white flex items-center space-x-2">
          <TrendingUp className="h-6 w-6 text-blue-400" />
          <span>Technical Momentum & Moving Average Analysis</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Detailed inspection of Wilder's Smoothing RSI (14), 200-Day SMA support anchors, and MACD trend oscillator.
        </p>
      </div>

      {/* RSI Wilder's Chart */}
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <span>Relative Strength Index (RSI 14) – Wilder's Smoothing</span>
            </h3>
            <p className="text-xs text-slate-400">
              Target buy zone highlighted in green (30–42). Values below 30 indicate deep oversold levels.
            </p>
          </div>
          <div className="flex items-center space-x-2 text-xs">
            <span className="font-bold text-white">Current RSI:</span>
            <span className="text-base font-black text-blue-400">
              {technicals?.rsi_14?.toFixed(1) ?? 'N/A'}
            </span>
          </div>
        </div>

        {/* Chart */}
        <div className="w-full h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={rsiChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2438" />
              <XAxis
                dataKey="date"
                stroke="#64748b"
                fontSize={11}
                tickFormatter={(d) => (d ? `${d.split('-')[2]}/${d.split('-')[1]}` : '')}
              />
              <YAxis domain={[0, 100]} ticks={[0, 30, 42, 50, 70, 100]} stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#141828',
                  borderColor: '#2a2f45',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '12px',
                }}
                formatter={(v: any) => [`${Number(v).toFixed(2)}`, 'RSI (14)']}
              />

              {/* Shaded Target Entry Band (30 to 42) */}
              <ReferenceArea
                y1={30}
                y2={42}
                fill="#10b981"
                fillOpacity={0.15}
                label={{ value: 'TARGET ENTRY ZONE (30-42)', fill: '#10b981', fontSize: 10, position: 'insideTopLeft' }}
              />

              {/* Reference Threshold Lines */}
              <ReferenceLine y={70} stroke="#f43f5e" strokeDasharray="3 3" />
              <ReferenceLine y={50} stroke="#64748b" strokeDasharray="2 2" />
              <ReferenceLine y={42} stroke="#10b981" strokeWidth={1.5} />
              <ReferenceLine y={30} stroke="#f59e0b" strokeDasharray="3 3" />

              <Line type="monotone" dataKey="rsi_14" stroke="#60a5fa" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* RSI Zone Explanation */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-4 pt-3 border-t border-[#2a2f45] text-xs">
          <div className="p-2 rounded bg-slate-900/40 border border-slate-800">
            <span className="text-slate-400 block text-[10px] uppercase font-bold">&lt; 30.0</span>
            <span className="text-rose-400 font-bold">Deep Oversold</span>
          </div>
          <div className="p-2 rounded bg-emerald-950/20 border border-emerald-500/30">
            <span className="text-emerald-400 block text-[10px] uppercase font-bold">30.0 – 42.0</span>
            <span className="text-emerald-400 font-bold">Target Entry Zone</span>
          </div>
          <div className="p-2 rounded bg-slate-900/40 border border-slate-800">
            <span className="text-slate-400 block text-[10px] uppercase font-bold">42.0 – 70.0</span>
            <span className="text-slate-300 font-bold">Neutral Momentum</span>
          </div>
          <div className="p-2 rounded bg-rose-950/20 border border-rose-500/30">
            <span className="text-rose-400 block text-[10px] uppercase font-bold">&gt; 70.0</span>
            <span className="text-rose-400 font-bold">Overbought</span>
          </div>
        </div>
      </div>

      {/* MACD Chart */}
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg">
        <h3 className="text-base font-bold text-white mb-2">MACD Histogram & Signal Lines (12, 26, 9)</h3>
        <p className="text-xs text-slate-400 mb-4">
          Visualizes trend velocity and short-term directional momentum shifts.
        </p>

        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={macdChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2438" />
              <XAxis
                dataKey="date"
                stroke="#64748b"
                fontSize={11}
                tickFormatter={(d) => (d ? `${d.split('-')[2]}/${d.split('-')[1]}` : '')}
              />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#141828',
                  borderColor: '#2a2f45',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '12px',
                }}
              />
              <ReferenceLine y={0} stroke="#475569" />
              <Bar dataKey="macd_histogram" fill="#3b82f6" name="Histogram" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

