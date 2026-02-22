import { useEffect, useMemo, useState } from "react"

import "./App.css"
import { AppShell } from "./components/AppShell"
import { SignInForm } from "./components/SignInForm"
import { SignUpForm } from "./components/SignUpForm"
import { HomePage } from "./pages/HomePage"
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
import { BirthProfilePage } from "./pages/BirthProfilePage"
import { ChatPage } from "./pages/ChatPage"
import { NatalChartPage } from "./pages/NatalChartPage"
import { useAuthMe } from "./api/authMe"
import { clearAccessToken, useAccessTokenSnapshot } from "./utils/authToken"

export type ViewId =
  | "natal"
  | "chat"
  | "billing"
  | "privacy"
  | "profil-natal"
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
}

type AuthView = "home" | "signin" | "register"

function App() {
  const accessToken = useAccessTokenSnapshot()
  const [authView, setAuthView] = useState<AuthView>("home")

  useEffect(() => {
    const handleAuthChange = () => {
      if (!window.localStorage.getItem("access_token")) {
        setAuthView("home")
      }
    }
    window.addEventListener("auth-token-changed", handleAuthChange)
    window.addEventListener("storage", handleAuthChange)
    return () => {
      window.removeEventListener("auth-token-changed", handleAuthChange)
      window.removeEventListener("storage", handleAuthChange)
    }
  }, [])

  useEffect(() => {
    if (!accessToken) setAuthView("home")
  }, [accessToken])

  const authMe = useAuthMe(accessToken)
  const role = authMe.data?.role ?? null

  const [activeView, setActiveView] = useState<ViewId>("natal")

  const views = useMemo<ViewDefinition[]>(() => {
    if (!accessToken || !authMe.data) {
      return [{ id: "natal", label: "Thème natal" }]
    }
    const base: ViewDefinition[] = [
      { id: "natal", label: "Thème natal" },
      { id: "chat", label: "Chat" },
      { id: "billing", label: "Abonnement" },
      { id: "privacy", label: "Confidentialité" },
      { id: "profil-natal", label: "Mon profil natal" },
    ]
    if (role === "support" || role === "ops") {
      base.push({ id: "support", label: "Support" })
    }
    if (role === "ops") {
      base.push(
        { id: "ops-monitoring", label: "Monitoring Ops" },
        { id: "ops-persona", label: "Persona Ops" },
        { id: "b2b-reconciliation", label: "Réconciliation B2B" },
      )
    }
    if (role === "enterprise_admin") {
      base.push(
        { id: "enterprise-credentials", label: "API Entreprise" },
        { id: "b2b-astrology", label: "Astrologie B2B" },
        { id: "b2b-usage", label: "Usage B2B" },
        { id: "b2b-editorial", label: "Éditorial B2B" },
        { id: "b2b-billing", label: "Facturation B2B" },
      )
    }
    return base
  }, [accessToken, authMe.data, role])

  useEffect(() => {
    if (!views.some((view) => view.id === activeView)) {
      setActiveView(views[0]?.id ?? "natal")
    }
  }, [activeView, views])

  const currentViewId = views.find((view) => view.id === activeView)?.id ?? views[0]?.id ?? "natal"

  const renderView = () => {
    switch (currentViewId) {
      case "chat":
        return <ChatPage />
      case "billing":
        return <BillingPanel />
      case "privacy":
        return <PrivacyPanel />
      case "profil-natal":
        return <BirthProfilePage onNavigate={setActiveView} />
      case "support":
        return <SupportOpsPanel />
      case "ops-monitoring":
        return <OpsMonitoringPanel />
      case "ops-persona":
        return <OpsPersonaPanel />
      case "b2b-reconciliation":
        return <B2BReconciliationPanel />
      case "enterprise-credentials":
        return <EnterpriseCredentialsPanel />
      case "b2b-astrology":
        return <B2BAstrologyPanel />
      case "b2b-usage":
        return <B2BUsagePanel />
      case "b2b-editorial":
        return <B2BEditorialPanel />
      case "b2b-billing":
        return <B2BBillingPanel />
      case "natal":
      default:
        return <NatalChartPage />
    }
  }

  return (
    <AppShell>
      {!accessToken && authView === "home" ? (
        <HomePage
          onSignIn={() => setAuthView("signin")}
          onRegister={() => setAuthView("register")}
        />
      ) : null}
      {!accessToken && authView === "signin" ? (
        <SignInForm onRegister={() => setAuthView("register")} />
      ) : null}
      {!accessToken && authView === "register" ? (
        <SignUpForm onSignIn={() => setAuthView("signin")} />
      ) : null}
      {accessToken && authMe.isLoading ? (
        <section className="panel">
          <p>Vérification de votre session en cours...</p>
        </section>
      ) : null}
      {accessToken && authMe.isError ? (
        <section className="panel">
          <p>Impossible de vérifier votre profil. Les vues privilégiées sont masquées.</p>
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
              disabled={currentViewId === view.id}
            >
              {view.label}
            </button>
          ))}
          {accessToken ? (
            <button type="button" onClick={clearAccessToken}>
              Se déconnecter
            </button>
          ) : null}
        </div>
      </section>
      {renderView()}
    </AppShell>
  )
}

export default App
