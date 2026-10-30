import React from 'react';
import { BookOpen, Calculator, Scale, TrendingUp, Newspaper, ShieldAlert, Check } from 'lucide-react';

export const Methodology: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-black text-white flex items-center space-x-2">
          <BookOpen className="h-6 w-6 text-blue-400" />
          <span>Quantitative Methodology & Analytical Transparency</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Complete mathematical formulations, data integrity protocols, and investment logic documentation.
        </p>
      </div>

      {/* 1. Condition 1: Price Threshold Formula */}
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg space-y-3">
        <div className="flex items-center space-x-2 text-white font-bold text-base">
          <Calculator className="h-5 w-5 text-blue-400" />
          <span>1. Price Valuation Anchor Threshold (Condition 1)</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          The price anchor establishes a disciplined, systematic upper boundary for entering the Nifty 100 Equal Weight Index.
          It anchors the entry price to the midpoint between the prevailing long-term moving trend (200-day SMA) and the 52-week cyclical floor,
          with a conservative 10% premium.
        </p>
        <div className="p-3.5 rounded-lg bg-black/40 border border-white/5 font-mono text-sm text-blue-300">
          T = 1.10 × [(52-week low + 200-day SMA) / 2]
        </div>
        <div className="space-y-2 text-xs text-slate-300">
          <div className="font-semibold text-white">Selectable Interpretations:</div>
          <ul className="list-disc list-inside space-y-1 text-slate-400">
            <li>
              <strong className="text-slate-200">Mode A (Current Price is Below Threshold):</strong> Condition is satisfied if <code className="text-blue-300">Current Price ≤ T</code>.
            </li>
            <li>
              <strong className="text-slate-200">Mode B (Configurable Percentage Band):</strong> Condition is satisfied if the index price hovers within a defined percentage band (e.g., ±2%) around threshold T.
            </li>
          </ul>
        </div>
      </div>

      {/* 2. Condition 2: Relative Strength Index (RSI 14) */}
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg space-y-3">
        <div className="flex items-center space-x-2 text-white font-bold text-base">
          <TrendingUp className="h-5 w-5 text-indigo-400" />
          <span>2. RSI (14) using Wilder's Exponential Smoothing (Condition 2)</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          The Relative Strength Index measures the magnitude of recent price changes to evaluate overbought or oversold market conditions.
          Wilder's smoothing utilizes an exponential moving average with <code className="text-blue-300">α = 1 / 14</code>:
        </p>
        <div className="p-3.5 rounded-lg bg-black/40 border border-white/5 font-mono text-xs text-indigo-300 space-y-1">
          <div>RSI = 100 - [100 / (1 + RS)]</div>
          <div>RS = Average Gain / Average Loss (Wilder's 14-session EWMA)</div>
        </div>
        <div className="text-xs text-slate-300 space-y-1">
          <div className="font-semibold text-white">Threshold Interpretation:</div>
          <p className="text-slate-400">
            • <strong className="text-emerald-400">RSI &lt; 42:</strong> Indicates weak momentum and market consolidation, satisfying the disciplined entry zone.<br />
            • <strong className="text-rose-400">RSI &gt; 70:</strong> Traditionally overbought momentum.<br />
            • Note: An RSI below 42 is an indicator of momentum exhaustion, never a standalone guarantee of upward price movement.
          </p>
        </div>
      </div>

      {/* 3. Fundamental Valuation: Consolidated P/E & P/B */}
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg space-y-3">
        <div className="flex items-center space-x-2 text-white font-bold text-base">
          <Scale className="h-5 w-5 text-amber-400" />
          <span>3. Consolidated P/E Ratio & P/B Multiples (Conditions 3 & 4)</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Valuation is tracked using the official Nifty 100 Equal Weight consolidated index methodology published by NSE Indices.
        </p>
        <div className="p-3.5 rounded-lg bg-black/40 border border-white/5 text-xs text-amber-200/90 space-y-1">
          <div>• <strong>Consolidated P/E Target:</strong> &lt; 20.0 (Condition 3)</div>
          <div>• <strong>Price-to-Book Target:</strong> 2.7 – 3.2 (Condition 4, experimental assumption)</div>
          <div>• <strong>Earnings Yield:</strong> (1 / P/E) × 100</div>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          <strong>Important Methodology Note:</strong> The index P/E is <em>never</em> calculated by taking a simple arithmetic mean of constituent P/Es,
          as that introduces severe mathematical distortion from outlier multiple constituents. It follows the aggregate constituent market capitalization divided by consolidated net profit methodology.
        </p>
      </div>

      {/* 4. NLP News Intelligence */}
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg space-y-3">
        <div className="flex items-center space-x-2 text-white font-bold text-base">
          <Newspaper className="h-5 w-5 text-emerald-400" />
          <span>4. NLP Financial News Intelligence Engine</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          The natural language pipeline ingests authorized RSS feeds from leading financial newsrooms (Economic Times, Livemint, Business Standard).
        </p>
        <ul className="list-disc list-inside space-y-1 text-xs text-slate-400">
          <li><strong>Deduplication:</strong> Cryptographic SHA-256 canonical hashing prevents redundant alerts.</li>
          <li><strong>17 Financial Categories:</strong> Classifies articles into RBI monetary policy, FII/DII institutional flows, inflation, corporate earnings, crude oil, and rupee trajectory.</li>
          <li><strong>Financial Sentiment Lexicon:</strong> Distinguishes market-specific terminology (e.g., rate cut as supportive, FPI outflow as liquidity pressure).</li>
        </ul>
      </div>

      {/* Regulatory & Advisory Disclaimer */}
      <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 text-xs text-amber-200/90 flex items-start space-x-3">
        <ShieldAlert className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-amber-300 uppercase tracking-wider">
            Important Compliance & Investor Transparency Notice
          </div>
          <p className="leading-relaxed">
            NUMPE Trading Software is a personal quantitative monitoring tool created strictly for informational and analytical assistance.
            No signal or indicator calculation constitutes a guaranteed prediction, financial advice, or an automated trading execution.
            All investments in Indian equities and index funds carry market risk.
          </p>
        </div>
      </div>
    </div>
  );
};

