import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Newspaper, ExternalLink, Filter, Sparkles, Tag, CheckCircle2, AlertCircle } from 'lucide-react';

const TOPICS = [
  'All Topics',
  'Indian equity markets',
  'Corporate earnings',
  'RBI monetary policy',
  'Inflation',
  'Interest rates',
  'Foreign portfolio investment',
  'Domestic institutional investment',
  'Crude oil',
  'Indian rupee',
  'Banking sector',
  'Government policy',
  'Geopolitical developments',
];

export const NewsIntelligence: React.FC = () => {
  const [selectedTopic, setSelectedTopic] = useState('All Topics');
  const [selectedSentiment, setSelectedSentiment] = useState<string>('all');

  const { data: newsData, isLoading } = useQuery({
    queryKey: ['news', selectedTopic, selectedSentiment],
    queryFn: () =>
      api.getLatestNews(
        40,
        selectedTopic !== 'All Topics' ? selectedTopic : undefined,
        selectedSentiment !== 'all' ? selectedSentiment : undefined
      ),
  });

  const { data: sentimentSummary } = useQuery({
    queryKey: ['sentimentSummary'],
    queryFn: () => api.getSentimentSummary(7),
  });

  const { data: briefing } = useQuery({
    queryKey: ['dailyBriefing'],
    queryFn: api.getDailyBriefing,
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-black text-white flex items-center space-x-2">
          <Newspaper className="h-6 w-6 text-blue-400" />
          <span>NLP Financial News Intelligence & Market Briefing</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Automated news retrieval from legitimate Indian financial publications with domain-specific NLP sentiment and entity tagging.
        </p>
      </div>

      {/* Sentiment Gauge Card */}
      {sentimentSummary && sentimentSummary.total > 0 && (
        <div className="glass-panel rounded-xl p-5 border border-[#2a2f45]">
          <h3 className="text-sm font-bold text-white mb-2">
            7-Day Market Sentiment Distribution ({sentimentSummary.total} articles analyzed)
          </h3>
          <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden flex mb-2">
            <div
              className="bg-emerald-500 h-3"
              style={{ width: `${sentimentSummary.positive_pct}%` }}
              title={`Positive: ${sentimentSummary.positive_pct}%`}
            />
            <div
              className="bg-slate-500 h-3"
              style={{ width: `${sentimentSummary.neutral_pct}%` }}
              title={`Neutral: ${sentimentSummary.neutral_pct}%`}
            />
            <div
              className="bg-rose-500 h-3"
              style={{ width: `${sentimentSummary.negative_pct}%` }}
              title={`Negative: ${sentimentSummary.negative_pct}%`}
            />
          </div>
          <div className="flex justify-between text-xs text-slate-300">
            <span className="text-emerald-400 font-bold">● Positive: {sentimentSummary.positive_pct}%</span>
            <span className="text-slate-400 font-bold">● Neutral: {sentimentSummary.neutral_pct}%</span>
            <span className="text-rose-400 font-bold">● Negative: {sentimentSummary.negative_pct}%</span>
          </div>
        </div>
      )}

      {/* Daily Market Briefing */}
      {briefing && (
        <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg">
          <div className="flex items-center space-x-2 mb-3">
            <Sparkles className="h-5 w-5 text-amber-400" />
            <h3 className="text-base font-bold text-white">
              Today's Indian Equity Market Intelligence Briefing ({briefing.date})
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="glass-card rounded-lg p-3.5 border border-[#2a2f45]">
              <div className="font-bold text-emerald-400 mb-2">Constructive Tailwinds</div>
              <ul className="space-y-1.5 text-slate-300">
                {briefing.key_positives.map((p, i) => (
                  <li key={i}>• {p}</li>
                ))}
              </ul>
            </div>
            <div className="glass-card rounded-lg p-3.5 border border-[#2a2f45]">
              <div className="font-bold text-rose-400 mb-2">Macro Headwinds</div>
              <ul className="space-y-1.5 text-slate-300">
                {briefing.key_negatives.map((n, i) => (
                  <li key={i}>• {n}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <div className="glass-panel rounded-xl p-4 border border-[#2a2f45] flex flex-wrap items-center justify-between gap-3">
        {/* Topic Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          {TOPICS.slice(0, 7).map((t) => (
            <button
              key={t}
              onClick={() => setSelectedTopic(t)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition ${
                selectedTopic === t
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-900/60 text-slate-400 hover:text-white border border-[#2a2f45]'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Sentiment selector */}
        <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-lg border border-[#2a2f45] text-xs">
          {['all', 'positive', 'neutral', 'negative'].map((s) => (
            <button
              key={s}
              onClick={() => setSelectedSentiment(s)}
              className={`px-2.5 py-0.5 rounded capitalize ${
                selectedSentiment === s ? 'bg-blue-600 text-white font-bold' : 'text-slate-400'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {isLoading ? (
          <div className="col-span-2 text-center py-12 text-slate-400">Loading intelligence feed...</div>
        ) : (newsData?.articles || []).length === 0 ? (
          <div className="col-span-2 text-center py-12 text-slate-400">
            No news matching the selected filter. Try choosing "All Topics".
          </div>
        ) : (
          (newsData?.articles || []).map((art) => (
            <div
              key={art.id}
              className="glass-card rounded-xl p-4 border border-[#2a2f45] hover:border-blue-500/40 transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-2">
                  <span className="font-bold">{art.publisher}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      art.sentiment === 'positive'
                        ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-500/30'
                        : art.sentiment === 'negative'
                        ? 'bg-rose-950/40 text-rose-400 border border-rose-500/30'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {art.sentiment.toUpperCase()}
                  </span>
                </div>

                <a
                  href={art.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-bold text-white hover:text-blue-400 transition flex items-start justify-between group"
                >
                  <span>{art.headline}</span>
                  <ExternalLink className="h-3.5 w-3.5 text-slate-500 group-hover:text-blue-400 shrink-0 ml-1.5 mt-0.5" />
                </a>

                <p className="text-xs text-slate-300 mt-2 line-clamp-3 leading-relaxed">
                  {art.summary}
                </p>
              </div>

              <div className="mt-3 pt-2.5 border-t border-[#2a2f45] flex items-center justify-between text-[11px]">
                <span className="text-slate-400">{art.topic}</span>
                <span className="text-blue-300 font-medium">Confidence: {(art.confidence_score * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

