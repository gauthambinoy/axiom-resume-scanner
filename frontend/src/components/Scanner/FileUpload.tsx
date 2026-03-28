import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X } from 'lucide-react';
import { formatFileSize } from '../../utils/formatters';

interface Props {
  file: File | null;
  onFile: (f: File) => void;
  onRemove: () => void;
  error?: string | null;
}

export function FileUpload({ file, onFile, onRemove, error }: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => { if (accepted[0]) onFile(accepted[0]); },
    [onFile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  if (file) {
    return (
      <div className="flex items-center gap-3 px-4 py-3 bg-bg border border-border rounded-xl">
        <div className="w-8 h-8 rounded-lg bg-primary-dim flex items-center justify-center">
          <File size={14} className="text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium truncate">{file.name}</p>
          <p className="text-[10px] text-muted">{formatFileSize(file.size)}</p>
        </div>
        <button onClick={onRemove} className="p-1 rounded-md hover:bg-surface-light text-muted hover:text-danger transition">
          <X size={14} />
        </button>
      </div>
    );
  }

  return (
    <div>
      <div
        {...getRootProps()}
        className={`border border-dashed rounded-xl px-6 py-10 text-center cursor-pointer transition-all ${
          isDragActive ? 'border-primary bg-primary-dim' : 'border-border hover:border-border-light'
        }`}
      >
        <input {...getInputProps()} />
        <Upload size={18} className="mx-auto mb-2 text-muted" />
        <p className="text-xs text-muted">Drop PDF or DOCX here</p>
        <p className="text-[10px] text-muted/50 mt-1">Max 10MB</p>
      </div>
      {error && <p className="text-[11px] text-danger mt-1">{error}</p>}
    </div>
  );
}
