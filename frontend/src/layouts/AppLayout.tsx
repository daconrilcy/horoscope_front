import { Outlet } from "react-router-dom"

import { Header } from "../components/layout/Header"
import { Sidebar } from "../components/layout/Sidebar"
import { BottomNav } from "../components/layout/BottomNav"
import { PageErrorBoundary } from "../components/ErrorBoundary"
import { SidebarProvider, useSidebarContext } from "../state/SidebarContext"

function AppLayoutContent() {
  const { sidebarState } = useSidebarContext()
  const mainClassName = sidebarState === "icon-only"
    ? "app-shell-main app-shell-main--with-sidebar-offset"
    : "app-shell-main"

  return (
    <>
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
    </>
  )
}

export function AppLayout() {
  return (
    <SidebarProvider>
      <AppLayoutContent />
    </SidebarProvider>
  )
}
