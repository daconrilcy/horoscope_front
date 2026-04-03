import "./LandingPage.css"
import { HeroSection } from "./sections/HeroSection"
import { SocialProofSection } from "./sections/SocialProofSection"
import { ProblemSection } from "./sections/ProblemSection"
import { SolutionSection } from "./sections/SolutionSection"
import { TestimonialsSection } from "./sections/TestimonialsSection"

export const LandingPage = () => {
  return (
    <div className="landing-page">
      <HeroSection />
      <SocialProofSection />
      <ProblemSection />
      <SolutionSection />
      <TestimonialsSection />
      
      {/* Future sections (63.7 to 63.9) will be added here */}
    </div>
  )
}
