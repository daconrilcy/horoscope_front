import { Outlet } from "react-router-dom"

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
      <main className="landing-layout__main">
        <Outlet />
      </main>
    </div>
  )
}
