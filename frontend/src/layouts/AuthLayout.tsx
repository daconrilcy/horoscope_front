import { Outlet } from "react-router-dom"
import "./AuthLayout.css"

export function AuthLayout() {
  return (
    <div className="auth-layout">
      <div className="auth-layout__container">
        <Outlet />
      </div>
    </div>
  )
}
