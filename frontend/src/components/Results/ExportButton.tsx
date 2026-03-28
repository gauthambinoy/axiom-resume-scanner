import { Download } from 'lucide-react';

export function ExportButton() {
  const handleExport = () => {
    window.print();
  };

  return (
    <button
      onClick={handleExport}
      className="flex items-center gap-2 px-4 py-2 bg-surface-light text-sm text-muted hover:text-text rounded-lg transition"
    >
      <Download size={16} />
      Export Report
    </button>
  );
}
