import type { BulletAnalysisResponse } from '../../types';

const RISK_DOT: Record<string, string> = {
  clean: 'bg-success',
  suspicious: 'bg-warning',
  flagged: 'bg-danger',
};

export function BulletAnalysis({ bullets }: { bullets: BulletAnalysisResponse[] }) {
  if (!bullets.length) return null;

  return (
    <div className="card p-5">
      <h3 className="text-sm font-medium mb-4">Bullet Analysis</h3>
      <div className="space-y-1">
        {bullets.map((b, i) => (
          <div
            key={i}
            className="flex items-start gap-3 px-3 py-2.5 rounded-lg hover:bg-surface-light/30 transition group"
          >
            <div className="flex items-center gap-2 shrink-0 mt-0.5">
              <span className="mono text-[10px] text-muted w-4 text-right">{i + 1}</span>
              <div className={`w-1.5 h-1.5 rounded-full ${RISK_DOT[b.ai_risk]}`} />
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-[11px] text-text-secondary leading-relaxed truncate group-hover:whitespace-normal group-hover:overflow-visible">
                {b.text}
              </p>
              {b.flags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {b.flags.map((f, j) => (
                    <span key={j} className="text-[9px] px-1.5 py-0.5 rounded bg-danger-dim text-danger/80">{f}</span>
                  ))}
                </div>
              )}
            </div>

            <div className="flex items-center gap-3 shrink-0 text-[10px] text-muted">
              <span className="mono w-6 text-right">{b.word_count}w</span>
              {b.diff_from_previous !== null && (
                <span className={`mono w-6 text-right ${b.diff_from_previous < 3 ? 'text-warning' : ''}`}>
                  {b.diff_from_previous === 0 ? '=' : `${b.diff_from_previous > 0 ? '+' : ''}${b.diff_from_previous}`}
                </span>
              )}
              <span className="w-16 text-right text-[9px] uppercase tracking-wider">
                {b.structure_type.replace('TYPE_', '').toLowerCase().replace('_', ' ')}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4 mt-4 pt-3 border-t border-border text-[10px] text-muted">
        <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-success" /> Clean</span>
        <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-warning" /> Suspicious</span>
        <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-danger" /> Flagged</span>
      </div>
    </div>
  );
}
