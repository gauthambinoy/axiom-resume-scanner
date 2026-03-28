import type { ScanResponse } from '../../types';
import { ScoreGauge } from './ScoreGauge';
import { ATSPanel } from './ATSPanel';
import { AIDetectionPanel } from './AIDetectionPanel';
import { BulletAnalysis } from './BulletAnalysis';
import { FixSuggestions } from './FixSuggestions';
import { KeywordGrid } from './KeywordGrid';
import { ExportButton } from './ExportButton';
import { formatMs } from '../../utils/formatters';

const READINESS_LABELS: Record<string, { label: string; color: string }> = {
  INTERVIEW_READY: { label: 'Interview Ready', color: '#16A34A' },
  NEEDS_WORK: { label: 'Needs Work', color: '#D97706' },
  AT_RISK: { label: 'At Risk', color: '#DC2626' },
};

export function ResultsDashboard({ result }: { result: ScanResponse }) {
  const readiness = READINESS_LABELS[result.combined.readiness_level] || READINESS_LABELS.AT_RISK;

  return (
    <div className="space-y-6">
      {/* Top Row: Score Gauges */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Scan Results</h2>
        <div className="flex items-center gap-4">
          <span className="text-xs text-muted">Processed in {formatMs(result.metadata.processing_time_ms)}</span>
          <ExportButton />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-surface rounded-xl p-6 border border-surface-light flex justify-center">
          <ScoreGauge
            score={result.ats_score.overall_score}
            label="ATS Score"
            subtitle={`Grade: ${result.ats_score.grade}`}
          />
        </div>
        <div className="bg-surface rounded-xl p-6 border border-surface-light flex justify-center">
          <ScoreGauge
            score={result.ai_score.overall_score}
            label="AI Detection Risk"
            subtitle={result.ai_score.risk_level}
            inverted
          />
        </div>
        <div className="bg-surface rounded-xl p-6 border border-surface-light flex justify-center">
          <ScoreGauge
            score={result.combined.interview_readiness_score}
            label="Interview Readiness"
            subtitle={readiness.label}
          />
        </div>
      </div>

      {/* Percentile */}
      <div className="bg-surface rounded-xl p-4 border border-surface-light text-center">
        <p className="text-sm text-muted">
          Your resume scores higher than approximately <strong className="text-text">{result.combined.competitor_percentile}%</strong> of applicants
        </p>
      </div>

      {/* Detailed Breakdowns */}
      <div className="grid md:grid-cols-2 gap-6">
        <ATSPanel ats={result.ats_score} />
        <AIDetectionPanel ai={result.ai_score} />
      </div>

      {/* Bullet Analysis */}
      <BulletAnalysis bullets={result.ai_score.per_bullet_analysis} />

      {/* Fix Suggestions */}
      <FixSuggestions fixes={result.fixes} />

      {/* Keyword Grid */}
      <KeywordGrid ats={result.ats_score} />

      {/* Warnings */}
      {result.metadata.warnings.length > 0 && (
        <div className="bg-warning/10 border border-warning/30 rounded-xl p-4">
          <p className="text-sm font-medium text-warning mb-2">Warnings</p>
          {result.metadata.warnings.map((w, i) => (
            <p key={i} className="text-xs text-warning/80">{w}</p>
          ))}
        </div>
      )}
    </div>
  );
}
