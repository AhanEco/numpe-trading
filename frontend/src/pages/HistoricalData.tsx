import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Database, Download, Calendar, ArrowUpDown } from 'lucide-react';

export const HistoricalData: React.FC = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { data: pricesData, isLoading } = useQuery({
    queryKey: ['historicalPrices', startDate, endDate],
    queryFn: () => api.getPrices(startDate || undefined, endDate || undefined),
  });

  const rows = pricesData?.data || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white flex items-center space-x-2">
            <Database className="h-6 w-6 text-blue-400" />
            <span>Nifty 100 Equal Weight Historical Records</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Audit and inspect genuine daily OHLCV closing observations with full source traceability.
          </p>
        </div>

        {/* CSV Export Button */}
        <a
          href={api.exportPricesCsvUrl()}
          download
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-lg transition self-start sm:self-auto"
        >
          <Download className="h-4 w-4" />
          <span>Export CSV</span>
        </a>
      </div>

      {/* Date Filter Bar */}
      <div className="glass-panel rounded-xl p-4 border border-[#2a2f45] flex flex-wrap items-center gap-4 text-xs">
        <div className="flex items-center space-x-2">
          <Calendar className="h-4 w-4 text-slate-400" />
          <span className="text-slate-300 font-semibold">From:</span>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="bg-slate-900 border border-[#2a2f45] rounded px-2.5 py-1 text-white"
          />
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-slate-300 font-semibold">To:</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="bg-slate-900 border border-[#2a2f45] rounded px-2.5 py-1 text-white"
          />
        </div>

        {(startDate || endDate) && (
          <button
            onClick={() => {
              setStartDate('');
              setEndDate('');
            }}
            className="text-blue-400 hover:underline"
          >
            Clear Filter
          </button>
        )}

        <div className="ml-auto text-slate-400 font-medium">
          Showing {rows.length} recorded trading sessions
        </div>
      </div>

      {/* Table */}
      <div className="glass-panel rounded-xl border border-[#2a2f45] overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-[#2a2f45] uppercase font-semibold">
              <tr>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Open (₹)</th>
                <th className="py-3 px-4">High (₹)</th>
                <th className="py-3 px-4">Low (₹)</th>
                <th className="py-3 px-4 text-white">Close (₹)</th>
                <th className="py-3 px-4">Volume</th>
                <th className="py-3 px-4">Data Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f2438] text-slate-300 font-mono">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400 font-sans">
                    Loading historical index observations...
                  </td>
                </tr>
              ) : rows.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400 font-sans">
                    No records found for the selected period.
                  </td>
                </tr>
              ) : (
                rows.slice().reverse().map((r, i) => (
                  <tr key={i} className="hover:bg-slate-800/40 transition">
                    <td className="py-2.5 px-4 font-sans text-slate-300">{r.date}</td>
                    <td className="py-2.5 px-4">{r.open?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td className="py-2.5 px-4 text-emerald-400">{r.high?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td className="py-2.5 px-4 text-rose-400">{r.low?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td className="py-2.5 px-4 font-bold text-white">{r.close?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td className="py-2.5 px-4 text-slate-400">{r.volume?.toLocaleString('en-IN')}</td>
                    <td className="py-2.5 px-4 font-sans text-slate-400 text-[11px] truncate max-w-xs">{r.source}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

