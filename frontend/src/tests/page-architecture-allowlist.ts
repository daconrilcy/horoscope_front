// Declare les exceptions exactes de l'architecture des pages avec owner et sortie.
export type PageArchitectureException = {
  file: string
  owner: string
  reason: string
  exit: string
}

export const TS_NOCHECK_PAGE_EXCEPTIONS: PageArchitectureException[] = [
  {
    file: "pages/AstrologerProfilePage.tsx",
    owner: "frontend-react-pages/profile",
    reason: "profil astrologue non traite par CS-090 a CS-095",
    exit: "story dediee de typage de la page profil astrologue",
  },
  {
    file: "pages/ConsultationResultPage.tsx",
    owner: "frontend-react-pages/consultations",
    reason: "resultat consultation hors lot pages admin/public-route actuel",
    exit: "story dediee de typage du resultat consultation",
  },
  {
    file: "pages/NotFoundPage.tsx",
    owner: "frontend-react-pages/routing",
    reason: "page courte hors lot de convergence des alias publics",
    exit: "story dediee de typage des pages route-support",
  },
]

export const DIRECT_API_PAGE_EXCEPTIONS: PageArchitectureException[] = [
  {
    file: "pages/admin/AdminAiGenerationsPage.tsx",
    owner: "frontend-react-pages/admin-ai",
    reason: "cluster admin AI hors CS-091",
    exit: "story dediee de centralisation API admin AI",
  },
  {
    file: "pages/admin/AdminEntitlementsPage.tsx",
    owner: "frontend-react-pages/admin-entitlements",
    reason: "cluster entitlements hors CS-091",
    exit: "story dediee de centralisation API entitlements admin",
  },
  {
    file: "pages/admin/AdminSettingsPage.tsx",
    owner: "frontend-react-pages/admin-settings",
    reason: "exports admin hors CS-091",
    exit: "story dediee de centralisation API settings admin",
  },
  {
    file: "pages/admin/AdminSupportPage.tsx",
    owner: "frontend-react-pages/admin-support",
    reason: "cluster support hors CS-091",
    exit: "story dediee de centralisation API support admin",
  },
]

export const PAGE_SIZE_EXCEPTIONS: Array<PageArchitectureException & { maxLines: number }> = [
  {
    file: "pages/admin/AdminPromptsPage.tsx",
    maxLines: 3200,
    owner: "frontend-react-pages/admin-prompts",
    reason: "conteneur route encore volumineux apres extraction CS-090",
    exit: "stories incrementales admin-prompts de reduction par sous-surface",
  },
  {
    file: "pages/AstrologerProfilePage.tsx",
    maxLines: 900,
    owner: "frontend-react-pages/profile",
    reason: "surface profil hors lot CS-090 a CS-095",
    exit: "story dediee profil astrologue",
  },
  {
    file: "pages/BirthProfilePage.tsx",
    maxLines: 800,
    owner: "frontend-react-pages/birth-profile",
    reason: "surface publique conservee mais gardee par seuil exact",
    exit: "story dediee de decomposition birth profile",
  },
  {
    file: "pages/admin/AdminSamplePayloadsAdmin.tsx",
    maxLines: 780,
    owner: "frontend-react-pages/admin-prompts",
    reason: "sous-surface sample payloads hors extraction CS-090",
    exit: "story dediee sample payloads admin-prompts",
  },
  {
    file: "pages/settings/SubscriptionSettings.tsx",
    maxLines: 850,
    owner: "frontend-react-pages/settings-subscription",
    reason: "settings abonnement hors lot actuel",
    exit: "story dediee de decomposition subscription settings",
  },
]

export const FORBIDDEN_PUBLIC_ROUTE_ALIASES = [
  `/${"today"}`,
  `/${"natal"}-${"chart"}`,
  `/${"birth"}-${"profile"}`,
] as const
export const FORBIDDEN_ADMIN_BARREL_EXPORTS = [`Pricing${"Admin"}`, `Monitoring${"Admin"}`] as const
