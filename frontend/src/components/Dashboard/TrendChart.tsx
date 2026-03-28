import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import type { ScanResponse } from '../../types';

export function TrendChart({ scans }: { scans: ScanResponse[] }) {
  const data = scans.map((s, i) => ({
    scan: i + 1,
    ats: s.ats_score.overall_score,
    ai: Math.round(s.ai_score.overall_score),
  })).reverse();

  if (data.length < 2) return null;

  return (
    <div className="bg-surface border border-surface-light rounded-xl p-6">
      <h3 className="font-semibold mb-4">Score Trend</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <XAxis dataKey="scan" stroke="#94A3B8" fontSize={12} />
          <YAxis stroke="#94A3B8" fontSize={12} domain={[0, 100]} />
          <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8 }} />
          <Line type="monotone" dataKey="ats" stroke="#2563EB" strokeWidth={2} name="ATS" />
          <Line type="monotone" dataKey="ai" stroke="#DC2626" strokeWidth={2} name="AI Risk" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
