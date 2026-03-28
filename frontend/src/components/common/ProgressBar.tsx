interface Props { value: number; max?: number; color?: string; label?: string; }

export function ProgressBar({ value, max = 100, color = '#2563EB', label }: Props) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div className="w-full">
      {label && <div className="flex justify-between text-sm text-muted mb-1"><span>{label}</span><span>{Math.round(pct)}%</span></div>}
      <div className="w-full h-2 bg-surface-light rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}
