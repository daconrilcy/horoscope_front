// Declare les exceptions exactes de l'architecture des pages avec owner et sortie.
export type PageArchitectureException = {
  file: string
  owner: string
  reason: string
  exit: string
}

export const TS_NOCHECK_PAGE_EXCEPTIONS: PageArchitectureException[] = []

export const DIRECT_API_PAGE_EXCEPTIONS: PageArchitectureException[] = []

export const PAGE_SIZE_EXCEPTIONS: Array<PageArchitectureException & { maxLines: number }> = [
  {
    file: "pages/admin/AdminPromptsPage.tsx",
    maxLines: 2700,
    owner: "frontend-react-pages/admin-prompts",
    reason: "conteneur route catalogue/archive apres extraction des helpers et modales partagees CS-096",
    exit: "prochaines stories de reduction des sections JSX catalogue et consommation",
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
