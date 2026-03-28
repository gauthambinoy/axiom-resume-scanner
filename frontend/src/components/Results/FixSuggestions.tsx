import { useState } from 'react';
import type { FixResponse } from '../../types';
import { PriorityBadge } from '../common/Badge';
import { ProgressBar } from '../common/ProgressBar';
import { Check, Target, Bot, Layout, PenTool } from 'lucide-react';

const CATEGORY_ICONS: Record<string, typeof Target> = {
  ats_keyword: Target,
  ai_detection: Bot,
  section: Layout,
  formatting: PenTool,
};

export function FixSuggestions({ fixes }: { fixes: FixResponse[] }) {
  const [done, setDone] = useState<Set<number>>(new Set());

  if (!fixes.length) return null;

  const groups: Record<string, FixResponse[]> = {};
  fixes.forEach((f, i) => {
    const key = f.priority;
    if (!groups[key]) groups[key] = [];
    groups[key].push({ ...f, affected_bullets: [...f.affected_bullets, i] });
  });

  const completedCount = done.size;

  return (
    <div className="bg-surface rounded-xl p-6 border border-surface-light">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-lg">Fix Suggestions</h3>
        <span className="text-sm text-muted">{completedCount}/{fixes.length} done</span>
      </div>

      <ProgressBar value={completedCount} max={fixes.length} color="#2563EB" />

      <div className="mt-4 space-y-3">
        {fixes.map((fix, idx) => {
          const Icon = CATEGORY_ICONS[fix.category] || Target;
          const isDone = done.has(idx);
          return (
            <div
              key={idx}
              className={`flex items-start gap-3 p-3 rounded-lg border transition ${
                isDone ? 'border-surface-light/50 opacity-50' : 'border-surface-light hover:bg-surface-light/30'
              }`}
            >
              <button
                onClick={() => {
                  setDone((prev) => {
                    const next = new Set(prev);
                    if (next.has(idx)) next.delete(idx); else next.add(idx);
                    return next;
                  });
                }}
                className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded border flex items-center justify-center ${
                  isDone ? 'bg-success border-success' : 'border-muted'
                }`}
              >
                {isDone && <Check size={12} className="text-white" />}
              </button>
              <Icon size={16} className="text-muted mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <PriorityBadge priority={fix.priority} />
                  <span className={`text-sm font-medium ${isDone ? 'line-through' : ''}`}>{fix.title}</span>
                </div>
                <p className="text-xs text-muted">{fix.description}</p>
                {fix.estimated_impact && (
                  <p className="text-xs text-primary mt-1">{fix.estimated_impact}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
