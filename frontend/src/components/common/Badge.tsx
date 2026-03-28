import type { Priority, RiskLevel } from '../../types';

const PRIORITY_STYLES: Record<Priority, string> = {
  critical: 'bg-red-600/20 text-red-400 border-red-600/30',
  high: 'bg-orange-600/20 text-orange-400 border-orange-600/30',
  medium: 'bg-yellow-600/20 text-yellow-400 border-yellow-600/30',
  low: 'bg-blue-600/20 text-blue-400 border-blue-600/30',
};

const RISK_STYLES: Record<RiskLevel, string> = {
  LOW: 'bg-green-600/20 text-green-400',
  MODERATE: 'bg-yellow-600/20 text-yellow-400',
  HIGH: 'bg-orange-600/20 text-orange-400',
  CRITICAL: 'bg-red-600/20 text-red-400',
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span className={`px-2 py-0.5 text-xs font-medium rounded-md border ${PRIORITY_STYLES[priority]}`}>
      {priority.toUpperCase()}
    </span>
  );
}

export function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <span className={`px-2 py-0.5 text-xs font-medium rounded-md ${RISK_STYLES[level]}`}>
      {level}
    </span>
  );
}
