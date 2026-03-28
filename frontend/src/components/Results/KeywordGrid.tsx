import type { ATSScoreResponse } from '../../types';
import { Check, X, Copy } from 'lucide-react';

export function KeywordGrid({ ats }: { ats: ATSScoreResponse }) {
  const copy = (text: string) => {
    navigator.clipboard.writeText(text).catch(() => {});
  };

  return (
    <div className="bg-surface rounded-xl p-6 border border-surface-light">
      <h3 className="font-semibold text-lg mb-4">Keywords</h3>
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-medium text-success mb-2 flex items-center gap-1">
            <Check size={14} /> Found ({ats.matched_keywords.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {ats.matched_keywords.map((kw) => (
              <span key={kw.keyword} className="px-2 py-1 text-xs bg-green-600/15 text-green-400 rounded-md">
                {kw.keyword}
              </span>
            ))}
          </div>
        </div>
        <div>
          <h4 className="text-sm font-medium text-danger mb-2 flex items-center gap-1">
            <X size={14} /> Missing ({ats.missing_keywords.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {ats.missing_keywords.map((kw) => (
              <button
                key={kw}
                onClick={() => copy(kw)}
                className="group px-2 py-1 text-xs bg-red-600/15 text-red-400 rounded-md flex items-center gap-1 hover:bg-red-600/25 transition"
              >
                {kw}
                <Copy size={10} className="opacity-0 group-hover:opacity-100 transition" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {ats.skills_only_keywords.length > 0 && (
        <div className="mt-4 pt-4 border-t border-surface-light">
          <h4 className="text-sm font-medium text-warning mb-2">Skills-Only Keywords (need bullet context)</h4>
          <div className="flex flex-wrap gap-2">
            {ats.skills_only_keywords.map((kw) => (
              <span key={kw} className="px-2 py-1 text-xs bg-yellow-600/15 text-yellow-400 rounded-md">{kw}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
