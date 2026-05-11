// Fournit le layout maitre unique pour le fond global et le conteneur de route.
import { Outlet, useLocation } from "react-router-dom"
import { StarfieldBackground } from "../components/StarfieldBackground"

/** Rend le fond applicatif canonique et laisse les layouts secondaires gerer leur navigation. */
export function RootLayout() {
  const location = useLocation()
  const backgroundClassName = "app-shell app-bg app-bg--internal"
  const containerClassName = location.pathname.startsWith("/admin")
    ? "app-bg-container app-bg-container--admin"
    : "app-bg-container"

  return (
    <div className={backgroundClassName}>
      <StarfieldBackground />
      <div className={containerClassName}>
        <Outlet />
      </div>
    </div>
  )
}
