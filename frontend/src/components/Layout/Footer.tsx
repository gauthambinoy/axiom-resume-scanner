export function Footer() {
  return (
    <footer className="border-t border-border mt-auto">
      <div className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between text-xs text-muted">
        <span>&copy; {new Date().getFullYear()} ResumeShield</span>
        <span>Built for job seekers.</span>
      </div>
    </footer>
  );
}
