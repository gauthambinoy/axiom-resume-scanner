import { useState } from 'react';
import { ResumeInput } from './ResumeInput';
import { JDInput } from './JDInput';
import { FileUpload } from './FileUpload';
import { ScanButton } from './ScanButton';
import { ResultsDashboard } from '../Results/ResultsDashboard';
import { useScan } from '../../hooks/useScan';
import { useFileUpload } from '../../hooks/useFileUpload';
import { validateResumeText, validateJDText } from '../../utils/validators';

export function ScannerPage() {
  const [resumeText, setResumeText] = useState('');
  const [jdText, setJdText] = useState('');
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [jdError, setJdError] = useState<string | null>(null);
  const [useFile, setUseFile] = useState(false);

  const { scanResult, isLoading, error, scan, scanWithFile, reset } = useScan();
  const { file, handleFile, removeFile, error: fileError } = useFileUpload();

  const handleScan = async () => {
    setResumeError(null);
    setJdError(null);

    const jdErr = validateJDText(jdText);
    if (jdErr) { setJdError(jdErr); return; }

    if (useFile && file) {
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

  if (scanResult) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <button onClick={reset} className="mb-6 text-sm text-primary hover:underline">
          &larr; New Scan
        </button>
        <ResultsDashboard result={scanResult} />
      </div>
    );
  }

  return (
    <section id="scanner" className="max-w-7xl mx-auto px-4 py-12" onKeyDown={handleKeyDown}>
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">Scan Your Resume</h2>
        <p className="text-muted">Paste any resume and any job description. We analyze both in under 3 seconds.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div>
          <div className="flex items-center gap-3 mb-3">
            <button
              onClick={() => setUseFile(false)}
              className={`text-sm px-3 py-1 rounded-lg ${!useFile ? 'bg-primary text-white' : 'text-muted hover:text-text'}`}
            >
              Paste Text
            </button>
            <button
              onClick={() => setUseFile(true)}
              className={`text-sm px-3 py-1 rounded-lg ${useFile ? 'bg-primary text-white' : 'text-muted hover:text-text'}`}
            >
              Upload File
            </button>
          </div>
          {useFile ? (
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
        disabled={(!useFile && !resumeText.trim()) || (useFile && !file) || !jdText.trim()}
      />

      {error && (
        <div className="mt-4 p-4 bg-danger/10 border border-danger/30 rounded-xl text-danger text-sm">
          {error}
        </div>
      )}

      <p className="text-center text-xs text-muted mt-3">Press Ctrl+Enter to scan</p>
    </section>
  );
}
