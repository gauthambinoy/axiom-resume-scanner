import { useEffect, useState } from 'react';
import { getScoreColor } from '../../utils/constants';

interface Props {
  score: number;
  label: string;
  subtitle?: string;
  inverted?: boolean;
}

export function ScoreGauge({ score, label, subtitle, inverted = false }: Props) {
  const [animated, setAnimated] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(score), 50);
    return () => clearTimeout(timer);
  }, [score]);

  const size = 120;
  const stroke = 5;
  const r = (size - stroke * 2) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (animated / 100) * circ;
  const color = getScoreColor(score, inverted);

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2} cy={size / 2} r={r}
            fill="none" stroke="currentColor" strokeWidth={stroke}
            className="text-surface-light"
          />
          <circle
            cx={size / 2} cy={size / 2} r={r}
            fill="none" stroke={color} strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            className="transition-all duration-[1200ms] ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold mono" style={{ color }}>{Math.round(animated)}</span>
        </div>
      </div>
      <p className="text-xs font-medium mt-2">{label}</p>
      {subtitle && <p className="text-[10px] text-muted">{subtitle}</p>}
    </div>
  );
}
