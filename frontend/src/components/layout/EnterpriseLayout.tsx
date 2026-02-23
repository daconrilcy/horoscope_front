import { Outlet } from "react-router-dom"

export function EnterpriseLayout() {
  return (
    <div className="enterprise-layout">
      <h2>Espace Entreprise</h2>
      <div className="enterprise-content">
        <Outlet />
      </div>
    </div>
  )
}
