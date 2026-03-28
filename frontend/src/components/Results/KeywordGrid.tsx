import type { ATSScoreResponse } from '../../types';
import { Copy } from 'lucide-react';

export function KeywordGrid({ ats }: { ats: ATSScoreResponse }) {
  const copy = (text: string) => { navigator.clipboard.writeText(text).catch(() => {}); };

  if (!ats.matched_keywords.length && !ats.missing_keywords.length) return null;

  return (
    <div className="card p-5">
      <h3 className="text-sm font-medium mb-4">Keywords</h3>

      <div className="grid md:grid-cols-2 gap-5">
        {/* Found */}
        <div>
          <p className="text-[10px] font-medium text-success uppercase tracking-widest mb-2">
            Found &middot; {ats.matched_keywords.length}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {ats.matched_keywords.map((kw) => (
              <span key={kw.keyword} className="px-2 py-0.5 text-[10px] rounded-md bg-success-dim text-success/90 mono">
                {kw.keyword}
              </span>
            ))}
          </div>
        </div>

        {/* Missing */}
        <div>
          <p className="text-[10px] font-medium text-danger uppercase tracking-widest mb-2">
            Missing &middot; {ats.missing_keywords.length}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {ats.missing_keywords.map((kw) => (
              <button
                key={kw}
                onClick={() => copy(kw)}
                className="group flex items-center gap-1 px-2 py-0.5 text-[10px] rounded-md bg-danger-dim text-danger/80 mono hover:bg-danger/20 transition"
              >
                {kw}
                <Copy size={8} className="opacity-0 group-hover:opacity-100 transition" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {ats.skills_only_keywords.length > 0 && (
        <div className="mt-4 pt-3 border-t border-border">
          <p className="text-[10px] font-medium text-warning uppercase tracking-widest mb-2">
            Skills-only (need bullet context) &middot; {ats.skills_only_keywords.length}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {ats.skills_only_keywords.map((kw) => (
              <span key={kw} className="px-2 py-0.5 text-[10px] rounded-md bg-warning-dim text-warning/80 mono">{kw}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
