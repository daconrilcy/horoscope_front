import "./LandingPage.css"
import { HeroSection } from "./sections/HeroSection"
import { SocialProofSection } from "./sections/SocialProofSection"
import { ProblemSection } from "./sections/ProblemSection"
import { SolutionSection } from "./sections/SolutionSection"

export const LandingPage = () => {
  return (
    <div className="landing-page">
      <HeroSection />
      <SocialProofSection />
      <ProblemSection />
      <SolutionSection />
      
      {/* Future sections (63.6 to 63.9) will be added here */}
    </div>
  )
}
