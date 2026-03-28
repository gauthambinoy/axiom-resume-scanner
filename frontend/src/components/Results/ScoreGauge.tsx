import { useEffect, useState } from 'react';
import { getScoreColor } from '../../utils/constants';

interface Props {
  score: number;
  label: string;
  subtitle?: string;
  inverted?: boolean;
  size?: number;
}

export function ScoreGauge({ score, label, subtitle, inverted = false, size = 160 }: Props) {
  const [animated, setAnimated] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  const r = (size - 16) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (animated / 100) * circ;
  const color = getScoreColor(score, inverted);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#334155" strokeWidth={8} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="relative -mt-[calc(50%+12px)] flex flex-col items-center justify-center" style={{ height: size }}>
        <span className="text-3xl font-bold" style={{ color }}>{Math.round(animated)}</span>
        <span className="text-xs text-muted">/100</span>
      </div>
      <p className="font-semibold mt-2">{label}</p>
      {subtitle && <p className="text-xs text-muted">{subtitle}</p>}
    </div>
  );
}
