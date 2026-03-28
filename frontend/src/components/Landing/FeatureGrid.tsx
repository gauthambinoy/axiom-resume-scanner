import { Target, Bot, Wrench, FileText, Zap, BarChart3 } from 'lucide-react';

const FEATURES = [
  { icon: Target, title: 'ATS Keyword Matching', desc: 'Matches your resume against JD keywords with alias detection' },
  { icon: Bot, title: '12-Signal AI Detection', desc: 'Detects AI-generated content with 12 independent signals' },
  { icon: Wrench, title: 'Actionable Fix Suggestions', desc: 'Specific, prioritized fixes with estimated score impact' },
  { icon: FileText, title: 'PDF & DOCX Upload', desc: 'Upload your resume directly, we extract the text' },
  { icon: Zap, title: 'Under 3 Seconds', desc: 'Full analysis in under 3 seconds, quick re-scan in 500ms' },
  { icon: BarChart3, title: 'Bullet-by-Bullet Analysis', desc: 'Every bullet scored for AI risk, structure, and flags' },
];

export function FeatureGrid() {
  return (
    <section id="features" className="py-16">
      <h2 className="text-3xl font-bold text-center mb-12">Everything You Need</h2>
      <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {FEATURES.map((f) => (
          <div key={f.title} className="bg-surface border border-surface-light rounded-xl p-6 hover:border-primary/30 transition">
            <f.icon size={24} className="text-primary mb-3" />
            <h3 className="font-semibold mb-2">{f.title}</h3>
            <p className="text-sm text-muted">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
