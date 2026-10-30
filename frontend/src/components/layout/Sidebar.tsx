import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  BarChart3,
  Newspaper,
  Database,
  Sliders,
  BookOpen,
  Settings,
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/technical', label: 'Technical Analysis', icon: TrendingUp },
  { path: '/fundamental', label: 'Fundamental Valuation', icon: BarChart3 },
  { path: '/news', label: 'News Intelligence', icon: Newspaper },
  { path: '/historical', label: 'Historical Data', icon: Database },
  { path: '/backtest', label: 'Strategy Backtest', icon: Sliders },
  { path: '/methodology', label: 'Methodology & Transparency', icon: BookOpen },
  { path: '/settings', label: 'Admin Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="hidden lg:flex flex-col w-64 glass-panel border-r border-[#2a2f45] min-h-[calc(100vh-65px)] p-4">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-bold tracking-wider text-slate-500 uppercase">
          Market Intelligence
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition duration-150 ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
                }`
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      {/* Target Focus Box */}
      <div className="mt-auto pt-6">
        <div className="rounded-lg p-3 bg-slate-900/60 border border-[#2a2f45]">
          <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider mb-1">
            Tracked Instrument
          </div>
          <div className="text-xs font-bold text-white">Nifty 100 Equal Weight</div>
          <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
            Tracks equal 1% weight across top 100 large-caps for balanced market participation.
          </p>
        </div>
      </div>
    </aside>
  );
};

