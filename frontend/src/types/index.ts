export interface MarketOverview {
  index_name: string;
  current_price: number | null;
  previous_close: number | null;
  daily_change: number;
  daily_change_pct: number;
  pe_ratio: number | null;
  pb_ratio: number | null;
  rsi_14: number | null;
  rsi_interpretation?: string;
  high_52w: number | null;
  low_52w: number | null;
  sma_200: number | null;
  sma_50: number | null;
  distance_from_sma200_pct: number | null;
  distance_from_52w_low_pct: number | null;
  is_market_open: boolean;
  market_status_text: string;
  observation_date: string | null;
  source: string;
  data_quality: string;
}

export interface SignalCondition {
  name: string;
  condition_id: string;
  met: boolean;
  status: 'SATISFIED' | 'NOT_SATISFIED' | 'INSUFFICIENT_DATA';
  actual_value: number | null;
  target_value: string;
  threshold_value?: number;
  mode?: string;
  explanation: string;
  is_experimental?: boolean;
}

export interface InvestmentSignal {
  date: string;
  index_name: string;
  conditions_met_count: number;
  total_conditions: number;
  signal_category: string;
  market_assessment: string;
  summary: string;
  current_price: number | null;
  price_threshold: number | null;
  current_rsi: number | null;
  rsi_threshold: number;
  current_pe: number | null;
  pe_threshold: number;
  current_pb: number | null;
  pb_lower: number;
  pb_upper: number;
  sma_200: number | null;
  low_52w: number | null;
  conditions: SignalCondition[];
  disclaimer: string;
}

export interface PricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  source?: string;
}

export interface TechnicalIndicators {
  date: string;
  index_name: string;
  rsi_14: number | null;
  sma_50: number | null;
  sma_200: number | null;
  high_52w: number | null;
  low_52w: number | null;
  distance_from_sma200_pct: number | null;
  distance_from_52w_low_pct: number | null;
  distance_from_52w_high_pct: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  rsi_interpretation?: string;
}

export interface ValuationMetrics {
  date: string;
  index_name: string;
  pe_ratio: number | null;
  pb_ratio: number | null;
  earnings_yield: number | null;
  pe_1y_avg: number | null;
  pe_3y_avg: number | null;
  pe_5y_avg: number | null;
  pe_percentile: number | null;
  pb_1y_avg: number | null;
  pb_3y_avg: number | null;
  pb_5y_avg: number | null;
  pb_percentile: number | null;
  pe_type: string;
  source: string;
  benchmarks?: {
    pe_median_5y: number;
    pe_min_5y: number;
    pe_max_5y: number;
    pb_median_5y: number;
    pb_min_5y: number;
    pb_max_5y: number;
    ind_10y_gsec_yield: number;
  };
}

export interface NewsArticle {
  id: number;
  headline: string;
  publisher: string;
  published_at: string;
  source_url: string;
  topic: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  sentiment_score: number;
  named_entities: Record<string, string[]>;
  summary: string;
  market_relevance: string;
  confidence_score: number;
}

export interface DailyBriefing {
  date: string;
  content: string;
  key_positives: string[];
  key_negatives: string[];
  macro_risks: string[];
  rbi_developments: string[];
  fii_dii_developments: string[];
  nifty_implications: string[];
}

export interface BacktestResult {
  strategy: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  duration_years: number;
  initial_investment: number;
  total_invested: number;
  final_value: number;
  absolute_return: number;
  return_pct: number;
  cagr_pct: number | null;
  max_drawdown_pct: number;
  volatility_pct: number;
  sharpe_ratio: number | null;
  trades_count: number;
  benchmark_final_value: number;
  benchmark_return_pct: number;
  outperformance_pct: number;
  curve_samples: Array<{
    date: string;
    portfolio_value: number;
    index_price: number;
    benchmark_value: number;
  }>;
  disclaimer: string;
}

export interface AppSettings {
  rsi_threshold: number;
  pe_threshold: number;
  pb_lower: number;
  pb_upper: number;
  price_interpretation: 'below' | 'band';
  price_band_pct: number;
  sma_period: number;
}

