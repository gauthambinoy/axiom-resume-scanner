interface Props {
  value: string;
  onChange: (v: string) => void;
  error?: string | null;
}

export function ResumeInput({ value, onChange, error }: Props) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <label className="text-xs font-medium text-muted-light">Resume</label>
        <span className="mono text-[10px] text-muted">{value.length.toLocaleString()}</span>
      </div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste your full resume text here..."
        spellCheck={false}
        className={`w-full h-[380px] p-4 bg-bg border rounded-xl text-[13px] leading-relaxed text-text-secondary placeholder:text-muted/40 resize-none focus:outline-none focus:ring-1 focus:ring-primary/40 focus:border-primary/40 transition ${
          error ? 'border-danger/50' : 'border-border'
        }`}
      />
      {error && <p className="text-[11px] text-danger">{error}</p>}
    </div>
  );
}
