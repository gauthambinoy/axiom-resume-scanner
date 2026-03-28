import type { CompareResponse } from '../../types';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';

function Change({ value, inverted = false }: { value: number; inverted?: boolean }) {
  const isGood = inverted ? value < 0 : value > 0;
  const isBad = inverted ? value > 0 : value < 0;
  const Icon = value > 0 ? ArrowUp : value < 0 ? ArrowDown : Minus;
  const color = isGood ? 'text-green-400' : isBad ? 'text-red-400' : 'text-muted';

  return (
    <span className={`inline-flex items-center gap-1 ${color}`}>
      <Icon size={14} />
      {Math.abs(value)}
    </span>
  );
}

export function ComparisonView({ data }: { data: CompareResponse }) {
  return (
    <div className="bg-surface rounded-xl p-6 border border-surface-light">
      <h3 className="font-semibold text-lg mb-4">Before vs After</h3>
      <div className="grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-sm text-muted mb-1">ATS Score</p>
          <p className="text-2xl font-bold">{data.before.ats_score.overall_score} &rarr; {data.after.ats_score.overall_score}</p>
          <Change value={data.ats_change} />
        </div>
        <div>
          <p className="text-sm text-muted mb-1">AI Detection</p>
          <p className="text-2xl font-bold">{data.before.ai_score.overall_score.toFixed(0)} &rarr; {data.after.ai_score.overall_score.toFixed(0)}</p>
          <Change value={data.ai_change} inverted />
        </div>
        <div>
          <p className="text-sm text-muted mb-1">Readiness</p>
          <p className="text-2xl font-bold">{data.before.combined.interview_readiness_score} &rarr; {data.after.combined.interview_readiness_score}</p>
          <Change value={data.readiness_change} />
        </div>
      </div>
      {data.improved_keywords.length > 0 && (
        <div className="mt-4 pt-4 border-t border-surface-light">
          <p className="text-sm text-success">Newly matched: {data.improved_keywords.join(', ')}</p>
        </div>
      )}
    </div>
  );
}
