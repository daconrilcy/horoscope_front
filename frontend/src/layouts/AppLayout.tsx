import { Outlet } from "react-router-dom"

import { Header } from "../components/layout/Header"
import { Sidebar } from "../components/layout/Sidebar"
import { BottomNav } from "../components/layout/BottomNav"
import { PageErrorBoundary } from "../components/ErrorBoundary"
import { StarfieldBackground } from "../components/StarfieldBackground"
import { SidebarProvider, useSidebarContext } from "../state/SidebarContext"

function AppLayoutContent() {
  const { sidebarState } = useSidebarContext()
  const mainClassName = sidebarState === "icon-only"
    ? "app-shell-main app-shell-main--with-sidebar-offset"
    : "app-shell-main"

  return (
    <div className="app-shell app-bg">
      <StarfieldBackground />
      <div className="app-bg-container">
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
