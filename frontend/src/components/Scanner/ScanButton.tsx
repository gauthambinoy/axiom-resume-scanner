import { Zap } from 'lucide-react';
import { LoadingSpinner } from '../common/LoadingSpinner';

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
      className="w-full py-4 bg-primary hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition flex items-center justify-center gap-2 text-lg"
    >
      {isLoading ? (
        <>
          <LoadingSpinner size="sm" />
          Scanning...
        </>
      ) : (
        <>
          <Zap size={20} />
          Scan My Resume
        </>
      )}
    </button>
  );
}
