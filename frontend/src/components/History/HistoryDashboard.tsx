import { useState, useEffect } from 'react';
import { getScanHistory, clearHistory, deleteScanFromHistory } from '../../utils/history';
import type { ScanHistoryEntry } from '../../utils/history';
import { Trash2, History, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';

function scoreColor(score: number, inverted = false): string {
  const effective = inverted ? 100 - score : score;
  if (effective >= 70) return '#10B981';
  if (effective >= 40) return '#F59E0B';
  return '#EF4444';
}

function gradeColor(grade: string): string {
  if (grade.startsWith('A')) return '#10B981';
  if (grade.startsWith('B')) return '#F59E0B';
  if (grade.startsWith('C')) return '#F97316';
  return '#EF4444';
}

function readinessColor(level: string): string {
  if (level === 'INTERVIEW_READY') return '#10B981';
  if (level === 'NEEDS_WORK') return '#F59E0B';
  return '#EF4444';
}

function readinessLabel(level: string): string {
  if (level === 'INTERVIEW_READY') return 'Ready';
  if (level === 'NEEDS_WORK') return 'Needs Work';
  return 'At Risk';
}

function formatDate(ts: string): string {
  const d = new Date(ts);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatTime(ts: string): string {
  const d = new Date(ts);
  return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

/** Simple CSS bar chart for score trends */
function TrendBars({ entries, field, inverted = false }: {
  entries: ScanHistoryEntry[];
  field: 'ats_score' | 'ai_score' | 'readiness_score';
  inverted?: boolean;
}) {
  // Show oldest-to-newest (left to right)
  const ordered = [...entries].reverse();
  const maxBars = 15;
  const display = ordered.slice(-maxBars);

  return (
    <div className="flex items-end gap-[3px] h-10">
      {display.map((entry) => {
        const value = entry[field];
        const height = Math.max(value, 4); // min visible height
        return (
          <div
            key={entry.id}
            title={`${Math.round(value)} - ${formatDate(entry.timestamp)}`}
            className="rounded-sm min-w-[6px] flex-1 max-w-[14px] transition-all"
            style={{
              height: `${height}%`,
              backgroundColor: scoreColor(value, inverted),
              opacity: 0.85,
            }}
          />
        );
      })}
    </div>
  );
}

export function HistoryDashboard() {
  const [history, setHistory] = useState<ScanHistoryEntry[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [confirmClear, setConfirmClear] = useState(false);

  useEffect(() => {
    setHistory(getScanHistory());
  }, []);

  const handleDelete = (id: string) => {
    deleteScanFromHistory(id);
    setHistory(getScanHistory());
  };

  const handleClear = () => {
    if (!confirmClear) {
      setConfirmClear(true);
      return;
    }
    clearHistory();
    setHistory([]);
    setConfirmClear(false);
  };

  if (history.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="w-14 h-14 rounded-2xl bg-surface border border-border flex items-center justify-center mb-4">
          <History size={22} className="text-muted" />
        </div>
        <h3 className="text-sm font-semibold mb-1">No scans yet</h3>
        <p className="text-xs text-muted max-w-xs">
          Your scan history will appear here after you run your first scan. Results are saved locally in your browser.
        </p>
      </div>
    );
  }

  const showTrends = history.length >= 3;

  return (
    <div className="space-y-5 animate-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">Scan History</h2>
          <p className="text-[10px] text-muted mt-0.5">
            {history.length} scan{history.length !== 1 ? 's' : ''} saved locally
          </p>
        </div>
        <button
          onClick={handleClear}
          onBlur={() => setConfirmClear(false)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-medium transition border ${
            confirmClear
              ? 'bg-danger/10 border-danger/30 text-danger'
              : 'bg-surface border-border text-muted hover:text-text'
          }`}
        >
          {confirmClear ? (
            <>
              <AlertCircle size={11} /> Confirm clear
            </>
          ) : (
            <>
              <Trash2 size={11} /> Clear all
            </>
          )}
        </button>
      </div>

      {/* Trend Sparklines */}
      {showTrends && (
        <div className="grid grid-cols-3 gap-3">
          <div className="card-elevated p-4">
            <p className="text-[10px] text-muted uppercase tracking-wider mb-2">ATS Score Trend</p>
            <TrendBars entries={history} field="ats_score" />
          </div>
          <div className="card-elevated p-4">
            <p className="text-[10px] text-muted uppercase tracking-wider mb-2">AI Risk Trend</p>
            <TrendBars entries={history} field="ai_score" inverted />
          </div>
          <div className="card-elevated p-4">
            <p className="text-[10px] text-muted uppercase tracking-wider mb-2">Readiness Trend</p>
            <TrendBars entries={history} field="readiness_score" />
          </div>
        </div>
      )}

      {/* Table */}
      <div className="card-elevated overflow-hidden">
        {/* Header row */}
        <div className="grid grid-cols-[1fr_80px_70px_70px_80px_60px_36px] gap-2 px-4 py-2.5 border-b border-border text-[10px] text-muted uppercase tracking-wider font-medium">
          <span>Date</span>
          <span>Mode</span>
          <span>ATS</span>
          <span>AI Risk</span>
          <span>Readiness</span>
          <span>Grade</span>
          <span></span>
        </div>

        {/* Rows */}
        {history.map((entry) => {
          const isExpanded = expandedId === entry.id;
          return (
            <div key={entry.id} className="border-b border-border/50 last:border-0">
              <div
                onClick={() => setExpandedId(isExpanded ? null : entry.id)}
                className="grid grid-cols-[1fr_80px_70px_70px_80px_60px_36px] gap-2 px-4 py-3 items-center cursor-pointer hover:bg-surface/50 transition text-xs"
              >
                <div className="flex flex-col">
                  <span className="text-text font-medium">{formatDate(entry.timestamp)}</span>
                  <span className="text-[10px] text-muted">{formatTime(entry.timestamp)}</span>
                </div>
                <span className="capitalize text-muted">{entry.mode}</span>
                <span className="font-mono font-semibold" style={{ color: scoreColor(entry.ats_score) }}>
                  {Math.round(entry.ats_score)}
                </span>
                <span className="font-mono font-semibold" style={{ color: scoreColor(entry.ai_score, true) }}>
                  {Math.round(entry.ai_score)}
                </span>
                <span className="text-[11px] font-medium" style={{ color: readinessColor(entry.readiness_level) }}>
                  {readinessLabel(entry.readiness_level)}
                </span>
                <span className="font-mono font-bold text-sm" style={{ color: gradeColor(entry.grade) }}>
                  {entry.grade}
                </span>
                <div className="flex items-center justify-end gap-1">
                  {isExpanded ? <ChevronUp size={12} className="text-muted" /> : <ChevronDown size={12} className="text-muted" />}
                </div>
              </div>

              {/* Expanded details */}
              {isExpanded && (
                <div className="px-4 pb-3 space-y-2 animate-in">
                  {entry.text_preview && (
                    <div className="bg-surface rounded-lg px-3 py-2">
                      <p className="text-[10px] text-muted uppercase tracking-wider mb-1">Preview</p>
                      <p className="text-[11px] text-text/70 leading-relaxed">
                        {entry.text_preview}{entry.text_preview.length >= 100 ? '...' : ''}
                      </p>
                    </div>
                  )}
                  <div className="grid grid-cols-3 gap-2 text-[11px]">
                    <div className="bg-surface rounded-lg px-3 py-2">
                      <p className="text-[10px] text-muted">ATS Score</p>
                      <p className="font-mono font-semibold" style={{ color: scoreColor(entry.ats_score) }}>
                        {Math.round(entry.ats_score)} / 100
                      </p>
                    </div>
                    <div className="bg-surface rounded-lg px-3 py-2">
                      <p className="text-[10px] text-muted">AI Detection</p>
                      <p className="font-mono font-semibold" style={{ color: scoreColor(entry.ai_score, true) }}>
                        {Math.round(entry.ai_score)} / 100
                      </p>
                    </div>
                    <div className="bg-surface rounded-lg px-3 py-2">
                      <p className="text-[10px] text-muted">Readiness</p>
                      <p className="font-mono font-semibold" style={{ color: scoreColor(entry.readiness_score) }}>
                        {Math.round(entry.readiness_score)} / 100
                      </p>
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(entry.id);
                      }}
                      className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-medium text-danger/70 hover:text-danger hover:bg-danger/10 transition"
                    >
                      <Trash2 size={10} /> Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
