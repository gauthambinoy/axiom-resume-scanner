export function HowItWorks() {
  const steps = [
    { num: '01', title: 'Paste', desc: 'Resume + job description' },
    { num: '02', title: 'Scan', desc: 'ATS match + AI detection' },
    { num: '03', title: 'Fix', desc: 'Follow ranked suggestions' },
  ];

  return (
    <section className="py-16 px-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-4 md:gap-0 md:justify-between">
          {steps.map((s, i) => (
            <div key={s.num} className="flex items-center gap-4 flex-1">
              <div className="flex items-center gap-3">
                <span className="mono text-[10px] text-muted">{s.num}</span>
                <div>
                  <p className="text-sm font-medium">{s.title}</p>
                  <p className="text-[11px] text-muted">{s.desc}</p>
                </div>
              </div>
              {i < steps.length - 1 && (
                <div className="hidden md:block flex-1 h-px bg-border mx-6" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
