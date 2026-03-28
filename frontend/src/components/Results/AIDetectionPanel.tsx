import { useState } from 'react';
import type { AIDetectionResponse } from '../../types';
import { ChevronRight } from 'lucide-react';
import { getSignalColor } from '../../utils/constants';

export function AIDetectionPanel({ ai }: { ai: AIDetectionResponse }) {
  const [open, setOpen] = useState<string | null>(null);

  const riskColors: Record<string, string> = {
    LOW: 'text-success bg-success-dim',
    MODERATE: 'text-warning bg-warning-dim',
    HIGH: 'text-danger bg-danger-dim',
    CRITICAL: 'text-danger bg-danger-dim',
  };

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-sm font-medium">AI Detection</h3>
        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md ${riskColors[ai.risk_level] || ''}`}>
          {ai.risk_level}
        </span>
      </div>

      <div className="space-y-0.5">
        {ai.signals.map((s) => {
          const isOpen = open === s.name;
          const color = getSignalColor(s.score, s.max_score);
          const pct = Math.min(100, (s.score / s.max_score) * 100);

          return (
            <div key={s.name}>
              <button
                onClick={() => setOpen(isOpen ? null : s.name)}
                className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-surface-light/50 transition text-left group"
              >
                <ChevronRight
                  size={11}
                  className={`text-muted transition-transform shrink-0 ${isOpen ? 'rotate-90' : ''}`}
                />
                <span className="flex-1 text-[11px] text-text-secondary truncate">{s.name}</span>
                <div className="w-16 h-1 bg-surface-light rounded-full overflow-hidden shrink-0">
                  <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: color }} />
                </div>
                <span className="mono text-[10px] text-muted w-7 text-right shrink-0">{s.score.toFixed(1)}</span>
              </button>

              {isOpen && (
                <div className="ml-7 mr-2 mb-2 px-3 py-2 bg-bg rounded-lg border border-border">
                  <p className="text-[11px] text-muted leading-relaxed">{s.details}</p>
                  {s.flagged_items.length > 0 && (
                    <div className="mt-1.5 space-y-0.5">
                      {s.flagged_items.slice(0, 5).map((item, i) => (
                        <p key={i} className="text-[10px] text-danger/70 mono">{item}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
