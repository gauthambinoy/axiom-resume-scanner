import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, Play, Loader2, CheckCircle, AlertCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { formatFileSize } from '../../utils/formatters';
import { getScoreColor } from '../../utils/constants';
import { scanBulk } from '../../services/api';
import type { BulkScanResultItem, ContentMode, ScanResponse } from '../../types';
import { ResultsDashboard } from '../Results/ResultsDashboard';

const MAX_FILES = 10;
const MAX_SIZE = 10 * 1024 * 1024;
const ALLOWED_EXTENSIONS = /\.(pdf|docx)$/i;
const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

interface Props {
  jdText: string;
  contentMode: ContentMode;
}

function getReadinessLabel(level: string): string {
  const labels: Record<string, string> = {
    INTERVIEW_READY: 'Ready',
    NEEDS_WORK: 'Needs work',
    AT_RISK: 'At risk',
  };
  return labels[level] || level;
}

function getReadinessColor(level: string): string {
  const colors: Record<string, string> = {
    INTERVIEW_READY: '#10B981',
    NEEDS_WORK: '#F59E0B',
    AT_RISK: '#EF4444',
  };
  return colors[level] || '#6B7280';
}

export function BulkUpload({ jdText, contentMode }: Props) {
  const [files, setFiles] = useState<File[]>([]);
  const [fileError, setFileError] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<BulkScanResultItem[] | null>(null);
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const onDrop = useCallback((accepted: File[]) => {
    setFileError(null);

    const valid: File[] = [];
    for (const f of accepted) {
      if (!ALLOWED_TYPES.includes(f.type) && !f.name.match(ALLOWED_EXTENSIONS)) {
        continue; // skip invalid
      }
      if (f.size > MAX_SIZE) {
        continue; // skip oversized
      }
      valid.push(f);
    }

    setFiles(prev => {
      const combined = [...prev, ...valid];
      if (combined.length > MAX_FILES) {
        setFileError(`Maximum ${MAX_FILES} files. Excess files were removed.`);
        return combined.slice(0, MAX_FILES);
      }
      return combined;
    });
  }, []);

  const removeFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setFileError(null);
  }, []);

  const clearAll = useCallback(() => {
    setFiles([]);
    setResults(null);
    setExpandedRow(null);
    setFileError(null);
    setProgress(0);
  }, []);

  const handleScanAll = async () => {
    if (files.length === 0) return;

    setIsScanning(true);
    setResults(null);
    setExpandedRow(null);
    setProgress(0);

    try {
      // Simulate progress since bulk endpoint processes sequentially
      const progressTimer = setInterval(() => {
        setProgress(prev => Math.min(prev + (100 / files.length / 4), 95));
      }, 500);

      const response = await scanBulk(files, contentMode === 'resume' ? jdText : '', contentMode);
      clearInterval(progressTimer);
      setProgress(100);
      setResults(response.results);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Bulk scan failed. Please try again.';
      setFileError(message);
    } finally {
      setIsScanning(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: MAX_FILES,
    maxSize: MAX_SIZE,
    multiple: true,
  });

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      {!results && (
        <div
          {...getRootProps()}
          className={`border border-dashed rounded-xl px-6 py-8 text-center cursor-pointer transition-all ${
            isDragActive ? 'border-primary bg-primary-dim' : 'border-border hover:border-border-light'
          }`}
        >
          <input {...getInputProps()} />
          <Upload size={20} className="mx-auto mb-2 text-muted" />
          <p className="text-xs text-muted">Drop up to {MAX_FILES} PDF or DOCX files here</p>
          <p className="text-[10px] text-muted/50 mt-1">Max 10MB each</p>
        </div>
      )}

      {/* Error */}
      {fileError && (
        <p className="text-[11px] text-danger px-1">{fileError}</p>
      )}

      {/* File list */}
      {files.length > 0 && !results && (
        <div className="space-y-1.5">
          <div className="flex items-center justify-between mb-2">
            <p className="text-[11px] text-muted font-medium">{files.length} file{files.length !== 1 ? 's' : ''} selected</p>
            <button onClick={clearAll} className="text-[10px] text-muted hover:text-danger transition">Clear all</button>
          </div>
          {files.map((f, i) => (
            <div key={`${f.name}-${i}`} className="flex items-center gap-3 px-3 py-2 bg-bg border border-border rounded-lg">
              <div className="w-7 h-7 rounded-md bg-primary-dim flex items-center justify-center shrink-0">
                <File size={12} className="text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[11px] font-medium truncate">{f.name}</p>
                <p className="text-[9px] text-muted">{formatFileSize(f.size)}</p>
              </div>
              <button
                onClick={() => removeFile(i)}
                className="p-1 rounded-md hover:bg-surface-light text-muted hover:text-danger transition"
              >
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Progress bar */}
      {isScanning && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-[10px] text-muted">
            <span className="flex items-center gap-1.5">
              <Loader2 size={11} className="animate-spin text-primary" />
              Processing files...
            </span>
            <span className="mono">{Math.round(progress)}%</span>
          </div>
          <div className="h-1.5 bg-surface-light rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Scan All button */}
      {files.length > 0 && !results && (
        <button
          onClick={handleScanAll}
          disabled={isScanning || files.length === 0}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-medium rounded-xl transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isScanning ? (
            <>
              <Loader2 size={13} className="animate-spin" />
              Scanning {files.length} files...
            </>
          ) : (
            <>
              <Play size={13} />
              Scan All ({files.length} file{files.length !== 1 ? 's' : ''})
            </>
          )}
        </button>
      )}

      {/* Results table */}
      {results && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold">Bulk Results</h3>
            <button
              onClick={clearAll}
              className="text-[10px] text-primary hover:text-primary-hover transition font-medium"
            >
              New bulk scan
            </button>
          </div>

          {/* Summary table */}
          <div className="border border-border rounded-xl overflow-hidden">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="bg-surface text-muted text-left">
                  <th className="px-3 py-2 font-medium w-8"></th>
                  <th className="px-3 py-2 font-medium">File</th>
                  <th className="px-3 py-2 font-medium text-center">ATS</th>
                  <th className="px-3 py-2 font-medium text-center">AI Risk</th>
                  <th className="px-3 py-2 font-medium text-center">Readiness</th>
                  <th className="px-3 py-2 font-medium text-center">Status</th>
                </tr>
              </thead>
              <tbody>
                {results.map((item, i) => (
                  <ResultRow
                    key={i}
                    item={item}
                    index={i}
                    expanded={expandedRow === i}
                    onToggle={() => setExpandedRow(expandedRow === i ? null : i)}
                  />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function ResultRow({
  item,
  index,
  expanded,
  onToggle,
}: {
  item: BulkScanResultItem;
  index: number;
  expanded: boolean;
  onToggle: () => void;
}) {
  const hasResult = !!item.result;
  const result = item.result;

  return (
    <>
      <tr
        className={`border-t border-border cursor-pointer hover:bg-surface/50 transition ${
          expanded ? 'bg-surface/30' : ''
        }`}
        onClick={onToggle}
      >
        <td className="px-3 py-2.5">
          {hasResult ? (
            expanded ? <ChevronDown size={12} className="text-muted" /> : <ChevronRight size={12} className="text-muted" />
          ) : null}
        </td>
        <td className="px-3 py-2.5 font-medium truncate max-w-[180px]">{item.filename}</td>
        <td className="px-3 py-2.5 text-center">
          {result ? (
            <span className="mono font-semibold" style={{ color: getScoreColor(result.ats_score.overall_score) }}>
              {result.ats_score.overall_score}
            </span>
          ) : <span className="text-muted">--</span>}
        </td>
        <td className="px-3 py-2.5 text-center">
          {result ? (
            <span className="mono font-semibold" style={{ color: getScoreColor(result.ai_score.overall_score, true) }}>
              {Math.round(result.ai_score.overall_score)}
            </span>
          ) : <span className="text-muted">--</span>}
        </td>
        <td className="px-3 py-2.5 text-center">
          {result ? (
            <span
              className="text-[10px] font-medium px-1.5 py-0.5 rounded-full"
              style={{
                color: getReadinessColor(result.combined.readiness_level),
                backgroundColor: getReadinessColor(result.combined.readiness_level) + '15',
              }}
            >
              {getReadinessLabel(result.combined.readiness_level)}
            </span>
          ) : <span className="text-muted">--</span>}
        </td>
        <td className="px-3 py-2.5 text-center">
          {item.error ? (
            <span className="inline-flex items-center gap-1 text-danger">
              <AlertCircle size={11} /> Error
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-success">
              <CheckCircle size={11} /> Done
            </span>
          )}
        </td>
      </tr>
      {expanded && hasResult && result && (
        <tr>
          <td colSpan={6} className="px-4 py-4 bg-bg border-t border-border">
            <ResultsDashboard result={result as ScanResponse} />
          </td>
        </tr>
      )}
      {expanded && item.error && (
        <tr>
          <td colSpan={6} className="px-4 py-3 bg-danger/5 border-t border-border">
            <p className="text-[11px] text-danger">{item.error}</p>
          </td>
        </tr>
      )}
    </>
  );
}
