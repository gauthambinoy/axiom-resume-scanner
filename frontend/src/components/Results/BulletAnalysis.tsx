import type { BulletAnalysisResponse } from '../../types';

const RISK_COLORS: Record<string, string> = {
  clean: 'border-l-green-500',
  suspicious: 'border-l-yellow-500',
  flagged: 'border-l-red-500',
};

export function BulletAnalysis({ bullets }: { bullets: BulletAnalysisResponse[] }) {
  if (!bullets.length) return null;

  return (
    <div className="bg-surface rounded-xl p-6 border border-surface-light">
      <h3 className="font-semibold text-lg mb-4">Bullet-by-Bullet Analysis</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-muted border-b border-surface-light">
              <th className="pb-2 pr-2">#</th>
              <th className="pb-2 pr-2">First Word</th>
              <th className="pb-2 pr-2">Words</th>
              <th className="pb-2 pr-2">Diff</th>
              <th className="pb-2 pr-2">Structure</th>
              <th className="pb-2 pr-2">Flags</th>
              <th className="pb-2">Risk</th>
            </tr>
          </thead>
          <tbody>
            {bullets.map((b, i) => (
              <tr
                key={i}
                className={`border-l-2 ${RISK_COLORS[b.ai_risk] || ''} hover:bg-surface-light/30 transition`}
                title={b.text}
              >
                <td className="py-2 pr-2 text-muted">{i + 1}</td>
                <td className="py-2 pr-2 font-mono text-xs">{b.first_word}</td>
                <td className="py-2 pr-2">{b.word_count}</td>
                <td className="py-2 pr-2 text-muted">{b.diff_from_previous !== null ? b.diff_from_previous : '-'}</td>
                <td className="py-2 pr-2 text-xs">{b.structure_type.replace('TYPE_', '')}</td>
                <td className="py-2 pr-2">
                  {b.flags.length > 0 ? (
                    <span className="text-xs text-warning" title={b.flags.join('\n')}>
                      {b.flags.length} issue{b.flags.length > 1 ? 's' : ''}
                    </span>
                  ) : (
                    <span className="text-xs text-success">OK</span>
                  )}
                </td>
                <td className="py-2">
                  <span className={`text-xs font-medium ${
                    b.ai_risk === 'clean' ? 'text-green-400'
                      : b.ai_risk === 'suspicious' ? 'text-yellow-400'
                      : 'text-red-400'
                  }`}>
                    {b.ai_risk}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
