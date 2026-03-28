export const COLORS = {
  primary: '#2563EB',
  success: '#16A34A',
  warning: '#D97706',
  danger: '#DC2626',
  bg: '#0F172A',
  surface: '#1E293B',
  text: '#F8FAFC',
  muted: '#94A3B8',
} as const;

export const SCORE_COLORS = {
  high: '#16A34A',
  medium: '#D97706',
  low: '#DC2626',
} as const;

export function getScoreColor(score: number, inverted = false): string {
  const effective = inverted ? 100 - score : score;
  if (effective >= 70) return SCORE_COLORS.high;
  if (effective >= 40) return SCORE_COLORS.medium;
  return SCORE_COLORS.low;
}

export function getSignalColor(score: number, max: number): string {
  const pct = (score / max) * 100;
  if (pct >= 60) return SCORE_COLORS.low;
  if (pct >= 25) return SCORE_COLORS.medium;
  return SCORE_COLORS.high;
}
