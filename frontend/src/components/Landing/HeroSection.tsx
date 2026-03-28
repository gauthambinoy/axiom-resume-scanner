export function HeroSection() {
  return (
    <section className="py-20 text-center">
      <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
        <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          Pass the ATS.
        </span>
        <br />
        <span className="bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
          Fool the AI Detector.
        </span>
      </h1>
      <p className="text-xl text-muted max-w-2xl mx-auto mb-8">
        The only tool that scores your resume on both axes. Free.
      </p>
      <a
        href="#scanner"
        className="inline-flex items-center gap-2 px-8 py-4 bg-primary hover:bg-primary-light text-white text-lg font-semibold rounded-xl transition shadow-lg shadow-primary/25"
      >
        Scan My Resume Now
      </a>
      <div className="mt-12 flex justify-center gap-8 text-sm text-muted">
        <div><span className="text-2xl font-bold text-text">75%</span><br />of resumes fail ATS</div>
        <div><span className="text-2xl font-bold text-text">80%</span><br />of AI resumes get rejected</div>
        <div><span className="text-2xl font-bold text-text">2</span><br />axes, one scan</div>
      </div>
    </section>
  );
}
