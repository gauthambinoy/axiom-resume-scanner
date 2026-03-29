import type { TextAnalytics, ReadabilityScore } from '../../types';
import { BarChart3, BookOpen, Clock, Hash, Type, Gauge } from 'lucide-react';

interface Props {
  analytics?: TextAnalytics;
  readability?: ReadabilityScore;
}

function formatTime(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`;
}

function getGradeLabel(grade: number): string {
  if (grade <= 6) return 'Easy';
  if (grade <= 10) return 'Medium';
  if (grade <= 14) return 'Hard';
  return 'Very Hard';
}

function getGradeColor(grade: number): string {
  if (grade <= 6) return 'text-success';
  if (grade <= 10) return 'text-primary';
  if (grade <= 14) return 'text-warning';
  return 'text-danger';
}

export function WordAnalytics({ analytics, readability }: Props) {
  if (!analytics && !readability) return null;

  const stats = [
    { label: 'Words', value: analytics?.word_count ?? readability?.word_count ?? 0, icon: Type },
    { label: 'Characters', value: analytics?.character_count ?? 0, icon: Hash },
    { label: 'Sentences', value: analytics?.sentence_count ?? readability?.sentence_count ?? 0, icon: BarChart3 },
    { label: 'Avg Sentence', value: `${(analytics?.avg_sentence_length ?? readability?.avg_sentence_length ?? 0).toFixed(1)} words`, icon: BarChart3 },
    { label: 'Vocabulary', value: `${((analytics?.vocabulary_richness ?? readability?.vocabulary_richness ?? 0) * 100).toFixed(1)}%`, icon: BookOpen },
    ...(readability ? [
      { label: 'Reading Time', value: formatTime(readability.reading_time_seconds), icon: Clock },
    ] : []),
  ];

  return (
    <div className="card p-5 animate-in">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 size={14} className="text-primary" />
        <h3 className="text-sm font-semibold">Word Analytics</h3>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
        {stats.map(({ label, value, icon: Icon }) => (
          <div key={label} className="bg-bg rounded-xl border border-border px-3 py-2.5">
            <div className="flex items-center gap-1.5 mb-1">
              <Icon size={10} className="text-muted" />
              <p className="text-[10px] text-muted">{label}</p>
            </div>
            <p className="text-sm font-semibold mono">{typeof value === 'number' ? value.toLocaleString() : value}</p>
          </div>
        ))}
      </div>

      {/* Readability Grade */}
      {readability && (
        <div className="bg-bg rounded-xl border border-border px-4 py-3 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gauge size={14} className="text-primary" />
              <div>
                <p className="text-[10px] text-muted">Flesch-Kincaid Grade</p>
                <p className="text-sm font-semibold mono">{readability.flesch_kincaid_grade.toFixed(1)}</p>
              </div>
            </div>
            <span className={`text-xs font-medium ${getGradeColor(readability.flesch_kincaid_grade)}`}>
              {getGradeLabel(readability.flesch_kincaid_grade)}
            </span>
          </div>
        </div>
      )}

      {/* Top Words */}
      {analytics?.top_words && analytics.top_words.length > 0 && (
        <div>
          <p className="text-[10px] font-medium text-muted mb-2">Top Words</p>
          <div className="flex flex-wrap gap-1.5">
            {analytics.top_words.slice(0, 10).map(([word, count]) => (
              <span
                key={word}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary-dim text-primary rounded-full text-[10px] font-medium"
              >
                {word}
                <span className="text-primary/60">{count}</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
