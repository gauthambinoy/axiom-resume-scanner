import { useState } from 'react';
import { ResumeInput } from './ResumeInput';
import { JDInput } from './JDInput';
import { FileUpload } from './FileUpload';
import { ScanButton } from './ScanButton';
import { ResultsDashboard } from '../Results/ResultsDashboard';
import { useScan } from '../../hooks/useScan';
import { useFileUpload } from '../../hooks/useFileUpload';
import { validateResumeText, validateJDText } from '../../utils/validators';
import { ArrowLeft, FileText, Type } from 'lucide-react';

export function ScannerPage() {
  const [resumeText, setResumeText] = useState('');
  const [jdText, setJdText] = useState('');
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [jdError, setJdError] = useState<string | null>(null);
  const [mode, setMode] = useState<'text' | 'file'>('text');

  const { scanResult, isLoading, error, scan, scanWithFile, reset } = useScan();
  const { file, handleFile, removeFile, error: fileError } = useFileUpload();

  const handleScan = async () => {
    setResumeError(null);
    setJdError(null);
    const jdErr = validateJDText(jdText);
    if (jdErr) { setJdError(jdErr); return; }
    if (mode === 'file' && file) {
      await scanWithFile(file, jdText);
    } else {
      const rErr = validateResumeText(resumeText);
      if (rErr) { setResumeError(rErr); return; }
      await scan(resumeText, jdText);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleScan();
  };

  const handleRescan = async (humanizedText: string) => {
    setResumeText(humanizedText);
    await scan(humanizedText, jdText);
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
          jdText={jdText}
          onRescan={handleRescan}
        />
      </div>
    );
  }

  return (
    <section id="scanner" className="max-w-5xl mx-auto px-6 py-16" onKeyDown={handleKeyDown}>
      <div className="mb-8">
        <p className="text-xs font-medium text-primary uppercase tracking-widest mb-2">Scanner</p>
        <h2 className="text-xl font-semibold tracking-tight">Paste & scan</h2>
      </div>

      <div className="grid md:grid-cols-2 gap-5 mb-5">
        <div>
          {/* Mode toggle */}
          <div className="flex items-center gap-1 mb-3 p-0.5 bg-surface rounded-lg w-fit border border-border">
            <button
              onClick={() => setMode('text')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition ${
                mode === 'text' ? 'bg-surface-light text-text' : 'text-muted hover:text-text'
              }`}
            >
              <Type size={11} /> Text
            </button>
            <button
              onClick={() => setMode('file')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition ${
                mode === 'file' ? 'bg-surface-light text-text' : 'text-muted hover:text-text'
              }`}
            >
              <FileText size={11} /> File
            </button>
          </div>

          {mode === 'file' ? (
            <FileUpload file={file} onFile={handleFile} onRemove={removeFile} error={fileError} />
          ) : (
            <ResumeInput value={resumeText} onChange={setResumeText} error={resumeError} />
          )}
        </div>

        <JDInput value={jdText} onChange={setJdText} error={jdError} />
      </div>

      <ScanButton
        onClick={handleScan}
        isLoading={isLoading}
        disabled={(mode === 'text' && !resumeText.trim()) || (mode === 'file' && !file) || !jdText.trim()}
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
