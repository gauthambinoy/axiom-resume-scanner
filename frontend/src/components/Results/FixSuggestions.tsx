import { useState } from 'react';
import type { FixResponse } from '../../types';
import { Check, Crosshair, Brain, LayoutGrid, PaintBucket } from 'lucide-react';

const CATEGORY_ICONS = {
  ats_keyword: Crosshair,
  ai_detection: Brain,
  section: LayoutGrid,
  formatting: PaintBucket,
} as const;

const PRIORITY_DOT: Record<string, string> = {
  critical: 'bg-danger',
  high: 'bg-warning',
  medium: 'bg-primary',
  low: 'bg-muted',
};

export function FixSuggestions({ fixes }: { fixes: FixResponse[] }) {
  const [done, setDone] = useState<Set<number>>(new Set());

  if (!fixes.length) return null;

  const toggle = (idx: number) => {
    setDone((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx); else next.add(idx);
      return next;
    });
  };

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-sm font-medium">Fixes</h3>
        <span className="mono text-[10px] text-muted">{done.size}/{fixes.length}</span>
      </div>

      {/* Progress bar */}
      <div className="w-full h-0.5 bg-surface-light rounded-full mb-5 overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all duration-300"
          style={{ width: `${(done.size / fixes.length) * 100}%` }}
        />
      </div>

      <div className="space-y-1">
        {fixes.map((fix, idx) => {
          const Icon = CATEGORY_ICONS[fix.category as keyof typeof CATEGORY_ICONS] || Crosshair;
          const isDone = done.has(idx);

          return (
            <div
              key={idx}
              className={`flex items-start gap-3 px-3 py-2.5 rounded-lg transition cursor-pointer ${
                isDone ? 'opacity-40' : 'hover:bg-surface-light/30'
              }`}
              onClick={() => toggle(idx)}
            >
              {/* Checkbox */}
              <div className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center shrink-0 transition ${
                isDone ? 'bg-primary border-primary' : 'border-border-light'
              }`}>
                {isDone && <Check size={9} className="text-white" />}
              </div>

              {/* Priority dot */}
              <div className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${PRIORITY_DOT[fix.priority]}`} />

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <Icon size={11} className="text-muted shrink-0" />
                  <span className={`text-[11px] font-medium ${isDone ? 'line-through text-muted' : ''}`}>
                    {fix.title}
                  </span>
                </div>
                <p className="text-[10px] text-muted leading-relaxed mt-0.5 line-clamp-2">{fix.description}</p>
                {fix.estimated_impact && (
                  <p className="text-[9px] text-primary mt-1">{fix.estimated_impact}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
