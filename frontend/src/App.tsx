import { type ReactNode, useEffect, useMemo, useState } from "react"

import "./App.css"
import { AppShell } from "./components/AppShell"
import { B2BAstrologyPanel } from "./components/B2BAstrologyPanel"
import { B2BBillingPanel } from "./components/B2BBillingPanel"
import { B2BEditorialPanel } from "./components/B2BEditorialPanel"
import { B2BReconciliationPanel } from "./components/B2BReconciliationPanel"
import { B2BUsagePanel } from "./components/B2BUsagePanel"
import { BillingPanel } from "./components/BillingPanel"
import { EnterpriseCredentialsPanel } from "./components/EnterpriseCredentialsPanel"
import { OpsMonitoringPanel } from "./components/OpsMonitoringPanel"
import { OpsPersonaPanel } from "./components/OpsPersonaPanel"
import { PrivacyPanel } from "./components/PrivacyPanel"
import { SupportOpsPanel } from "./components/SupportOpsPanel"
import { ChatPage } from "./pages/ChatPage"
import { NatalChartPage } from "./pages/NatalChartPage"
import { useAuthMe } from "./api/authMe"
import { useAccessTokenSnapshot } from "./utils/authToken"

type ViewId =
  | "natal"
  | "chat"
  | "billing"
  | "privacy"
  | "support"
  | "ops-monitoring"
  | "ops-persona"
  | "enterprise-credentials"
  | "b2b-astrology"
  | "b2b-usage"
  | "b2b-editorial"
  | "b2b-billing"
  | "b2b-reconciliation"

type ViewDefinition = {
  id: ViewId
  label: string
  render: () => ReactNode
}

function App() {
  const accessToken = useAccessTokenSnapshot()
  const authMe = useAuthMe(accessToken)
  const role = authMe.data?.role ?? null
  const views = useMemo<ViewDefinition[]>(() => {
    if (!accessToken) {
      return [{ id: "natal", label: "Theme natal", render: () => <NatalChartPage /> }]
    }
    if (!authMe.data) {
      return [{ id: "natal", label: "Theme natal", render: () => <NatalChartPage /> }]
    }
    const base: ViewDefinition[] = [
      { id: "natal", label: "Theme natal", render: () => <NatalChartPage /> },
      { id: "chat", label: "Chat", render: () => <ChatPage /> },
      { id: "billing", label: "Abonnement", render: () => <BillingPanel /> },
      { id: "privacy", label: "Confidentialite", render: () => <PrivacyPanel /> },
    ]
    if (role === "support" || role === "ops") {
      base.push({ id: "support", label: "Support", render: () => <SupportOpsPanel /> })
    }
    if (role === "ops") {
      base.push(
        { id: "ops-monitoring", label: "Ops Monitoring", render: () => <OpsMonitoringPanel /> },
        { id: "ops-persona", label: "Ops Persona", render: () => <OpsPersonaPanel /> },
        { id: "b2b-reconciliation", label: "B2B Reconciliation", render: () => <B2BReconciliationPanel /> },
      )
    }
    if (role === "enterprise_admin") {
      base.push(
        { id: "enterprise-credentials", label: "Enterprise API", render: () => <EnterpriseCredentialsPanel /> },
        { id: "b2b-astrology", label: "B2B Astrology", render: () => <B2BAstrologyPanel /> },
        { id: "b2b-usage", label: "B2B Usage", render: () => <B2BUsagePanel /> },
        { id: "b2b-editorial", label: "B2B Editorial", render: () => <B2BEditorialPanel /> },
        { id: "b2b-billing", label: "B2B Billing", render: () => <B2BBillingPanel /> },
      )
    }
    return base
  }, [accessToken, authMe.data, role])
  const [activeView, setActiveView] = useState<ViewId>("natal")

  useEffect(() => {
    if (!views.some((view) => view.id === activeView)) {
      setActiveView(views[0]?.id ?? "natal")
    }
  }, [activeView, views])

  const currentView = views.find((view) => view.id === activeView) ?? views[0]

  return (
    <AppShell>
      {!accessToken ? (
        <section className="panel">
          <p>Aucun token detecte. Connectez-vous pour acceder aux fonctionnalités protegees.</p>
        </section>
      ) : null}
      {accessToken && authMe.isLoading ? (
        <section className="panel">
          <p>Verification de votre session en cours...</p>
        </section>
      ) : null}
      {accessToken && authMe.isError ? (
        <section className="panel">
          <p>Impossible de verifier votre profil. Les vues privilegiees sont masquees.</p>
        </section>
      ) : null}
      <section className="panel">
        <h1>Navigation</h1>
        <div className="chat-form" aria-label="Navigation application">
          {views.map((view) => (
            <button
              key={view.id}
              type="button"
              onClick={() => setActiveView(view.id)}
              disabled={currentView?.id === view.id}
            >
              {view.label}
            </button>
          ))}
        </div>
      </section>
      {currentView?.render()}
    </AppShell>
  )
}

export default App
