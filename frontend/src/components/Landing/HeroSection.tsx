import { ArrowRight } from 'lucide-react';

export function HeroSection() {
  return (
    <section className="relative pt-24 pb-20 px-6">
      {/* Subtle grid bg */}
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.5) 1px, transparent 0)',
        backgroundSize: '32px 32px',
      }} />

      <div className="relative max-w-2xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border text-xs text-muted mb-8">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
          Free to use &middot; No signup required
        </div>

        <h1 className="text-4xl md:text-5xl font-bold tracking-tight leading-[1.1] mb-5">
          Your resume, scored on
          <br />
          <span className="text-gradient">two axes at once</span>
        </h1>

        <p className="text-base text-muted leading-relaxed max-w-md mx-auto mb-10">
          ATS keyword match and AI detection in a single scan.
          Paste, scan, fix. Under 3 seconds.
        </p>

        <a
          href="#scanner"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary-light text-white text-sm font-medium rounded-xl transition group"
        >
          Scan your resume
          <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
        </a>

        <div className="mt-16 grid grid-cols-3 gap-8 max-w-sm mx-auto">
          {[
            { value: '75%', label: 'fail ATS systems' },
            { value: '12', label: 'AI signals checked' },
            { value: '<3s', label: 'full analysis' },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-lg font-semibold mono">{stat.value}</div>
              <div className="text-[10px] text-muted mt-0.5">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
