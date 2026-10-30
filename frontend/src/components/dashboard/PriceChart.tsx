import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import { PricePoint, TechnicalIndicators } from '../../types';

interface Props {
  prices: PricePoint[];
  technicals?: TechnicalIndicators;
  isLoading?: boolean;
}

const RANGES = [
  { label: '1M', days: 30 },
  { label: '3M', days: 90 },
  { label: '6M', days: 180 },
  { label: '1Y', days: 365 },
  { label: '3Y', days: 1095 },
  { label: '5Y', days: 1825 },
];

export const PriceChart: React.FC<Props> = ({ prices, technicals, isLoading }) => {
  const [selectedRange, setSelectedRange] = useState('1Y');

  if (isLoading || !prices || prices.length === 0) {
    return (
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] h-96 animate-pulse mb-6" />
    );
  }

  // Filter prices according to selected range
  const rangeConfig = RANGES.find((r) => r.label === selectedRange) || RANGES[3];
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - rangeConfig.days);
  const cutoffStr = cutoffDate.toISOString().slice(0, 10);

  const filteredPrices = prices
    .filter((p) => p.date >= cutoffStr)
    .map((p) => ({
      date: p.date,
      close: p.close,
      high: p.high,
      low: p.low,
    }));

  const chartData = filteredPrices.length > 0 ? filteredPrices : prices.slice(-100);

  // Compute domain
  const values = chartData.map((d) => d.close);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const yPadding = (maxVal - minVal) * 0.08 || 500;
  const yDomain = [Math.floor(minVal - yPadding), Math.ceil(maxVal + yPadding)];

  return (
    <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <span>Historical Index Trend & Technical Anchors</span>
          </h3>
          <p className="text-xs text-slate-400">
            Nifty 100 Equal Weight with 50 SMA, 200 SMA & 52-Week Range
          </p>
        </div>

        {/* Range Buttons */}
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-lg border border-[#2a2f45]">
          {RANGES.map((r) => (
            <button
              key={r.label}
              onClick={() => setSelectedRange(r.label)}
              className={`px-2.5 py-1 text-xs font-semibold rounded transition ${
                selectedRange === r.label
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* Legend Indicator */}
      <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mb-3 px-1">
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-0.5 bg-blue-400 inline-block" />
          <span>Index Close</span>
        </div>
        {technicals?.sma_200 && (
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-0.5 bg-emerald-400 border-dashed inline-block" />
            <span>200-Day SMA (₹{technicals.sma_200.toLocaleString('en-IN')})</span>
          </div>
        )}
        {technicals?.sma_50 && (
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-0.5 bg-amber-400 border-dashed inline-block" />
            <span>50-Day SMA (₹{technicals.sma_50.toLocaleString('en-IN')})</span>
          </div>
        )}
        {technicals?.low_52w && (
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-0.5 bg-rose-400 inline-block" />
            <span>52W Low (₹{technicals.low_52w.toLocaleString('en-IN')})</span>
          </div>
        )}
      </div>

      {/* Recharts Canvas */}
      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2438" />
            <XAxis
              dataKey="date"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              tickFormatter={(str) => {
                if (!str) return '';
                const parts = str.split('-');
                return `${parts[2]}/${parts[1]}`;
              }}
            />
            <YAxis
              domain={yDomain}
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              tickFormatter={(v) => `₹${(v / 1000).toFixed(1)}k`}
              orientation="right"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#141828',
                borderColor: '#2a2f45',
                borderRadius: '8px',
                color: '#ffffff',
                fontSize: '12px',
              }}
              formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`, 'Price']}
              labelFormatter={(label) => `Date: ${label}`}
            />

            {/* Price Line */}
            <Line
              type="monotone"
              dataKey="close"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              name="Close Price"
            />

            {/* Technical Reference Lines */}
            {technicals?.sma_200 && (
              <ReferenceLine
                y={technicals.sma_200}
                stroke="#10b981"
                strokeDasharray="4 4"
                label={{
                  value: '200 SMA',
                  fill: '#10b981',
                  fontSize: 10,
                  position: 'insideTopLeft',
                }}
              />
            )}
            {technicals?.low_52w && (
              <ReferenceLine
                y={technicals.low_52w}
                stroke="#f43f5e"
                strokeDasharray="3 3"
                label={{
                  value: '52W Low',
                  fill: '#f43f5e',
                  fontSize: 10,
                  position: 'insideBottomLeft',
                }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

