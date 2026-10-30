import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { MarketOverview } from '../components/dashboard/MarketOverview';
import { InvestmentSignal } from '../components/dashboard/InvestmentSignal';
import { PriceChart } from '../components/dashboard/PriceChart';
import { TechnicalSummary } from '../components/dashboard/TechnicalSummary';
import { FundamentalSummary } from '../components/dashboard/FundamentalSummary';
import { NewsSummary } from '../components/dashboard/NewsSummary';
import { DailyBriefingSummary } from '../components/dashboard/DailyBriefingSummary';

export const Dashboard: React.FC = () => {
  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ['marketOverview'],
    queryFn: api.getMarketOverview,
  });

  const { data: signal, isLoading: loadingSignal } = useQuery({
    queryKey: ['currentSignal'],
    queryFn: api.getCurrentSignal,
  });

  const { data: pricesData, isLoading: loadingPrices } = useQuery({
    queryKey: ['prices'],
    queryFn: () => api.getPrices(),
  });

  const { data: technicals, isLoading: loadingTechnicals } = useQuery({
    queryKey: ['technicals'],
    queryFn: api.getCurrentTechnicals,
  });

  const { data: valuation, isLoading: loadingValuation } = useQuery({
    queryKey: ['valuation'],
    queryFn: api.getCurrentValuation,
  });

  const { data: newsData, isLoading: loadingNews } = useQuery({
    queryKey: ['latestNews'],
    queryFn: () => api.getLatestNews(6),
  });

  const { data: briefing, isLoading: loadingBriefing } = useQuery({
    queryKey: ['dailyBriefing'],
    queryFn: api.getDailyBriefing,
  });

  return (
    <div className="space-y-6">
      {/* 1. Market Overview 4 Cards */}
      <MarketOverview data={overview} isLoading={loadingOverview} />

      {/* 2. THE HERO: Investment Signal Monitor */}
      <InvestmentSignal signal={signal} isLoading={loadingSignal} />

      {/* 3. Interactive Price Chart with 50/200 SMA */}
      <PriceChart
        prices={pricesData?.data || []}
        technicals={technicals}
        isLoading={loadingPrices}
      />

      {/* 4. Technical Summary */}
      <TechnicalSummary
        data={technicals}
        currentPrice={overview?.current_price}
        isLoading={loadingTechnicals}
      />

      {/* 5. Fundamental Valuation Summary */}
      <FundamentalSummary data={valuation} isLoading={loadingValuation} />

      {/* 6. Today's Market Briefing */}
      <DailyBriefingSummary briefing={briefing} isLoading={loadingBriefing} />

      {/* 7. Latest News Intelligence */}
      <NewsSummary articles={newsData?.articles || []} isLoading={loadingNews} />
    </div>
  );
};

