import { ClipboardPaste, Scan, CheckCircle } from 'lucide-react';

const STEPS = [
  { icon: ClipboardPaste, title: 'Paste', desc: 'Paste your resume and the job description' },
  { icon: Scan, title: 'Scan', desc: 'We analyze ATS keywords and AI detection signals' },
  { icon: CheckCircle, title: 'Fix', desc: 'Follow prioritized suggestions to optimize your resume' },
];

export function HowItWorks() {
  return (
    <section className="py-16 bg-surface/50">
      <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
      <div className="flex flex-col md:flex-row items-center justify-center gap-8 max-w-4xl mx-auto">
        {STEPS.map((s, i) => (
          <div key={s.title} className="flex flex-col items-center text-center flex-1">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <s.icon size={28} className="text-primary" />
            </div>
            <div className="text-sm text-muted mb-1">Step {i + 1}</div>
            <h3 className="font-semibold text-lg mb-1">{s.title}</h3>
            <p className="text-sm text-muted">{s.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
