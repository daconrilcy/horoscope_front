import { Outlet } from "react-router-dom"
import { StarfieldBackground } from "../components/StarfieldBackground"

export function RootLayout() {
  return (
    <div className="app-shell app-bg">
      <StarfieldBackground />
      <div className="app-bg-container">
        <Outlet />
      </div>
    </div>
  )
}
