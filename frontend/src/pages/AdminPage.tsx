import { Link, Outlet, useLocation } from "react-router-dom"
import { detectLang } from "../i18n/astrology"
import { adminTranslations } from "../i18n/admin"
import "./AdminPage.css"

function PricingIcon() {
  return (
    <svg
      className="admin-card-icon-svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M12 6v12M9 9.5c0-1.1.9-2 2-2h2a2 2 0 110 4h-2a2 2 0 100 4h2a2 2 0 002-2" />
    </svg>
  )
}

function MonitoringIcon() {
  return (
    <svg
      className="admin-card-icon-svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 3v18h18" />
      <path d="M18 17V9" />
      <path d="M13 17V5" />
      <path d="M8 17v-3" />
    </svg>
  )
}

function PersonasIcon() {
  return (
    <svg
      className="admin-card-icon-svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="7" r="4" />
      <path d="M5.5 21a8.5 8.5 0 0113 0" />
    </svg>
  )
}

function ReconciliationIcon() {
  return (
    <svg
      className="admin-card-icon-svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21 12a9 9 0 11-9-9" />
      <path d="M21 3v9h-9" />
    </svg>
  )
}

export function AdminPage() {
  const lang = detectLang()
  const tPage = adminTranslations.page[lang]
  const tSections = adminTranslations.sections[lang]

  const adminSections = [
    { path: "/admin/pricing", label: tSections.pricing, Icon: PricingIcon },
    { path: "/admin/monitoring", label: tSections.monitoring, Icon: MonitoringIcon },
    { path: "/admin/personas", label: tSections.personas, Icon: PersonasIcon },
    { path: "/admin/reconciliation", label: tSections.reconciliation, Icon: ReconciliationIcon },
  ]

  const location = useLocation()
  const normalizedPath = location.pathname.replace(/\/$/, "")
  const isHub = normalizedPath === "/admin"

  return (
    <div className="admin-page">
      <header className="admin-header">
        <h1>{tPage.title}</h1>
        {!isHub && (
          <Link to="/admin" className="admin-back-link">
            {tPage.backToHub}
          </Link>
        )}
      </header>

      {isHub ? (
        <section className="admin-hub" aria-label="Sections d'administration">
          <div className="admin-grid">
            {adminSections.map((section) => (
              <Link
                key={section.path}
                to={section.path}
                className="admin-card"
                aria-label={section.label}
              >
                <section.Icon />
                <span className="admin-card-label">{section.label}</span>
              </Link>
            ))}
          </div>
        </section>
      ) : (
        <div className="admin-content">
          <Outlet />
        </div>
      )}
    </div>
  )
}
