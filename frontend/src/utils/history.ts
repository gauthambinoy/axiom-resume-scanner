import type { ScanResponse, Grade, ReadinessLevel } from '../types';

const STORAGE_KEY = 'resumeshield_history';
const MAX_ENTRIES = 50;

export interface ScanHistoryEntry {
  id: string;
  timestamp: string;
  mode: string;
  ats_score: number;
  ai_score: number;
  readiness_score: number;
  readiness_level: ReadinessLevel;
  text_preview: string;
  grade: Grade;
}

export function saveScanToHistory(result: ScanResponse, mode: string, resumeText?: string): void {
  const entry: ScanHistoryEntry = {
    id: result.scan_id || crypto.randomUUID(),
    timestamp: result.timestamp || new Date().toISOString(),
    mode,
    ats_score: result.ats_score.overall_score,
    ai_score: result.ai_score.overall_score,
    readiness_score: result.combined.interview_readiness_score,
    readiness_level: result.combined.readiness_level,
    text_preview: (resumeText || '').slice(0, 100),
    grade: result.ats_score.grade,
  };

  const history = getScanHistory();
  history.unshift(entry);

  // Auto-prune to max entries
  const pruned = history.slice(0, MAX_ENTRIES);

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(pruned));
  } catch {
    // localStorage full — drop oldest half and retry
    const halved = pruned.slice(0, Math.floor(MAX_ENTRIES / 2));
    localStorage.setItem(STORAGE_KEY, JSON.stringify(halved));
  }
}

export function getScanHistory(): ScanHistoryEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: ScanHistoryEntry[] = JSON.parse(raw);
    return parsed.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  } catch {
    return [];
  }
}

export function clearHistory(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export function deleteScanFromHistory(id: string): void {
  const history = getScanHistory().filter((entry) => entry.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}
