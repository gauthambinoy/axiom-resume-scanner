import { Shield } from 'lucide-react';

export function Header() {
  return (
    <header className="border-b border-surface-light">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="text-primary" size={28} />
          <span className="text-xl font-bold">ResumeShield</span>
        </div>
        <nav className="flex items-center gap-6 text-sm text-muted">
          <a href="#scanner" className="hover:text-text transition">Scanner</a>
          <a href="#features" className="hover:text-text transition">Features</a>
          <a href="#pricing" className="hover:text-text transition">Pricing</a>
        </nav>
      </div>
    </header>
  );
}
