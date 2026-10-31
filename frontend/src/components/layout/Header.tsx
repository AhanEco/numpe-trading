import React, { useState } from 'react';
import { RefreshCw, Activity, ShieldCheck, Clock } from 'lucide-react';
import { api } from '../../services/api';

interface HeaderProps {
  isMarketOpen?: boolean;
  marketStatusText?: string;
  observationDate?: string | null;
  onRefresh?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isMarketOpen = false,
  marketStatusText = 'Market Closed',
  observationDate,
  onRefresh,
}) => {
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState<string | null>(null);

  const handleSync = async () => {
    try {
      setIsSyncing(true);
      setSyncMsg('Syncing data...');
      const res = await api.triggerSync();
      setSyncMsg(res.message);
      if (onRefresh) onRefresh();
      setTimeout(() => setSyncMsg(null), 4000);
    } catch {
      setSyncMsg('Sync failed');
      setTimeout(() => setSyncMsg(null), 3000);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-[#2a2f45] px-4 py-3 md:px-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Brand identity */}
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-800 text-white font-bold text-xl shadow-lg shadow-blue-900/30">
            N
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-extrabold tracking-wider text-white">Numpecraft</h1>
              <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800">
                PRO
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Nifty 100 Equal Weight Investment Intelligence
            </p>
          </div>
        </div>

        {/* Live status indicators & Action buttons */}
        <div className="flex flex-wrap items-center gap-2 md:gap-4 text-xs">
          {/* Market Status Badge */}
          <div
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full border ${
              isMarketOpen
                ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-400'
                : 'bg-slate-900/80 border-slate-700 text-slate-400'
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                isMarketOpen ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'
              }`}
            />
            <span className="font-medium">{marketStatusText}</span>
          </div>

          {/* Observation Date */}
          {observationDate && (
            <div className="hidden sm:flex items-center space-x-1 text-slate-400 bg-slate-900/40 px-2.5 py-1 rounded border border-[#2a2f45]">
              <Clock className="h-3.5 w-3.5 text-slate-400" />
              <span>Data As Of: {observationDate}</span>
            </div>
          )}

          {/* Sync status msg */}
          {syncMsg && (
            <span className="text-blue-400 animate-pulse font-medium">{syncMsg}</span>
          )}

          {/* Manual Refresh / Pipeline trigger */}
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className="flex items-center space-x-1.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 px-3 py-1.5 rounded-md transition duration-150 disabled:opacity-50"
            title="Fetch latest market closing data and refresh analysis"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
            <span>{isSyncing ? 'Updating…' : 'Sync Pipeline'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};

