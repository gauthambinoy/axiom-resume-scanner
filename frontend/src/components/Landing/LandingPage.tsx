import { HeroSection } from './HeroSection';
import { FeatureGrid } from './FeatureGrid';
import { HowItWorks } from './HowItWorks';
import { Testimonials } from './Testimonials';
import { PricingSection } from './PricingSection';
import { CTASection } from './CTASection';
import { ScannerPage } from '../Scanner/ScannerPage';

export function LandingPage() {
  return (
    <div>
      <HeroSection />
      <HowItWorks />
      <ScannerPage />
      <FeatureGrid />
      <Testimonials />
      <PricingSection />
      <CTASection />
    </div>
  );
}
