import { Shield } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-surface-light mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted">
        <div className="flex items-center gap-2">
          <Shield size={18} className="text-primary" />
          <span>ResumeShield &copy; {new Date().getFullYear()}</span>
        </div>
        <p>Pass the ATS. Fool the AI detector. Land the interview.</p>
      </div>
    </footer>
  );
}
