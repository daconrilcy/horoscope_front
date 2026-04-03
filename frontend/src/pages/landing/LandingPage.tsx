import "./LandingPage.css"
import { HeroSection } from "./sections/HeroSection"

export const LandingPage = () => {
  return (
    <div className="landing-page">
      <HeroSection />
      
      {/* Future sections (63.4 to 63.9) will be added here */}
      <div id="how-it-works" style={{ height: '100px' }}></div>
    </div>
  )
}
