import { HeroSection } from './HeroSection';
import { HowItWorks } from './HowItWorks';
import { FeatureGrid } from './FeatureGrid';
import { ScannerPage } from '../Scanner/ScannerPage';

export function LandingPage() {
  return (
    <div>
      <HeroSection />
      <HowItWorks />
      <div className="border-t border-border">
        <ScannerPage />
      </div>
      <div className="border-t border-border">
        <FeatureGrid />
      </div>
    </div>
  );
}
