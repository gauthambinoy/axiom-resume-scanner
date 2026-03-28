export const COLORS = {
  primary: '#6366F1',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
} as const;

export function getScoreColor(score: number, inverted = false): string {
  const effective = inverted ? 100 - score : score;
  if (effective >= 70) return COLORS.success;
  if (effective >= 40) return COLORS.warning;
  return COLORS.danger;
}

export function getSignalColor(score: number, max: number): string {
  const pct = (score / max) * 100;
  if (pct >= 60) return COLORS.danger;
  if (pct >= 25) return COLORS.warning;
  return COLORS.success;
}
