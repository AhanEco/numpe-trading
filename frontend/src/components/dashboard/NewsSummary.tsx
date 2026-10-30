import React from 'react';
import { NewsArticle } from '../../types';
import { Newspaper, ExternalLink, Tag } from 'lucide-react';

interface Props {
  articles: NewsArticle[];
  isLoading?: boolean;
}

export const NewsSummary: React.FC<Props> = ({ articles, isLoading }) => {
  if (isLoading) {
    return (
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] animate-pulse h-64 mb-6" />
    );
  }

  const sentimentStyles = {
    positive: 'bg-emerald-950/40 text-emerald-400 border-emerald-500/30',
    negative: 'bg-rose-950/40 text-rose-400 border-rose-500/30',
    neutral: 'bg-slate-800 text-slate-300 border-slate-700',
  };

  return (
    <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Newspaper className="h-4 w-4 text-blue-400" />
            <span>NLP Financial News Intelligence</span>
          </h3>
          <p className="text-xs text-slate-400">
            Real Indian financial news curated & classified by sentiment and market relevance
          </p>
        </div>
        <span className="text-xs text-slate-400">
          Showing latest {articles.slice(0, 6).length} stories
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {articles.slice(0, 6).map((item) => (
          <div
            key={item.id}
            className="glass-card rounded-xl p-4 border border-[#2a2f45] hover:border-blue-500/30 transition flex flex-col justify-between"
          >
            <div>
              {/* Meta row */}
              <div className="flex flex-wrap items-center justify-between gap-1 mb-2">
                <span className="text-[11px] font-bold text-slate-400">{item.publisher}</span>
                <div className="flex items-center space-x-1.5">
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                      sentimentStyles[item.sentiment] || sentimentStyles.neutral
                    }`}
                  >
                    {item.sentiment.toUpperCase()}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 flex items-center space-x-1">
                    <Tag className="h-2.5 w-2.5" />
                    <span>{item.topic}</span>
                  </span>
                </div>
              </div>

              {/* Headline */}
              <a
                href={item.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-bold text-white hover:text-blue-400 transition flex items-start justify-between group leading-snug"
              >
                <span>{item.headline}</span>
                <ExternalLink className="h-3.5 w-3.5 text-slate-500 group-hover:text-blue-400 shrink-0 ml-1.5 mt-0.5" />
              </a>

              {/* Brief summary */}
              <p className="text-xs text-slate-300 mt-2 line-clamp-2 leading-relaxed">
                {item.summary}
              </p>
            </div>

            {/* Relevance interpretation */}
            <div className="mt-3 pt-2.5 border-t border-[#2a2f45] text-[11px] text-blue-300/90 font-medium">
              💡 {item.market_relevance}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

