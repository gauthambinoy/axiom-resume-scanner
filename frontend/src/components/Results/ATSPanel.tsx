import type { ATSScoreResponse } from '../../types';
import { ProgressBar } from '../common/ProgressBar';
import { getScoreColor } from '../../utils/constants';

export function ATSPanel({ ats }: { ats: ATSScoreResponse }) {
  const dimensions = [
    { label: 'Keyword Match', value: ats.keyword_match_score },
    { label: 'Keyword Placement', value: ats.keyword_placement_score },
    { label: 'Section Structure', value: ats.section_score },
    { label: 'Formatting', value: ats.formatting_score },
    { label: 'Relevance', value: ats.relevance_score },
  ];

  return (
    <div className="bg-surface rounded-xl p-6 border border-surface-light">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-lg">ATS Breakdown</h3>
        <span className="text-2xl font-bold" style={{ color: getScoreColor(ats.overall_score) }}>
          {ats.grade}
        </span>
      </div>

      <div className="space-y-4">
        {dimensions.map((d) => (
          <ProgressBar key={d.label} label={d.label} value={d.value} color={getScoreColor(d.value)} />
        ))}
      </div>

      {ats.section_warnings.length > 0 && (
        <div className="mt-4 space-y-1">
          {ats.section_warnings.map((w, i) => (
            <p key={i} className="text-xs text-warning">{w}</p>
          ))}
        </div>
      )}
    </div>
  );
}
