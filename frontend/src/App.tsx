import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { TechnicalAnalysis } from './pages/TechnicalAnalysis';
import { FundamentalAnalysis } from './pages/FundamentalAnalysis';
import { NewsIntelligence } from './pages/NewsIntelligence';
import { HistoricalData } from './pages/HistoricalData';
import { StrategyBacktesting } from './pages/StrategyBacktesting';
import { Methodology } from './pages/Methodology';
import { Settings } from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      retry: 2,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="technical" element={<TechnicalAnalysis />} />
            <Route path="fundamental" element={<FundamentalAnalysis />} />
            <Route path="news" element={<NewsIntelligence />} />
            <Route path="historical" element={<HistoricalData />} />
            <Route path="backtest" element={<StrategyBacktesting />} />
            <Route path="methodology" element={<Methodology />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;

