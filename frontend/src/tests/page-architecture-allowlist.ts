// Declare les exceptions exactes de l'architecture des pages avec owner et sortie.
export type PageArchitectureException = {
  file: string
  owner: string
  reason: string
  exit: string
}

export type PageLayoutOwnerClassification = PageArchitectureException & {
  classification:
    | "routed-page"
    | "nested-routed-page"
    | "page-adjacent-component"
    | "dead/unmounted-page-candidate"
    | "needs-user-decision"
  route?: string
  decisionSource?: {
    story: string
    decidedOn: string
    owner: string
    evidence: string
  }
  expiresOn?: string
  removalStory?: string
}

export const TS_NOCHECK_PAGE_EXCEPTIONS: PageArchitectureException[] = []

export const DIRECT_API_PAGE_EXCEPTIONS: PageArchitectureException[] = []

export const PAGE_SIZE_EXCEPTIONS: Array<
  PageArchitectureException & { maxLines: number }
> = []

export const FORBIDDEN_PUBLIC_ROUTE_ALIASES = [
  `/${"today"}`,
  `/${"natal"}-${"chart"}`,
  `/${"birth"}-${"profile"}`,
] as const
export const FORBIDDEN_ADMIN_BARREL_EXPORTS = [
  `Pricing${"Admin"}`,
  `Monitoring${"Admin"}`,
] as const

