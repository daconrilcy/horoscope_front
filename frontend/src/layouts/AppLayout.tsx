import { Outlet } from "react-router-dom"

import { Header } from "../components/layout/Header"
import { Sidebar } from "../components/layout/Sidebar"
import { BottomNav } from "../components/layout/BottomNav"

export function AppLayout() {
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
