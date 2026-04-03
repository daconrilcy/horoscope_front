import "./LandingPage.css"
import { HeroSection } from "./sections/HeroSection"
import { SocialProofSection } from "./sections/SocialProofSection"
import { ProblemSection } from "./sections/ProblemSection"
import { SolutionSection } from "./sections/SolutionSection"
import { TestimonialsSection } from "./sections/TestimonialsSection"
import { PricingSection } from "./sections/PricingSection"
import { FaqSection } from "./sections/FaqSection"

export const LandingPage = () => {
  return (
    <div className="landing-page">
      <HeroSection />
      <SocialProofSection />
      <ProblemSection />
      <SolutionSection />
      <TestimonialsSection />
      <PricingSection />
      <FaqSection />
      
      {/* Future sections (63.9) will be added here */}
    </div>
  )
}
