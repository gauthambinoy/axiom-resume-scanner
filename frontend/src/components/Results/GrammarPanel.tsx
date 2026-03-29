import { useState } from 'react';
import type { GrammarResponse, GrammarIssue } from '../../types';
import { getScoreColor } from '../../utils/constants';
import { SpellCheck, AlertCircle, AlertTriangle, Lightbulb, ChevronDown, ChevronRight } from 'lucide-react';

interface Props {
  grammar?: GrammarResponse;
}

const SEVERITY_CONFIG: Record<string, { label: string; color: string; bg: string; icon: typeof AlertCircle }> = {
  error: { label: 'Errors', color: 'text-danger', bg: 'bg-danger/10', icon: AlertCircle },
  warning: { label: 'Warnings', color: 'text-warning', bg: 'bg-warning/10', icon: AlertTriangle },
  suggestion: { label: 'Suggestions', color: 'text-primary', bg: 'bg-primary/10', icon: Lightbulb },
};

function IssueItem({ issue }: { issue: GrammarIssue }) {
  const config = SEVERITY_CONFIG[issue.severity] || SEVERITY_CONFIG.suggestion;

  return (
    <div className="bg-bg rounded-lg border border-border px-3 py-2.5 space-y-1.5">
      <div className="flex items-start gap-2">
        <config.icon size={12} className={`${config.color} mt-0.5 shrink-0`} />
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-medium text-text">{issue.message}</p>
          {issue.context && (
            <p className="text-[10px] text-muted mt-1 font-mono bg-surface rounded px-2 py-1 break-all">
              &ldquo;{issue.context}&rdquo;
            </p>
          )}
          {issue.suggestion && (
            <p className="text-[10px] text-success mt-1">
              Fix: {issue.suggestion}
            </p>
          )}
        </div>
        <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded ${config.bg} ${config.color} shrink-0`}>
          {issue.type}
        </span>
      </div>
    </div>
  );
}

function IssueGroup({ severity, issues }: { severity: string; issues: GrammarIssue[] }) {
  const [expanded, setExpanded] = useState(severity === 'error');
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.suggestion;

  if (issues.length === 0) return null;

  return (
    <div className="border border-border rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-surface hover:bg-surface-light transition"
      >
        <div className="flex items-center gap-2">
          <config.icon size={13} className={config.color} />
          <span className="text-xs font-medium">{config.label}</span>
          <span className={`text-[10px] font-semibold mono px-1.5 py-0.5 rounded ${config.bg} ${config.color}`}>
            {issues.length}
          </span>
        </div>
        {expanded ? <ChevronDown size={13} className="text-muted" /> : <ChevronRight size={13} className="text-muted" />}
      </button>
      {expanded && (
        <div className="p-3 space-y-2">
          {issues.map((issue, i) => (
            <IssueItem key={i} issue={issue} />
          ))}
        </div>
      )}
    </div>
  );
}

export function GrammarPanel({ grammar }: Props) {
  if (!grammar) return null;

  const scoreColor = getScoreColor(grammar.overall_score);

  const errorIssues = grammar.issues.filter(i => i.severity === 'error');
  const warningIssues = grammar.issues.filter(i => i.severity === 'warning');
  const suggestionIssues = grammar.issues.filter(i => i.severity === 'suggestion');

  return (
    <div className="card p-5 animate-in">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <SpellCheck size={14} className="text-primary" />
          <h3 className="text-sm font-semibold">Grammar & Writing Quality</h3>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="mono text-lg font-bold"
            style={{ color: scoreColor }}
          >
            {grammar.overall_score}
          </span>
          <span className="text-[10px] text-muted">/100</span>
        </div>
      </div>

      {/* Summary badges */}
      <div className="flex items-center gap-2 mb-4">
        {grammar.error_count > 0 && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-danger/10 text-danger rounded-full text-[10px] font-medium">
            <AlertCircle size={10} /> {grammar.error_count} error{grammar.error_count !== 1 ? 's' : ''}
          </span>
        )}
        {grammar.warning_count > 0 && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-warning/10 text-warning rounded-full text-[10px] font-medium">
            <AlertTriangle size={10} /> {grammar.warning_count} warning{grammar.warning_count !== 1 ? 's' : ''}
          </span>
        )}
        {grammar.suggestion_count > 0 && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary/10 text-primary rounded-full text-[10px] font-medium">
            <Lightbulb size={10} /> {grammar.suggestion_count} suggestion{grammar.suggestion_count !== 1 ? 's' : ''}
          </span>
        )}
        {grammar.issue_count === 0 && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-success/10 text-success rounded-full text-[10px] font-medium">
            No issues found
          </span>
        )}
      </div>

      {/* Issue groups */}
      {grammar.issue_count > 0 && (
        <div className="space-y-2">
          <IssueGroup severity="error" issues={errorIssues} />
          <IssueGroup severity="warning" issues={warningIssues} />
          <IssueGroup severity="suggestion" issues={suggestionIssues} />
        </div>
      )}
    </div>
  );
}
