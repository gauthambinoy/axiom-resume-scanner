const TESTIMONIALS = [
  { quote: 'My ATS score went from 42 to 87 after following the fix suggestions.', name: 'Sarah K.', role: 'Software Engineer' },
  { quote: 'I had no idea my resume screamed AI-generated. ResumeShield caught everything.', name: 'Michael T.', role: 'Product Manager' },
  { quote: 'Got 3 interviews in the first week after optimizing with ResumeShield.', name: 'Priya R.', role: 'Data Scientist' },
];

export function Testimonials() {
  return (
    <section className="py-16 bg-surface/50">
      <h2 className="text-3xl font-bold text-center mb-12">What Users Say</h2>
      <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {TESTIMONIALS.map((t) => (
          <div key={t.name} className="bg-surface border border-surface-light rounded-xl p-6">
            <p className="text-sm text-muted mb-4 italic">"{t.quote}"</p>
            <p className="font-semibold text-sm">{t.name}</p>
            <p className="text-xs text-muted">{t.role}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
