// Verifie que les principales narrations publiques restent raccordees au formatage editorial partage.
import fs from "node:fs"
import path from "node:path"

import { describe, expect, it } from "vitest"

const PUBLIC_EDITORIAL_SURFACES = [
  "../features/natal-chart/NatalAstralReading.tsx",
  "../features/natal-chart/NatalProfileHero.tsx",
  "../features/astrologers/components/AstrologerCard.tsx",
  "../features/astrologers/components/AstrologerProfileSections.tsx",
  "../components/NatalChartGuide.tsx",
  "../components/AstroDailyEvents.tsx",
  "../components/AstroFoundationSection.tsx",
  "../components/BestWindowCard.tsx",
  "../components/DayClimateHero.tsx",
  "../components/TurningPointCard.tsx",
  "../components/dashboard/DashboardHoroscopeSummaryCard.tsx",
  "../components/prediction/DailyAdviceCard.tsx",
  "../components/prediction/DayTimelineSectionV4.tsx",
  "../pages/NatalChartPage.tsx",
  "../pages/DailyHoroscopePage.tsx",
  "../pages/AstrologersPage.tsx",
  "../pages/AstrologerProfilePage.tsx",
  "../pages/HelpPage.tsx",
  "../pages/SubscriptionGuidePage.tsx",
  "../pages/PrivacyPolicyPage.tsx",
  "../pages/landing/sections/HeroSection.tsx",
  "../pages/landing/sections/ProblemSection.tsx",
  "../pages/landing/sections/SolutionSection.tsx",
  "../pages/landing/sections/TestimonialsSection.tsx",
  "../pages/landing/sections/FaqSection.tsx",
  "../pages/landing/sections/PricingSection.tsx",
  "../pages/landing/sections/LandingFooter.tsx",
] as const

describe("couverture du formatage editorial public", () => {
  it.each(PUBLIC_EDITORIAL_SURFACES)("%s utilise EditorialText", (relativePath) => {
    const content = fs.readFileSync(path.resolve(__dirname, relativePath), "utf-8")

    expect(content).toContain("EditorialText")
    expect(content).toMatch(/<EditorialText\s+text=/)
  })
})
