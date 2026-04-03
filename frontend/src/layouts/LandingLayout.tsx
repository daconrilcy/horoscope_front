import { Outlet } from "react-router-dom"
import { LandingNavbar } from "../pages/landing/sections/LandingNavbar"
import { LandingFooter } from "../pages/landing/sections/LandingFooter"

/**
 * LandingLayout
 * 
 * Minimal wrapper for the landing page.
 * Inherits background from RootLayout.
 * No AppShell, no Sidebar, no BottomNav.
 */
export const LandingLayout = () => {
  return (
    <div className="landing-layout">
      <a href="#main-content" className="skip-link">
        Aller au contenu principal
      </a>
      <LandingNavbar />
      <main id="main-content" className="landing-layout__main">
        <Outlet />
      </main>
      <LandingFooter />
    </div>
  )
}
