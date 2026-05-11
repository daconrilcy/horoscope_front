// Page publique principale composee depuis les sections marketing de la landing.
import { useEffect } from "react"
import { useTranslation } from "../../i18n"
import { useAnalytics, getUtmParams } from "../../hooks/useAnalytics"
import "./LandingPage.css"
import { LandingHead } from "./LandingHead"
import { HeroSection } from "./sections/HeroSection"
import { SocialProofSection } from "./sections/SocialProofSection"
import { TestimonialsSection } from "./sections/TestimonialsSection"
import { ProblemSection } from "./sections/ProblemSection"
import { SolutionSection } from "./sections/SolutionSection"
import { PricingSection } from "./sections/PricingSection"
import { FaqSection } from "./sections/FaqSection"

export const LandingPage = () => {
  const t = useTranslation("landing")
  const { track } = useAnalytics()

  useEffect(() => {
    track("landing_view", getUtmParams())
  }, [track])

  return (
    <div className="landing-page">
      <LandingHead seo={t.seo} faqItems={t.faq.items} />
      <HeroSection />
      <SocialProofSection />
      <TestimonialsSection />
      <ProblemSection />
      <SolutionSection />
      <PricingSection />
      <FaqSection />
    </div>
  )
}

export default LandingPage
