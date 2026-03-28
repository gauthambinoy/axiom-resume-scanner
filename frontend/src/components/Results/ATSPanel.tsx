import type { ATSScoreResponse } from '../../types';
import { getScoreColor } from '../../utils/constants';

function Bar({ label, value }: { label: string; value: number }) {
  const color = getScoreColor(value);
  return (
    <div className="flex items-center gap-3">
      <span className="text-[11px] text-muted w-28 shrink-0 text-right">{label}</span>
      <div className="flex-1 h-1.5 bg-surface-light rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
      <span className="mono text-[11px] text-muted-light w-8">{value}</span>
    </div>
  );
}

export function ATSPanel({ ats }: { ats: ATSScoreResponse }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-sm font-medium">ATS Breakdown</h3>
        <span
          className="mono text-xs font-semibold px-2 py-0.5 rounded-md"
          style={{
            color: getScoreColor(ats.overall_score),
            backgroundColor: getScoreColor(ats.overall_score) + '15',
          }}
        >
          {ats.grade}
        </span>
      </div>

      <div className="space-y-3">
        <Bar label="Keywords" value={ats.keyword_match_score} />
        <Bar label="Placement" value={ats.keyword_placement_score} />
        <Bar label="Sections" value={ats.section_score} />
        <Bar label="Formatting" value={ats.formatting_score} />
        <Bar label="Relevance" value={ats.relevance_score} />
      </div>

      {ats.section_warnings.length > 0 && (
        <div className="mt-4 pt-3 border-t border-border space-y-1">
          {ats.section_warnings.map((w, i) => (
            <p key={i} className="text-[11px] text-warning">{w}</p>
          ))}
        </div>
      )}
    </div>
  );
}