export const PAGE_LAYOUT_OWNER_CLASSIFICATIONS: PageLayoutOwnerClassification[] =
  [
    {
      file: "pages/landing/LandingPage.tsx",
      classification: "routed-page",
      route: "/",
      owner: "LandingLayout sous RootLayout",
      reason: "Contenu de la landing publique rendu par LandingRedirect.",
      exit: "Garde de route landing et inventaire CS-107.",
    },
    {
      file: "pages/LoginPage.tsx",
      classification: "routed-page",
      route: "/login",
      owner: "AuthLayout sous RootLayout",
      reason: "Page de connexion publique sous layout auth secondaire.",
      exit: "Garde directe des routes auth.",
    },
    {
      file: "pages/RegisterPage.tsx",
      classification: "routed-page",
      route: "/register",
      owner: "AuthLayout sous RootLayout",
      reason: "Page d'inscription publique sous layout auth secondaire.",
      exit: "Garde directe des routes auth.",
    },
    {
      file: "pages/DashboardPage.tsx",
      classification: "routed-page",
      route: "/dashboard",
      owner: "AppLayout sous RootLayout",
      reason: "Page tableau de bord protegee.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/DailyHoroscopePage.tsx",
      classification: "nested-routed-page",
      route: "/dashboard/horoscope",
      owner: "AppLayout sous RootLayout",
      reason: "Sous-route horoscope du dashboard protege.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/NatalChartPage.tsx",
      classification: "routed-page",
      route: "/natal",
      owner: "AppLayout sous RootLayout",
      reason: "Page carte natale protegee.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/BirthProfilePage.tsx",
      classification: "routed-page",
      route: "/profile",
      owner: "AppLayout sous RootLayout",
      reason: "Page profil de naissance protegee.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/ChatPage.tsx",
      classification: "routed-page",
      route: "/chat et /chat/:conversationId",
      owner: "AppLayout sous RootLayout",
      reason: "Page chat protegee avec route detail conversation.",
      exit: "Routes protegees conservees.",
    },
    {
      file: "pages/AstrologersPage.tsx",
      classification: "routed-page",
      route: "/astrologers",
      owner: "AppLayout sous RootLayout",
      reason: "Liste astrologues protegee.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/AstrologerProfilePage.tsx",
      classification: "routed-page",
      route: "/astrologers/:id",
      owner: "AppLayout sous RootLayout",
      reason: "Profil astrologue protege.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/ConsultationsPage.tsx",
      classification: "nested-routed-page",
      route: "/consultations",
      owner: "ConsultationLayout puis AppLayout sous RootLayout",
      reason: "Index des consultations dans le layout consultation.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/ConsultationWizardPage.tsx",
      classification: "nested-routed-page",
      route: "/consultations/new",
      owner: "ConsultationLayout puis AppLayout sous RootLayout",
      reason: "Assistant consultation dans le layout consultation.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/ConsultationResultPage.tsx",
      classification: "nested-routed-page",
      route: "/consultations/result",
      owner: "ConsultationLayout puis AppLayout sous RootLayout",
      reason: "Resultat consultation dans le layout consultation.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/SettingsPage.tsx",
      classification: "nested-routed-page",
      route: "/settings",
      owner:
        "SettingsPage comme layout secondaire puis AppLayout sous RootLayout",
      reason: "Layout de section settings avec sous-routes.",
      exit: "Routes settings conservees.",
    },
    {
      file: "pages/settings/AccountSettings.tsx",
      classification: "nested-routed-page",
      route: "/settings/account",
      owner: "SettingsPage puis AppLayout sous RootLayout",
      reason: "Sous-page compte.",
      exit: "Route settings conservee.",
    },
    {
      file: "pages/settings/SubscriptionSettings.tsx",
      classification: "nested-routed-page",
      route: "/settings/subscription",
      owner: "SettingsPage puis AppLayout sous RootLayout",
      reason: "Sous-page abonnement.",
      exit: "Route settings conservee.",
    },
    {
      file: "pages/settings/UsageSettings.tsx",
      classification: "nested-routed-page",
      route: "/settings/usage",
      owner: "SettingsPage puis AppLayout sous RootLayout",
      reason: "Sous-page usage.",
      exit: "Route settings conservee.",
    },
    {
      file: "pages/HelpPage.tsx",
      classification: "routed-page",
      route: "/help",
      owner: "RoleGuard puis AppLayout sous RootLayout",
      reason: "Page aide protegee par roles.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/SubscriptionGuidePage.tsx",
      classification: "routed-page",
      route: "/help/subscriptions",
      owner: "RoleGuard puis AppLayout sous RootLayout",
      reason: "Guide abonnement protege par roles.",
      exit: "Route protegee conservee.",
    },
    {
      file: "pages/EnterpriseDashboardPage.tsx",
      classification: "nested-routed-page",
      route: "/enterprise",
      owner: "EnterpriseLayout puis AppLayout sous RootLayout",
      reason: "Index enterprise protege.",
      exit: "Route enterprise conservee.",
    },
    {
      file: "pages/AdminPage.tsx",
      classification: "nested-routed-page",
      route: "/admin",
      owner: "AdminLayout via AdminPage puis AppLayout sous RootLayout",
      reason: "Layout de section admin.",
      exit: "Routes admin conservees.",
    },
    {
      file: "pages/admin/AdminHubPage.tsx",
      classification: "nested-routed-page",
      route: "/admin",
      owner: "AdminLayout via AdminPage",
      reason: "Index admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminDashboardPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/dashboard",
      owner: "AdminLayout via AdminPage",
      reason: "Dashboard admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminUsersPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/users",
      owner: "AdminLayout via AdminPage",
      reason: "Liste utilisateurs admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminUserDetailPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/users/:userId",
      owner: "AdminLayout via AdminPage",
      reason: "Detail utilisateur admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminEntitlementsPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/entitlements",
      owner: "AdminLayout via AdminPage",
      reason: "Entitlements admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminAiGenerationsPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/ai-generations",
      owner: "AdminLayout via AdminPage",
      reason: "Generations IA admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminPromptsPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/prompts",
      owner: "AdminLayout via AdminPage",
      reason: "Prompts admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminContentPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/content",
      owner: "AdminLayout via AdminPage",
      reason: "Contenu admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminBillingPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/billing",
      owner: "AdminLayout via AdminPage",
      reason: "Billing admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminLogsPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/logs",
      owner: "AdminLayout via AdminPage",
      reason: "Logs admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminSupportPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/support",
      owner: "AdminLayout via AdminPage",
      reason: "Support admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminSettingsPage.tsx",
      classification: "nested-routed-page",
      route: "/admin/settings",
      owner: "AdminLayout via AdminPage",
      reason: "Settings admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/ReconciliationAdmin.tsx",
      classification: "nested-routed-page",
      route: "/admin/reconciliation",
      owner: "AdminLayout via AdminPage",
      reason: "Reconciliation admin.",
      exit: "Route admin conservee.",
    },
    {
      file: "pages/admin/AdminPricingPanel.tsx",
      classification: "page-adjacent-component",
      owner: "AdminBillingPage",
      reason: "Panneau importe par la page billing admin.",
      exit: "Relocalisation feature-admin-billing ulterieure si demandee.",
    },
    {
      file: "pages/support/SupportCategorySelect.tsx",
      classification: "page-adjacent-component",
      owner: "HelpPage",
      reason: "Composant de formulaire support importe par HelpPage.",
      exit: "Relocalisation support feature ulterieure si demandee.",
    },
    {
      file: "pages/support/SupportTicketForm.tsx",
      classification: "page-adjacent-component",
      owner: "HelpPage",
      reason: "Composant de creation ticket importe par HelpPage.",
      exit: "Relocalisation support feature ulterieure si demandee.",
    },
    {
      file: "pages/support/SupportTicketList.tsx",
      classification: "page-adjacent-component",
      owner: "HelpPage",
      reason: "Composant de liste tickets importe par HelpPage.",
      exit: "Relocalisation support feature ulterieure si demandee.",
    },
    {
      file: "pages/landing/sections/FaqSection.tsx",
      classification: "page-adjacent-component",
      owner: "LandingPage",
      reason: "Section composee par LandingPage.",
      exit: "Reste sous namespace landing tant que LandingPage en est l'owner.",
    },
    {
      file: "pages/landing/sections/HeroSection.tsx",
      classification: "page-adjacent-component",
      owner: "LandingPage",
      reason: "Section composee par LandingPage.",
      exit: "Reste sous namespace landing tant que LandingPage en est l'owner.",
    },
    {
      file: "pages/landing/sections/LandingFooter.tsx",
      classification: "page-adjacent-component",
      owner: "LandingLayout",
      reason: "Footer canonique du layout landing.",
      exit: "Reste sous namespace landing tant que LandingLayout en est l'owner.",
    },
    {
      file: "pages/landing/sections/LandingNavbar.tsx",
      classification: "page-adjacent-component",
      owner: "LandingLayout",
      reason: "Navbar canonique du layout landing.",
      exit: "Reste sous namespace landing tant que LandingLayout en est l'owner.",
    },
    {
      file: "pages/landing/sections/PricingSection.tsx",
      classification: "page-adjacent-component",
      owner: "LandingPage",
      reason: "Section composee par LandingPage.",
      exit: "Reste sous namespace landing tant que LandingPage en est l'owner.",
    },
    {
      file: "pages/landing/sections/ProblemSection.tsx",
      classification: "page-adjacent-component",
      owner: "LandingPage",
      reason: "Section composee par LandingPage.",
      exit: "Reste sous namespace landing tant que LandingPage en est l'owner.",
    },
    {
      file: "pages/landing/sections/SocialProofSection.tsx",
      classification: "page-adjacent-component",
      owner: "LandingPage",
      reason: "Section composee par LandingPage.",
      exit: "Reste sous namespace landing tant que LandingPage en est l'owner.",
    },
    {
      file: "pages/landing/sections/SolutionSection.tsx",
      classification: "page-adjacent-component",
      owner: "LandingPage",
      reason: "Section composee par LandingPage.",
      exit: "Reste sous namespace landing tant que LandingPage en est l'owner.",
    },
    {
      file: "pages/landing/sections/TestimonialsSection.tsx",
      classification: "page-adjacent-component",
      owner: "LandingPage",
      reason:
        "Section testimonials rattachee a LandingPage par decision produit.",
      exit:
        "Reste sous namespace landing tant que LandingPage en est l'owner.",
      decisionSource: {
        story: "CS-109-fermer-decisions-residuelles-pages-layout",
        decidedOn: "2026-05-08",
        owner: "LandingPage",
        evidence:
          "_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-after.md",
      },
    },
    {
      file: "pages/PrivacyPolicyPage.tsx",
      classification: "routed-page",
      route: "/privacy",
      owner: "LandingLayout sous RootLayout",
      reason:
        "Page privacy publique routee apres decision utilisateur.",
      exit:
        "Route publique conservee sous owner landing.",
      decisionSource: {
        story: "CS-109-fermer-decisions-residuelles-pages-layout",
        decidedOn: "2026-05-08",
        owner: "LandingLayout sous RootLayout",
        evidence:
          "_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-after.md",
      },
    },
    {
      file: "pages/billing/BillingSuccessPage.tsx",
      classification: "routed-page",
      route: "/billing/success",
      owner: "AppLayout sous RootLayout",
      reason:
        "Callback success Stripe route car STRIPE_CHECKOUT_SUCCESS_URL pointe vers /billing/success par defaut.",
      exit:
        "Route callback conservee tant que la config checkout Stripe utilise ce chemin.",
      decisionSource: {
        story: "CS-109-fermer-decisions-residuelles-pages-layout",
        decidedOn: "2026-05-08",
        owner: "AppLayout sous RootLayout",
        evidence:
          "_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-after.md",
      },
    },
    {
      file: "pages/billing/BillingCancelPage.tsx",
      classification: "routed-page",
      route: "/billing/cancel",
      owner: "AppLayout sous RootLayout",
      reason:
        "Callback cancel Stripe route car STRIPE_CHECKOUT_CANCEL_URL pointe vers /billing/cancel par defaut.",
      exit:
        "Route callback conservee tant que la config checkout Stripe utilise ce chemin.",
      decisionSource: {
        story: "CS-109-fermer-decisions-residuelles-pages-layout",
        decidedOn: "2026-05-08",
        owner: "AppLayout sous RootLayout",
        evidence:
          "_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-after.md",
      },
    },
    {
      file: "pages/NotFoundPage.tsx",
      classification: "routed-page",
      route: "*",
      owner: "AppLayout sous RootLayout",
      reason: "Route catch-all protegee existante.",
      exit: "Route catch-all conservee.",
    },
  ]
