import { useState, useCallback } from 'react';
import type { HumanizeResponse, HumanizeTone } from '../../types';
import { humanizeResume } from '../../services/api';
import { Sparkles, Copy, Check, RefreshCw, ArrowRight, AlertTriangle } from 'lucide-react';
import { getScoreColor } from '../../utils/constants';

const TONE_OPTIONS: { value: HumanizeTone; label: string }[] = [
  { value: 'formal', label: 'Formal' },
  { value: 'casual', label: 'Casual' },
  { value: 'academic', label: 'Academic' },
  { value: 'professional', label: 'Professional' },
  { value: 'creative', label: 'Creative' },
];

interface Props {
  aiScore: number;
  riskLevel: string;
  resumeText: string;
  jdText: string;
  onRescan?: (text: string) => void;
}

export function HumanizePanel({ aiScore, riskLevel, resumeText, jdText, onRescan }: Props) {
  const [state, setState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [result, setResult] = useState<HumanizeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [tone, setTone] = useState<HumanizeTone>('professional');

  const handleHumanize = useCallback(async () => {
    setState('loading');
    setError(null);
    try {
      const data = await humanizeResume(resumeText, jdText, tone);
      setResult(data);
      setState('success');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Humanization failed';
      setError(msg);
      setState('error');
    }
  }, [resumeText, jdText, tone]);

  const handleCopy = useCallback(async () => {
    if (!result) return;
    try {
      await navigator.clipboard.writeText(result.humanized_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard not available */
    }
  }, [result]);

  const handleRescan = useCallback(() => {
    if (result && onRescan) {
      onRescan(result.humanized_text);
    }
  }, [result, onRescan]);

  // Only show when AI score is above 30
  if (aiScore <= 30) return null;

  const isModerate = riskLevel === 'MODERATE';
  const borderColor = isModerate ? 'border-warning/30' : 'border-danger/30';
  const bgAccent = isModerate ? 'bg-warning-dim' : 'bg-danger-dim';

  // Idle / CTA state
  if (state === 'idle' || state === 'error') {
    return (
      <div className={`card p-5 ${borderColor} animate-in`}>
        <div className="flex items-start gap-4">
          <div className={`shrink-0 p-2.5 rounded-xl ${bgAccent}`}>
            <AlertTriangle size={18} className={isModerate ? 'text-warning' : 'text-danger'} />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold mb-1">Your resume scored {aiScore.toFixed(0)} on AI detection</h3>
            <p className="text-[11px] text-muted leading-relaxed mb-4">
              Many ATS systems now flag AI-generated content. Humanize your resume to reduce detection risk
              while preserving your qualifications and keywords.
            </p>
            <div className="flex items-center gap-3">
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value as HumanizeTone)}
                className="px-2.5 py-2 bg-bg border border-border rounded-lg text-[11px] text-text-secondary
                           focus:outline-none focus:ring-1 focus:ring-primary/40 focus:border-primary/40 transition"
              >
                {TONE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
              <button
                onClick={handleHumanize}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold
                           bg-primary text-white hover:bg-primary-light transition shadow-md shadow-primary/20"
              >
                <Sparkles size={13} />
                Humanize My Resume
              </button>
            </div>
            {state === 'error' && error && (
              <p className="mt-3 text-[11px] text-danger">{error}</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Loading state
  if (state === 'loading') {
    return (
      <div className={`card p-5 ${borderColor} animate-in`}>
        <div className="flex items-center gap-4">
          <div className="shrink-0 p-2.5 rounded-xl bg-primary-dim">
            <Sparkles size={18} className="text-primary animate-pulse" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold mb-1">Humanizing your resume...</h3>
            <p className="text-[11px] text-muted">This may take 15-30 seconds. We are rewriting flagged patterns while preserving your content.</p>
            <div className="mt-3 h-1 w-full bg-surface-light rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full animate-pulse" style={{ width: '60%' }} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Success state with results
  if (!result) return null;

  const origColor = getScoreColor(result.original_ai_score, true);
  const newColor = getScoreColor(result.new_ai_score, true);

  return (
    <div className="card p-5 border-success/30 animate-in space-y-5">
      {/* Score improvement header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-success-dim">
            <Sparkles size={18} className="text-success" />
          </div>
          <div>
            <h3 className="text-sm font-semibold">Resume Humanized</h3>
            <p className="text-[10px] text-muted">
              AI score reduced by {result.improvement.toFixed(1)} points
              {result.retries_used > 0 && ` (${result.retries_used} retry used)`}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-medium
                       bg-surface-light hover:bg-surface-hover text-text-secondary hover:text-text transition"
          >
            {copied ? <Check size={12} className="text-success" /> : <Copy size={12} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
          {onRescan && (
            <button
              onClick={handleRescan}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-medium
                         bg-primary-dim text-primary hover:bg-primary/20 transition"
            >
              <RefreshCw size={12} />
              Re-scan
            </button>
          )}
        </div>
      </div>

      {/* Score comparison */}
      <div className="flex items-center justify-center gap-6 py-3 bg-bg rounded-xl border border-border">
        <div className="text-center">
          <p className="text-[10px] text-muted mb-1">Original AI Score</p>
          <p className="text-2xl font-bold mono" style={{ color: origColor }}>
            {result.original_ai_score.toFixed(0)}
          </p>
        </div>
        <ArrowRight size={20} className="text-muted" />
        <div className="text-center">
          <p className="text-[10px] text-muted mb-1">New AI Score</p>
          <p className="text-2xl font-bold mono" style={{ color: newColor }}>
            {result.new_ai_score.toFixed(0)}
          </p>
        </div>
        <div className="text-center pl-6 border-l border-border">
          <p className="text-[10px] text-muted mb-1">Improvement</p>
          <p className="text-2xl font-bold mono text-success">
            -{result.improvement.toFixed(0)}
          </p>
        </div>
      </div>

      {/* Before / After comparison */}
      <div>
        <p className="text-[11px] font-medium text-muted mb-2">Before vs After</p>
        <div className="grid md:grid-cols-2 gap-3">
          <div className="bg-bg rounded-xl border border-border p-4 max-h-64 overflow-y-auto">
            <p className="text-[10px] font-semibold text-danger/80 uppercase tracking-wider mb-2">Original</p>
            <p className="text-[11px] text-text-secondary leading-relaxed whitespace-pre-wrap mono">
              {result.original_text}
            </p>
          </div>
          <div className="bg-bg rounded-xl border border-success/20 p-4 max-h-64 overflow-y-auto">
            <p className="text-[10px] font-semibold text-success/80 uppercase tracking-wider mb-2">Humanized</p>
            <p className="text-[11px] text-text-secondary leading-relaxed whitespace-pre-wrap mono">
              {result.humanized_text}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
