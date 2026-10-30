import React from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { MobileNav } from './MobileNav';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';

export const Layout: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: overview } = useQuery({
    queryKey: ['marketOverview'],
    queryFn: api.getMarketOverview,
    refetchInterval: 30000, // Refetch every 30s
  });

  const handleRefresh = () => {
    queryClient.invalidateQueries();
  };

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-slate-100 flex flex-col">
      <Header
        isMarketOpen={overview?.is_market_open}
        marketStatusText={overview?.market_status_text}
        observationDate={overview?.observation_date}
        onRefresh={handleRefresh}
      />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-4 md:p-6 lg:p-8 pb-20 lg:pb-8 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
      <MobileNav />
    </div>
  );
};

