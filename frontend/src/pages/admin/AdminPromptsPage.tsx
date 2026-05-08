// Shell de route Admin Prompts: garde la navigation et delegue les surfaces actives aux owners feature.
import { useMemo } from "react"
import { NavLink, Outlet, useLocation } from "react-router-dom"

import { useTranslation } from "../../i18n"
import {
  AdminPromptsRoute,
  resolvePromptsTabFromPath,
} from "../../features/admin-prompts/AdminPromptsRoute"
import "./AdminPromptsPage.css"

export { resolvePromptsTabFromPath }

const ADMIN_PROMPTS_BASE = "/admin/prompts"

export function AdminPromptsPage() {
  const location = useLocation()
  const tAdmin = useTranslation("admin")
  const tCat = tAdmin.promptsCatalog
  const sub = tAdmin.promptsSubNav
  const activeTab = useMemo(() => resolvePromptsTabFromPath(location.pathname), [location.pathname])
  const pageHeader = tAdmin.promptsPageHeader[activeTab]

  return (
    <div className="admin-prompts-page">
      <header className="admin-page-header">
        <div>
          <h2>{pageHeader.title}</h2>
          <p className="admin-prompts-page__intro">{pageHeader.intro}</p>
        </div>
        <nav className="admin-tabs admin-prompts-subnav" aria-label={tCat.subNavAriaLabel}>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/catalog`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.catalog}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/archive`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.archive}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/release`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.release}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/consumption`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.consumption}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/personas`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.personas}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/sample-payloads`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.sample_payloads}
          </NavLink>
        </nav>
      </header>

      <AdminPromptsRoute activeTab={activeTab} />
      <Outlet />
    </div>
  )
}
