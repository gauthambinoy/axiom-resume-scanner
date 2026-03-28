import { ArrowRight, Loader2 } from 'lucide-react';

interface Props {
  onClick: () => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ScanButton({ onClick, isLoading, disabled }: Props) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className="w-full py-3 bg-primary hover:bg-primary-light disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium rounded-xl transition-all flex items-center justify-center gap-2 active:scale-[0.99]"
    >
      {isLoading ? (
        <>
          <Loader2 size={14} className="animate-spin" />
          Analyzing...
        </>
      ) : (
        <>
          Run scan
          <ArrowRight size={14} />
        </>
      )}
    </button>
  );
}
