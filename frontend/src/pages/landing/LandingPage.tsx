import "./LandingPage.css"
import { HeroSection } from "./sections/HeroSection"
import { SocialProofSection } from "./sections/SocialProofSection"

export const LandingPage = () => {
  return (
    <div className="landing-page">
      <HeroSection />
      <SocialProofSection />
      
      {/* Future sections (63.4 to 63.9) will be added here */}
      <div id="how-it-works" style={{ height: '100px' }}></div>
    </div>
  )
}
