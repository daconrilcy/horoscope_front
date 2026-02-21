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

function App() {
  return (
    <AppShell>
      <B2BAstrologyPanel />
      <B2BBillingPanel />
      <B2BEditorialPanel />
      <B2BReconciliationPanel />
      <B2BUsagePanel />
      <EnterpriseCredentialsPanel />
      <OpsMonitoringPanel />
      <OpsPersonaPanel />
      <SupportOpsPanel />
      <BillingPanel />
      <PrivacyPanel />
      <ChatPage />
      <NatalChartPage />
    </AppShell>
  )
}

export default App
