import { useState } from 'react';
import { Download, Loader2 } from 'lucide-react';
import { exportPDF } from '../../services/api';

interface ExportButtonProps {
  resumeText: string;
  jdText: string;
  mode: string;
}

export function ExportButton({ resumeText, jdText, mode }: ExportButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const blob = await exportPDF(resumeText, jdText, mode);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'resumeshield-report.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF export failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={loading}
      className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] text-muted hover:text-text bg-surface border border-border rounded-lg hover:border-border-light transition disabled:opacity-50"
    >
      {loading ? <Loader2 size={11} className="animate-spin" /> : <Download size={11} />}
      {loading ? 'Generating...' : 'Export PDF'}
    </button>
  );
}
