import React from 'react';
import { DailyBriefing } from '../../types';
import { Sparkles, CheckCircle, AlertTriangle, Building, Landmark, Compass } from 'lucide-react';

interface Props {
  briefing?: DailyBriefing;
  isLoading?: boolean;
}

export const DailyBriefingSummary: React.FC<Props> = ({ briefing, isLoading }) => {
  if (isLoading || !briefing) {
    return (
      <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] animate-pulse h-48 mb-6" />
    );
  }

  return (
    <div className="glass-panel rounded-xl p-5 border border-[#2a2f45] shadow-lg mb-6">
      <div className="flex items-center space-x-2 mb-3">
        <Sparkles className="h-5 w-5 text-amber-400" />
        <h3 className="text-base font-bold text-white">
          Today's Indian Equity Market Intelligence Briefing
        </h3>
        <span className="text-xs text-slate-400">({briefing.date})</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Positives */}
        <div className="glass-card rounded-lg p-3.5 border border-[#2a2f45]">
          <div className="flex items-center space-x-1.5 font-bold text-emerald-400 mb-2">
            <CheckCircle className="h-4 w-4" />
            <span>Constructive Drivers & Opportunities</span>
          </div>
          <ul className="space-y-1.5 text-slate-300">
            {briefing.key_positives.slice(0, 3).map((item, i) => (
              <li key={i} className="flex items-start space-x-1.5">
                <span className="text-emerald-400 font-bold shrink-0">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Negatives / Headwinds */}
        <div className="glass-card rounded-lg p-3.5 border border-[#2a2f45]">
          <div className="flex items-center space-x-1.5 font-bold text-rose-400 mb-2">
            <AlertTriangle className="h-4 w-4" />
            <span>Macro Risks & Market Headwinds</span>
          </div>
          <ul className="space-y-1.5 text-slate-300">
            {briefing.key_negatives.slice(0, 3).map((item, i) => (
              <li key={i} className="flex items-start space-x-1.5">
                <span className="text-rose-400 font-bold shrink-0">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Strategic Implication for Nifty 100 Equal Weight */}
      {briefing.nifty_implications && briefing.nifty_implications.length > 0 && (
        <div className="mt-3.5 p-3 rounded-lg bg-blue-950/20 border border-blue-500/20 text-xs">
          <div className="font-bold text-blue-300 mb-1 flex items-center space-x-1.5">
            <Compass className="h-3.5 w-3.5 text-blue-400" />
            <span>Strategic Implication for Nifty 100 Equal Weight:</span>
          </div>
          <p className="text-slate-300 leading-relaxed">
            {briefing.nifty_implications[0]}
          </p>
        </div>
      )}
    </div>
  );
};

