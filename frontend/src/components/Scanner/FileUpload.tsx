import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X } from 'lucide-react';
import { formatFileSize } from '../../utils/formatters';

interface Props {
  file: File | null;
  onFile: (f: File) => void;
  onRemove: () => void;
  error?: string | null;
}

export function FileUpload({ file, onFile, onRemove, error }: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onFile(accepted[0]);
    },
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
      <div className="flex items-center gap-3 p-3 bg-surface border border-surface-light rounded-xl">
        <FileText size={20} className="text-primary" />
        <div className="flex-1 min-w-0">
          <p className="text-sm truncate">{file.name}</p>
          <p className="text-xs text-muted">{formatFileSize(file.size)}</p>
        </div>
        <button onClick={onRemove} className="text-muted hover:text-danger"><X size={18} /></button>
      </div>
    );
  }

  return (
    <div>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition ${
          isDragActive ? 'border-primary bg-primary/5' : 'border-surface-light hover:border-muted'
        }`}
      >
        <input {...getInputProps()} />
        <Upload size={24} className="mx-auto mb-2 text-muted" />
        <p className="text-sm text-muted">
          {isDragActive ? 'Drop your resume here' : 'Drag & drop a PDF or DOCX, or click to browse'}
        </p>
        <p className="text-xs text-muted/60 mt-1">Max 10MB</p>
      </div>
      {error && <p className="text-xs text-danger mt-1">{error}</p>}
    </div>
  );
}
