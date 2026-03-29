import { useState } from 'react';
import type { HeatmapItem } from '../../types';
import { Flame } from 'lucide-react';

interface Props {
  heatmap: HeatmapItem[];
}

function getRiskBg(risk: number): string {
  if (risk <= 0.2) return 'bg-success/15';
  if (risk <= 0.5) return 'bg-warning/15';
  if (risk <= 0.75) return 'bg-orange-400/15';
  return 'bg-danger/15';
}

function getRiskBorder(risk: number): string {
  if (risk <= 0.2) return 'border-success/30';
  if (risk <= 0.5) return 'border-warning/30';
  if (risk <= 0.75) return 'border-orange-400/30';
  return 'border-danger/30';
}

function getRiskLabel(risk: number): string {
  if (risk <= 0.2) return 'Clean';
  if (risk <= 0.5) return 'Mild';
  if (risk <= 0.75) return 'Suspicious';
  return 'Flagged';
}

function getRiskTextColor(risk: number): string {
  if (risk <= 0.2) return 'text-success';
  if (risk <= 0.5) return 'text-warning';
  if (risk <= 0.75) return 'text-orange-400';
  return 'text-danger';
}

export function DetectionHeatmap({ heatmap }: Props) {
  const [activeIdx, setActiveIdx] = useState<number | null>(null);

  if (!heatmap || heatmap.length === 0) return null;

  return (
    <div className="card p-5 animate-in">
      <div className="flex items-center gap-2 mb-4">
        <Flame size={14} className="text-primary" />
        <h3 className="text-sm font-semibold">AI Detection Heatmap</h3>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mb-4 text-[10px] text-muted">
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-success/30" /> Clean (0-0.2)</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-warning/30" /> Mild (0.2-0.5)</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-orange-400/30" /> Suspicious (0.5-0.75)</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-danger/30" /> Flagged (0.75-1.0)</span>
      </div>

      {/* Sentences */}
      <div className="space-y-1.5">
        {heatmap.map((item, idx) => (
          <div key={idx} className="relative">
            <div
              className={`px-3 py-2 rounded-lg border cursor-pointer transition ${getRiskBg(item.risk)} ${getRiskBorder(item.risk)} ${
                activeIdx === idx ? 'ring-1 ring-primary/40' : ''
              }`}
              onClick={() => setActiveIdx(activeIdx === idx ? null : idx)}
              onMouseEnter={() => setActiveIdx(idx)}
              onMouseLeave={() => setActiveIdx(null)}
            >
              <div className="flex items-start justify-between gap-3">
                <p className="text-[11px] text-text-secondary leading-relaxed flex-1">{item.text}</p>
                <span className={`shrink-0 text-[10px] font-semibold ${getRiskTextColor(item.risk)}`}>
                  {getRiskLabel(item.risk)} ({(item.risk * 100).toFixed(0)}%)
                </span>
              </div>
            </div>

            {/* Tooltip with flags */}
            {activeIdx === idx && item.flags.length > 0 && (
              <div className="absolute z-20 left-4 top-full mt-1 px-3 py-2 bg-surface-light text-text rounded-lg shadow-lg border border-border max-w-sm">
                <p className="text-[10px] font-semibold text-muted mb-1">Flags</p>
                <ul className="space-y-0.5">
                  {item.flags.map((flag, fi) => (
                    <li key={fi} className="text-[10px] text-text-secondary">- {flag}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
