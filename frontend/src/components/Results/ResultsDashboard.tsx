import type { ScanResponse } from '../../types';
import { ScoreGauge } from './ScoreGauge';
import { ATSPanel } from './ATSPanel';
import { AIDetectionPanel } from './AIDetectionPanel';
import { BulletAnalysis } from './BulletAnalysis';
import { FixSuggestions } from './FixSuggestions';
import { KeywordGrid } from './KeywordGrid';
import { ExportButton } from './ExportButton';
import { formatMs } from '../../utils/formatters';
import { Clock, TrendingUp } from 'lucide-react';

const READINESS: Record<string, { label: string; color: string }> = {
  INTERVIEW_READY: { label: 'Ready', color: '#10B981' },
  NEEDS_WORK: { label: 'Needs work', color: '#F59E0B' },
  AT_RISK: { label: 'At risk', color: '#EF4444' },
};

export function ResultsDashboard({ result }: { result: ScanResponse }) {
  const readiness = READINESS[result.combined.readiness_level] || READINESS.AT_RISK;

  return (
    <div className="space-y-5 animate-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">Results</h2>
          <div className="flex items-center gap-3 mt-1 text-[10px] text-muted">
            <span className="flex items-center gap-1"><Clock size={10} /> {formatMs(result.metadata.processing_time_ms)}</span>
            <span className="flex items-center gap-1">
              <TrendingUp size={10} /> Top {100 - result.combined.competitor_percentile}% of applicants
            </span>
          </div>
        </div>
        <ExportButton />
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-3 gap-3">
        <div className="card-elevated p-5 flex justify-center">
          <ScoreGauge
            score={result.ats_score.overall_score}
            label="ATS Score"
            subtitle={result.ats_score.grade}
          />
        </div>
        <div className="card-elevated p-5 flex justify-center">
          <ScoreGauge
            score={result.ai_score.overall_score}
            label="AI Risk"
            subtitle={result.ai_score.risk_level.toLowerCase()}
            inverted
          />
        </div>
        <div className="card-elevated p-5 flex justify-center">
          <ScoreGauge
            score={result.combined.interview_readiness_score}
            label="Readiness"
            subtitle={readiness.label}
          />
        </div>
      </div>

      {/* Breakdowns */}
      <div className="grid md:grid-cols-2 gap-3">
        <ATSPanel ats={result.ats_score} />
        <AIDetectionPanel ai={result.ai_score} />
      </div>

      {/* Keywords */}
      <KeywordGrid ats={result.ats_score} />

      {/* Bullet Analysis */}
      <BulletAnalysis bullets={result.ai_score.per_bullet_analysis} />

      {/* Fixes */}
      <FixSuggestions fixes={result.fixes} />

      {/* Warnings */}
      {result.metadata.warnings.length > 0 && (
        <div className="card px-4 py-3 border-warning/20">
          {result.metadata.warnings.map((w, i) => (
            <p key={i} className="text-[11px] text-warning">{w}</p>
          ))}
        </div>
      )}
    </div>
  );
}
