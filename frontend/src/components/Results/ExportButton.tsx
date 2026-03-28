import { Download } from 'lucide-react';

export function ExportButton() {
  return (
    <button
      onClick={() => window.print()}
      className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] text-muted hover:text-text bg-surface border border-border rounded-lg hover:border-border-light transition"
    >
      <Download size={11} />
      Export
    </button>
  );
}
