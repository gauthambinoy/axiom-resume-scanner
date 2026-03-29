import { useState, useEffect, useRef, useCallback } from 'react';
import { ResumeInput } from './ResumeInput';
import { JDInput } from './JDInput';
import { FileUpload } from './FileUpload';
import { ScanButton } from './ScanButton';
import { ResultsDashboard } from '../Results/ResultsDashboard';
import { useScan } from '../../hooks/useScan';
import { useFileUpload } from '../../hooks/useFileUpload';
import { validateResumeText, validateJDText } from '../../utils/validators';
import { quickScan } from '../../services/api';
import { ArrowLeft, FileText, Type, FileEdit, Mail, Globe, BookOpen, Loader2 } from 'lucide-react';
import type { ContentMode } from '../../types';

const CONTENT_MODES: { value: ContentMode; label: string; icon: typeof Type }[] = [
  { value: 'resume', label: 'Resume', icon: FileText },
  { value: 'essay', label: 'Essay', icon: BookOpen },
  { value: 'blog', label: 'Blog', icon: Globe },
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'general', label: 'General', icon: FileEdit },
];

function getQuickScoreColor(score: number): string {
  if (score < 25) return '#10B981';
  if (score < 50) return '#F59E0B';
  if (score < 75) return '#F97316';
  return '#EF4444';
}

