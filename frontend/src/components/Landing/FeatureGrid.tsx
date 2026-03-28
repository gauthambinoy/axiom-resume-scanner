import { Crosshair, Brain, Wrench, FileUp, Gauge, List } from 'lucide-react';

const FEATURES = [
  { icon: Crosshair, title: 'Keyword matching', desc: 'Matches against JD with 100+ alias mappings' },
  { icon: Brain, title: '12-signal AI scan', desc: 'Detects AI patterns, structure, vocabulary' },
  { icon: Wrench, title: 'Fix suggestions', desc: 'Prioritized, actionable, with impact estimates' },
  { icon: FileUp, title: 'PDF upload', desc: 'Drop a PDF or DOCX, we extract text' },
  { icon: Gauge, title: 'Fast', desc: 'Full analysis in under 3 seconds' },
  { icon: List, title: 'Bullet analysis', desc: 'Every bullet scored individually' },
];

export function FeatureGrid() {
  return (
    <section id="features" className="py-20 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-xs font-medium text-primary uppercase tracking-widest mb-2">Features</p>
          <h2 className="text-2xl font-semibold tracking-tight">Everything in one scan</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-3">
          {FEATURES.map((f, i) => (
            <div
              key={f.title}
              className={`card p-5 animate-in stagger-${i + 1}`}
            >
              <div className="w-8 h-8 rounded-lg bg-primary-dim flex items-center justify-center mb-3">
                <f.icon size={15} className="text-primary" />
              </div>
              <h3 className="text-sm font-medium mb-1">{f.title}</h3>
              <p className="text-xs text-muted leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
