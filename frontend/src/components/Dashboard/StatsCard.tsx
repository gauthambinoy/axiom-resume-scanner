interface Props { label: string; value: string | number; }

export function StatsCard({ label, value }: Props) {
  return (
    <div className="bg-surface border border-surface-light rounded-xl p-4 text-center">
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs text-muted mt-1">{label}</p>
    </div>
  );
}
