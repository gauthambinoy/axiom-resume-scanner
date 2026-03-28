import { useHistory } from '../../hooks/useHistory';
import { formatDate } from '../../utils/formatters';
import { Trash2 } from 'lucide-react';

export function HistoryPage() {
  const { history, clearHistory } = useHistory();

  if (!history.length) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <p className="text-muted">No scan history yet. Run your first scan to see results here.</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Scan History</h2>
        <button onClick={clearHistory} className="text-sm text-muted hover:text-danger flex items-center gap-1">
          <Trash2 size={14} /> Clear
        </button>
      </div>
      <div className="space-y-3">
        {history.map((scan) => (
          <div key={scan.scan_id} className="bg-surface border border-surface-light rounded-xl p-4 flex items-center justify-between">
            <div>
              <p className="text-sm">{formatDate(scan.timestamp)}</p>
              <p className="text-xs text-muted">ATS: {scan.ats_score.overall_score} | AI: {scan.ai_score.overall_score.toFixed(0)}</p>
            </div>
            <span className={`text-sm font-medium ${
              scan.combined.readiness_level === 'INTERVIEW_READY' ? 'text-success'
                : scan.combined.readiness_level === 'NEEDS_WORK' ? 'text-warning'
                : 'text-danger'
            }`}>
              {scan.combined.readiness_level.replace('_', ' ')}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
