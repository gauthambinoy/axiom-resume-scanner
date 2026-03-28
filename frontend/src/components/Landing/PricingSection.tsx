import { Check } from 'lucide-react';

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    desc: 'Perfect for getting started',
    features: ['5 scans per hour', 'Full ATS + AI analysis', '12 detection signals', 'Fix suggestions', 'PDF upload'],
    cta: 'Start Scanning',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$9/mo',
    desc: 'For active job seekers',
    features: ['Unlimited scans', 'Scan history & trends', 'PDF report export', 'Before/after comparison', 'Priority support'],
    cta: 'Coming Soon',
    highlighted: true,
  },
];

export function PricingSection() {
  return (
    <section id="pricing" className="py-16">
      <h2 className="text-3xl font-bold text-center mb-12">Pricing</h2>
      <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
        {PLANS.map((plan) => (
          <div
            key={plan.name}
            className={`rounded-xl p-6 border ${
              plan.highlighted
                ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10'
                : 'border-surface-light bg-surface'
            }`}
          >
            <h3 className="font-semibold text-lg">{plan.name}</h3>
            <div className="text-3xl font-bold my-2">{plan.price}</div>
            <p className="text-sm text-muted mb-4">{plan.desc}</p>
            <ul className="space-y-2 mb-6">
              {plan.features.map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm">
                  <Check size={14} className="text-success" /> {f}
                </li>
              ))}
            </ul>
            <button
              className={`w-full py-2.5 rounded-lg font-medium text-sm transition ${
                plan.highlighted
                  ? 'bg-primary hover:bg-primary-light text-white'
                  : 'bg-surface-light hover:bg-surface-light/80 text-text'
              }`}
            >
              {plan.cta}
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