export function ScannerPage() {
  const [resumeText, setResumeText] = useState('');
  const [jdText, setJdText] = useState('');
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [jdError, setJdError] = useState<string | null>(null);
  const [inputMode, setInputMode] = useState<'text' | 'file'>('text');
  const [contentMode, setContentMode] = useState<ContentMode>('resume');

  // Real-time AI score state
  const [quickScore, setQuickScore] = useState<number | null>(null);
  const [quickScoreLoading, setQuickScoreLoading] = useState(false);
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const { scanResult, isLoading, error, scan, scanWithFile, reset } = useScan();
  const { file, handleFile, removeFile, error: fileError } = useFileUpload();

  // Debounced quick score
  const triggerQuickScore = useCallback((text: string) => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    if (abortRef.current) abortRef.current.abort();

    if (text.length < 100) {
      setQuickScore(null);
      setQuickScoreLoading(false);
      return;
    }

    debounceTimer.current = setTimeout(async () => {
      setQuickScoreLoading(true);
      try {
        const result = await quickScan(text, '', contentMode);
        setQuickScore(result.ai_detection_score);
      } catch {
        // silent fail for quick score
      } finally {
        setQuickScoreLoading(false);
      }
    }, 1500);
  }, [contentMode]);

  useEffect(() => {
    if (inputMode === 'text') {
      triggerQuickScore(resumeText);
    }
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [resumeText, triggerQuickScore, inputMode]);

  const handleScan = async () => {
    setResumeError(null);
    setJdError(null);

    if (contentMode === 'resume') {
      const jdErr = validateJDText(jdText);
      if (jdErr) { setJdError(jdErr); return; }
    }

    if (inputMode === 'file' && file) {
      await scanWithFile(file, contentMode === 'resume' ? jdText : '', contentMode);
    } else {
      const rErr = validateResumeText(resumeText);
      if (rErr) { setResumeError(rErr); return; }
      await scan(resumeText, contentMode === 'resume' ? jdText : '', contentMode);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleScan();
  };

  const handleRescan = async (humanizedText: string) => {
    setResumeText(humanizedText);
    await scan(humanizedText, contentMode === 'resume' ? jdText : '', contentMode);
  };

  if (scanResult) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-10">
        <button onClick={reset} className="flex items-center gap-1.5 text-xs text-muted hover:text-text mb-8 transition">
          <ArrowLeft size={12} /> New scan
        </button>
        <ResultsDashboard
          result={scanResult}
          resumeText={resumeText}
          jdText={contentMode === 'resume' ? jdText : ''}
          onRescan={handleRescan}
        />
      </div>
    );
  }

  const isResumeMode = contentMode === 'resume';
  const canScan = inputMode === 'text'
    ? resumeText.trim() && (isResumeMode ? jdText.trim() : true)
    : file && (isResumeMode ? jdText.trim() : true);

  return (
    <section id="scanner" className="max-w-5xl mx-auto px-6 py-16" onKeyDown={handleKeyDown}>
      <div className="mb-8">
        <p className="text-xs font-medium text-primary uppercase tracking-widest mb-2">Scanner</p>
        <h2 className="text-xl font-semibold tracking-tight">Paste & scan</h2>
      </div>

      {/* Content Mode Toggle */}
      <div className="flex items-center gap-1 mb-5 p-0.5 bg-surface rounded-full w-fit border border-border">
        {CONTENT_MODES.map(({ value, label, icon: Icon }) => (
          <button
            key={value}
            onClick={() => setContentMode(value)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-medium transition ${
              contentMode === value
                ? 'bg-primary text-white shadow-sm'
                : 'text-muted hover:text-text'
            }`}
          >
            <Icon size={11} /> {label}
          </button>
        ))}
      </div>

      <div className={`grid ${isResumeMode ? 'md:grid-cols-2' : 'md:grid-cols-1'} gap-5 mb-5`}>
        <div className="relative">
          {/* Input mode toggle (text/file) */}
          <div className="flex items-center gap-1 mb-3 p-0.5 bg-surface rounded-lg w-fit border border-border">
            <button
              onClick={() => setInputMode('text')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition ${
                inputMode === 'text' ? 'bg-surface-light text-text' : 'text-muted hover:text-text'
              }`}
            >
              <Type size={11} /> Text
            </button>
            <button
              onClick={() => setInputMode('file')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition ${
                inputMode === 'file' ? 'bg-surface-light text-text' : 'text-muted hover:text-text'
              }`}
            >
              <FileText size={11} /> File
            </button>
          </div>

          {inputMode === 'file' ? (
            <FileUpload file={file} onFile={handleFile} onRemove={removeFile} error={fileError} />
          ) : (
            <ResumeInput value={resumeText} onChange={setResumeText} error={resumeError} />
          )}

          {/* Real-time AI Score Badge */}
          {inputMode === 'text' && resumeText.length >= 100 && (
            <div className="absolute top-12 right-2 z-10">
              <div className="flex items-center justify-center w-12 h-12 rounded-full border-2 bg-bg shadow-lg"
                style={{ borderColor: quickScoreLoading ? '#6366F1' : (quickScore !== null ? getQuickScoreColor(quickScore) : '#6366F1') }}
              >
                {quickScoreLoading ? (
                  <Loader2 size={16} className="text-primary animate-spin" />
                ) : quickScore !== null ? (
                  <span className="text-xs font-bold mono" style={{ color: getQuickScoreColor(quickScore) }}>
                    {Math.round(quickScore)}
                  </span>
                ) : null}
              </div>
              <p className="text-center text-[8px] text-muted mt-0.5">
                {quickScoreLoading ? 'Analyzing...' : quickScore !== null ? 'AI Risk' : ''}
              </p>
            </div>
          )}
        </div>

        {isResumeMode && (
          <JDInput value={jdText} onChange={setJdText} error={jdError} />
        )}
      </div>

      <ScanButton
        onClick={handleScan}
        isLoading={isLoading}
        disabled={!canScan}
      />

      {error && (
        <div className="mt-3 px-4 py-3 bg-danger-dim border border-danger/20 rounded-xl text-danger text-xs">
          {error}
        </div>
      )}

      <p className="text-center text-[10px] text-muted mt-3">
        <kbd className="px-1 py-0.5 bg-surface border border-border rounded text-[9px]">Ctrl</kbd> + <kbd className="px-1 py-0.5 bg-surface border border-border rounded text-[9px]">Enter</kbd> to scan
      </p>
    </section>
  );
}
