import { useState, useCallback, useEffect } from 'react';
import type { ScanResponse } from '../types';

const STORAGE_KEY = 'resumeshield_history';
const MAX_HISTORY = 5;

export function useHistory() {
  const [history, setHistory] = useState<ScanResponse[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) setHistory(JSON.parse(stored));
    } catch { /* ignore */ }
  }, []);

  const addScan = useCallback((scan: ScanResponse) => {
    setHistory((prev) => {
      const next = [scan, ...prev].slice(0, MAX_HISTORY);
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch { /* */ }
      return next;
    });
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const getScan = useCallback(
    (scanId: string) => history.find((s) => s.scan_id === scanId) ?? null,
    [history]
  );

  return { history, addScan, clearHistory, getScan };
}
