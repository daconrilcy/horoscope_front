import { Outlet } from "react-router-dom"

import { Header } from "./layout/Header"
import { Sidebar } from "./layout/Sidebar"
import { BottomNav } from "./layout/BottomNav"

export function AppShell() {
  return (
    <>
      <Header />
      <div className="app-shell-body">
        <Sidebar />
        <main className="app-shell-main">
          <Outlet />
        </main>
      </div>
      <BottomNav />
    </>
  )
}
