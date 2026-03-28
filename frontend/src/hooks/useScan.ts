import { useState, useCallback } from 'react';
import type { ScanResponse } from '../types';
import { scanResume, scanFile } from '../services/api';

type ScanState = 'idle' | 'loading' | 'success' | 'error';

export function useScan() {
  const [state, setState] = useState<ScanState>('idle');
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scan = useCallback(async (resumeText: string, jdText: string) => {
    setState('loading');
    setError(null);
    try {
      const result = await scanResume(resumeText, jdText);
      setScanResult(result);
      setState('success');
      try {
        localStorage.setItem('lastScan', JSON.stringify(result));
      } catch { /* quota exceeded */ }
      return result;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Scan failed';
      setError(msg);
      setState('error');
      return null;
    }
  }, []);

  const scanWithFile = useCallback(async (file: File, jdText: string) => {
    setState('loading');
    setError(null);
    try {
      const result = await scanFile(file, jdText);
      setScanResult(result);
      setState('success');
      return result;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Scan failed';
      setError(msg);
      setState('error');
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState('idle');
    setScanResult(null);
    setError(null);
  }, []);

  return {
    state,
    scanResult,
    isLoading: state === 'loading',
    error,
    scan,
    scanWithFile,
    reset,
  };
}
