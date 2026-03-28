import { useState, useCallback } from 'react';

const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];
const MAX_SIZE = 10 * 1024 * 1024;

export function useFileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback((f: File) => {
    setError(null);
    if (!ALLOWED_TYPES.includes(f.type) && !f.name.match(/\.(pdf|docx)$/i)) {
      setError('Only PDF and DOCX files are accepted');
      return;
    }
    if (f.size > MAX_SIZE) {
      setError('File must be under 10MB');
      return;
    }
    setFile(f);
  }, []);

  const removeFile = useCallback(() => {
    setFile(null);
    setError(null);
  }, []);

  return {
    file,
    fileName: file?.name ?? '',
    fileSize: file?.size ?? 0,
    error,
    isValid: file !== null && error === null,
    handleFile,
    removeFile,
  };
}
