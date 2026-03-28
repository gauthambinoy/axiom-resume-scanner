import { useState } from 'react';
import type { AIDetectionResponse } from '../../types';
import { RiskBadge } from '../common/Badge';
import { getSignalColor } from '../../utils/constants';
import { ChevronDown, ChevronRight } from 'lucide-react';

export function AIDetectionPanel({ ai }: { ai: AIDetectionResponse }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="bg-surface rounded-xl p-6 border border-surface-light">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-lg">AI Detection</h3>
        <RiskBadge level={ai.risk_level} />
      </div>

      <div className="space-y-2">
        {ai.signals.map((signal) => {
          const isOpen = expanded === signal.name;
          const color = getSignalColor(signal.score, signal.max_score);
          const pct = (signal.score / signal.max_score) * 100;

          return (
            <div key={signal.name} className="border border-surface-light rounded-lg overflow-hidden">
              <button
                onClick={() => setExpanded(isOpen ? null : signal.name)}
                className="w-full flex items-center gap-3 p-3 hover:bg-surface-light/50 transition text-left"
              >
                {isOpen ? <ChevronDown size={14} className="text-muted" /> : <ChevronRight size={14} className="text-muted" />}
                <span className="flex-1 text-sm">{signal.name}</span>
                <div className="w-24 h-1.5 bg-surface-light rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: color }} />
                </div>
                <span className="text-xs text-muted w-12 text-right">{signal.score.toFixed(1)}</span>
              </button>
              {isOpen && (
                <div className="px-3 pb-3 text-xs text-muted space-y-1">
                  <p>{signal.details}</p>
                  {signal.flagged_items.map((item, i) => (
                    <p key={i} className="text-danger/80 pl-4">- {item}</p>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
