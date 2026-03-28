import { Shield } from 'lucide-react';

export function Header() {
  return (
    <header className="glass sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2 group">
          <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition">
            <Shield size={15} className="text-primary" />
          </div>
          <span className="text-sm font-semibold tracking-tight">ResumeShield</span>
        </a>
        <nav className="flex items-center gap-1">
          <a href="#scanner" className="px-3 py-1.5 text-xs text-muted hover:text-text rounded-lg hover:bg-surface-light transition">Scanner</a>
          <a href="#features" className="px-3 py-1.5 text-xs text-muted hover:text-text rounded-lg hover:bg-surface-light transition">Features</a>
          <a
            href="#scanner"
            className="ml-2 px-3.5 py-1.5 text-xs font-medium bg-primary hover:bg-primary-light text-white rounded-lg transition"
          >
            Get Started
          </a>
        </nav>
      </div>
    </header>
  );
}
