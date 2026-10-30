/// <reference types="vite/client" />
import axios from 'axios';
import {
  MarketOverview,
  InvestmentSignal,
  PricePoint,
  TechnicalIndicators,
  ValuationMetrics,
  NewsArticle,
  DailyBriefing,
  BacktestResult,
  AppSettings,
} from '../types';

// Use environment variable in production, fallback to relative path with Vite proxy in dev
const API_BASE_URL = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Set token for admin operations
export const setAuthToken = (token: string | null) => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('numpe_admin_token', token);
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
    localStorage.removeItem('numpe_admin_token');
  }
};

// Initialize token from storage if present
const storedToken = localStorage.getItem('numpe_admin_token');
if (storedToken) {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
}

export const api = {
  // Market Data
  getMarketOverview: async (): Promise<MarketOverview> => {
    const res = await apiClient.get<MarketOverview>('/market/overview');
    return res.data;
  },
  getPrices: async (startDate?: string, endDate?: string): Promise<{ data: PricePoint[] }> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const res = await apiClient.get<{ data: PricePoint[] }>(`/market/prices?${params.toString()}`);
    return res.data;
  },
  exportPricesCsvUrl: (): string => `${API_BASE_URL}/market/export/csv`,

  // Technical Indicators
  getCurrentTechnicals: async (): Promise<TechnicalIndicators> => {
    const res = await apiClient.get<TechnicalIndicators>('/technical/current');
    return res.data;
  },
  getRsiHistory: async (startDate?: string, endDate?: string): Promise<{ data: Array<{ date: string; rsi_14: number }> }> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const res = await apiClient.get(`/technical/rsi?${params.toString()}`);
    return res.data;
  },
  getSmaHistory: async (startDate?: string, endDate?: string): Promise<{ data: Array<{ date: string; sma_50: number; sma_200: number }> }> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const res = await apiClient.get(`/technical/sma?${params.toString()}`);
    return res.data;
  },
  getMacdHistory: async (startDate?: string, endDate?: string): Promise<{ data: Array<{ date: string; macd: number; macd_signal: number; macd_histogram: number }> }> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const res = await apiClient.get(`/technical/macd?${params.toString()}`);
    return res.data;
  },

  // Fundamental Valuation
  getCurrentValuation: async (): Promise<ValuationMetrics> => {
    const res = await apiClient.get<ValuationMetrics>('/fundamental/current');
    return res.data;
  },
  getValuationHistory: async (startDate?: string, endDate?: string): Promise<{ data: Array<Partial<ValuationMetrics>> }> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const res = await apiClient.get(`/fundamental/history?${params.toString()}`);
    return res.data;
  },

  // Investment Signals
  getCurrentSignal: async (): Promise<InvestmentSignal> => {
    const res = await apiClient.get<InvestmentSignal>('/signals/current');
    return res.data;
  },

  // News Intelligence
  getLatestNews: async (limit = 25, topic?: string, sentiment?: string): Promise<{ count: number; articles: NewsArticle[] }> => {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (topic) params.append('topic', topic);
    if (sentiment) params.append('sentiment', sentiment);
    const res = await apiClient.get(`/news/latest?${params.toString()}`);
    return res.data;
  },
  getDailyBriefing: async (): Promise<DailyBriefing> => {
    const res = await apiClient.get<DailyBriefing>('/news/briefing');
    return res.data;
  },
  getSentimentSummary: async (days = 7): Promise<{ total: number; positive_pct: number; negative_pct: number; neutral_pct: number; net_sentiment: number }> => {
    const res = await apiClient.get(`/news/sentiment-summary?days=${days}`);
    return res.data;
  },

  // Backtesting
  getStrategies: async (): Promise<Array<{ code: string; name: string }>> => {
    const res = await apiClient.get<Array<{ code: string; name: string }>>('/backtest/strategies');
    return res.data;
  },
  runBacktest: async (payload: {
    strategy: string;
    start_date?: string;
    end_date?: string;
    initial_investment: number;
    sip_amount: number;
    rebalance_cost_pct: number;
  }): Promise<BacktestResult> => {
    const res = await apiClient.post<BacktestResult>('/backtest/run', payload);
    return res.data;
  },

  // Settings & Auth
  login: async (password: string): Promise<{ access_token: string; token_type: string }> => {
    const res = await apiClient.post('/settings/auth/login', { password });
    setAuthToken(res.data.access_token);
    return res.data;
  },
  getSettings: async (): Promise<AppSettings> => {
    const res = await apiClient.get<AppSettings>('/settings/');
    return res.data;
  },
  updateSettings: async (settings: AppSettings): Promise<{ message: string; settings: AppSettings }> => {
    const res = await apiClient.put('/settings/', settings);
    return res.data;
  },

  // System
  triggerSync: async (): Promise<{ status: string; message: string; news_added: number }> => {
    const res = await apiClient.post('/system/sync');
    return res.data;
  },
  getSystemStatus: async () => {
    const res = await apiClient.get('/system/status');
    return res.data;
  },
};
