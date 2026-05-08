// Fournit le shell d'authentification pour les routes Outlet et les pages de support.
import { Outlet } from "react-router-dom"
import type { ReactNode } from "react"
import "./AuthLayout.css"

export function AuthLayout({ children }: { children?: ReactNode }) {
  return (
    <div className="auth-layout">
      <div className="auth-layout__container">
        {children ?? <Outlet />}
      </div>
    </div>
  )
}
