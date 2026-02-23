import { Outlet } from "react-router-dom"

import { Header } from "./layout/Header"
import { Sidebar } from "./layout/Sidebar"
import { BottomNav } from "./layout/BottomNav"
import { StarfieldBackground } from "./StarfieldBackground"

export function AppShell() {
  return (
    <div className="app-shell app-bg">
      <StarfieldBackground />
      <div className="app-bg-container">
        <Header />
        <div className="app-shell-body">
          <Sidebar />
          <main className="app-shell-main">
            <Outlet />
          </main>
        </div>
        <BottomNav />
      </div>
    </div>
  )
}
