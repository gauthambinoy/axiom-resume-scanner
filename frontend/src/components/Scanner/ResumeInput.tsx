interface Props {
  value: string;
  onChange: (v: string) => void;
  error?: string | null;
}

export function ResumeInput({ value, onChange, error }: Props) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-muted">Resume Text</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste your resume here..."
        className={`w-full min-h-[400px] p-4 bg-surface border rounded-xl text-sm text-text placeholder:text-muted/50 resize-y focus:outline-none focus:ring-2 focus:ring-primary/50 ${
          error ? 'border-danger' : 'border-surface-light'
        }`}
      />
      <div className="flex justify-between text-xs text-muted">
        {error ? <span className="text-danger">{error}</span> : <span />}
        <span>{value.length.toLocaleString()} / 15,000</span>
      </div>
    </div>
  );
}
