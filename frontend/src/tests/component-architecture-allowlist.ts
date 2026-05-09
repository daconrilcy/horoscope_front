// Registre exact des exceptions d'architecture du dossier components.

export type ComponentArchitectureException = {
  file: string
  owner: string
  reason: string
  exitCondition: string
}

export const COMPONENT_API_IMPORT_EXCEPTIONS: ComponentArchitectureException[] = [
  {
    file: "components/AdminGuard.tsx",
    owner: "admin routing",
    reason: "Garde d'acces admin historique consommee comme composant de protection.",
    exitCondition: "Migrer vers app/guards ou layout route-level lors de la convergence admin.",
  },
  {
    file: "components/B2BReconciliationPanel.tsx",
    owner: "enterprise dashboard",
    reason: "Panel B2B conserve comme container API exact.",
    exitCondition: "Deplacer sous une feature enterprise/b2b quand le domaine est cree.",
  },
  {
    file: "components/EnterpriseCredentialsPanel.tsx",
    owner: "enterprise dashboard",
    reason: "Panel credentials conserve comme container API exact.",
    exitCondition: "Deplacer sous une feature enterprise/b2b quand le domaine est cree.",
  },
  {
    file: "components/SupportOpsPanel.tsx",
    owner: "admin operations",
    reason: "Panel support ops conserve comme container API exact.",
    exitCondition: "Deplacer sous une feature admin-ops quand le domaine est cree.",
  },
  {
    file: "components/dashboard/useDashboardAstroSummary.ts",
    owner: "dashboard summary",
    reason: "Hook dashboard historique localise sous components/dashboard.",
    exitCondition: "Deplacer sous hooks ou feature dashboard.",
  },
  {
    file: "components/layout/BottomNav.tsx",
    owner: "app layout",
    reason: "Navigation layout dependante de l'etat auth.",
    exitCondition: "Remplacer par un provider route-level ou prop issue du layout.",
  },
  {
    file: "components/layout/Header.tsx",
    owner: "app layout",
    reason: "Header layout dependant de l'etat auth.",
    exitCondition: "Remplacer par un provider route-level ou prop issue du layout.",
  },
  {
    file: "components/layout/Sidebar.tsx",
    owner: "app layout",
    reason: "Sidebar layout dependante de l'etat auth.",
    exitCondition: "Remplacer par un provider route-level ou prop issue du layout.",
  },
  {
    file: "components/settings/DeleteAccountModal.tsx",
    owner: "settings privacy",
    reason: "Modal settings historique avec mutation API privacy.",
    exitCondition: "Deplacer sous pages/settings ou feature privacy.",
  },
  {
    file: "components/ui/UpgradeCTA/UpgradeCTA.test.tsx",
    owner: "ui tests",
    reason: "Test de primitive qui importe uniquement le type UpgradeHint.",
    exitCondition: "Extraire le type vers un contrat UI neutre si la primitive sort du domaine billing.",
  },
]

export const COMPONENT_TS_NOCHECK_EXCEPTIONS: ComponentArchitectureException[] = []
