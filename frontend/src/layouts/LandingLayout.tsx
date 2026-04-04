import { Outlet } from "react-router-dom"
import { LandingNavbar } from "../pages/landing/sections/LandingNavbar"
import { LandingFooter } from "../pages/landing/sections/LandingFooter"
import { useTranslation } from "../i18n"
import "./LandingLayout.css"

/**
 * LandingLayout
 * 
 * Minimal wrapper for the landing page.
 * Inherits background from RootLayout.
 * No AppShell, no Sidebar, no BottomNav.
 */
export const LandingLayout = () => {
  const t = useTranslation("landing")

  return (
    <div className="landing-layout">
      <a href="#main-content" className="skip-link">
        {t.common.skipLink}
      </a>
      <LandingNavbar />
      <main id="main-content" className="landing-layout__main">
        <Outlet />
      </main>
      <LandingFooter />
    </div>
  )
}
