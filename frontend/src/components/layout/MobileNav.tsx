import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  BarChart3,
  Newspaper,
  Sliders,
  Settings,
} from 'lucide-react';

const MOBILE_NAV_ITEMS = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/technical', label: 'Technical', icon: TrendingUp },
  { path: '/fundamental', label: 'Valuation', icon: BarChart3 },
  { path: '/news', label: 'News', icon: Newspaper },
  { path: '/backtest', label: 'Backtest', icon: Sliders },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export const MobileNav: React.FC = () => {
  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-50 glass-panel border-t border-[#2a2f45] px-2 py-1.5 safe-area-pb">
      <div className="flex items-center justify-around">
        {MOBILE_NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex flex-col items-center py-1 px-2 rounded text-[10px] font-medium transition ${
                  isActive ? 'text-blue-400 font-bold' : 'text-slate-400 hover:text-slate-200'
                }`
              }
            >
              <Icon className="h-4 w-4 mb-0.5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
};

