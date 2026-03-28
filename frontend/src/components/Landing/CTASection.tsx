export function CTASection() {
  return (
    <section className="py-20 text-center">
      <h2 className="text-3xl font-bold mb-4">Ready to Beat the Bots?</h2>
      <p className="text-muted mb-8 max-w-lg mx-auto">
        Scan your resume now and get actionable fixes in under 3 seconds.
      </p>
      <a
        href="#scanner"
        className="inline-flex px-8 py-4 bg-primary hover:bg-primary-light text-white text-lg font-semibold rounded-xl transition shadow-lg shadow-primary/25"
      >
        Scan My Resume Now
      </a>
    </section>
  );
}
