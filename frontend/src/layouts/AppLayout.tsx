import { Outlet, useLocation } from "react-router-dom"

import { Header } from "../components/layout/Header"
import { Sidebar } from "../components/layout/Sidebar"
import { BottomNav } from "../components/layout/BottomNav"
import { PageErrorBoundary } from "../components/ErrorBoundary"
import { StarfieldBackground } from "../components/StarfieldBackground"
import { SidebarProvider, useSidebarContext } from "../state/SidebarContext"

function AppLayoutContent() {
  const { sidebarState } = useSidebarContext()
  const location = useLocation()
  const isAdminRoute = location.pathname.startsWith("/admin")
  const mainClassName = sidebarState === "icon-only"
    ? `app-shell-main app-shell-main--with-sidebar-offset${isAdminRoute ? " app-shell-main--admin" : ""}`
    : `app-shell-main${isAdminRoute ? " app-shell-main--admin" : ""}`
  const containerClassName = `app-bg-container${isAdminRoute ? " app-bg-container--admin" : ""}`

  return (
    <div className="app-shell app-bg">
      <StarfieldBackground />
      <div className={containerClassName}>
        <Header />
        <div className="app-shell-body">
          <Sidebar />
          <main className={mainClassName}>
            <PageErrorBoundary>
              <Outlet />
            </PageErrorBoundary>
          </main>
        </div>
        <BottomNav />
      </div>
    </div>
  )
}

export function AppLayout() {
  return (
    <SidebarProvider>
      <AppLayoutContent />
    </SidebarProvider>
  )
}
