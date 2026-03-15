import { Outlet } from "react-router-dom"
import { PageLayout } from "../../layouts"

export function EnterpriseLayout() {
  return (
    <PageLayout className="enterprise-layout">
      <h2>Espace Entreprise</h2>
      <div className="enterprise-content">
        <Outlet />
      </div>
    </PageLayout>
  )
}
