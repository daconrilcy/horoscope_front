# CS-107 - Inventaire pages apres

Source executable: `frontend/src/tests/page-architecture-allowlist.ts`, export `PAGE_LAYOUT_OWNER_CLASSIFICATIONS`.

## Decisions globales

- Zero fichier `frontend/src/pages/**/*.tsx` non classe.
- Les routes applicatives/admin/auth/landing ont un owner layout prouve par `page-architecture-guards.test.ts`.
- Les composants page-adjacent restent classes avec owner exact; aucune relocation n'est faite dans cette story.
- Les pages publiques potentielles `PrivacyPolicyPage`, `BillingSuccessPage` et `BillingCancelPage` restent non routees avec decisions CS-108, owner et expiry explicites.
- Les candidats morts `HomePage` et `TestimonialsSection` ne sont pas supprimes; CS-108 les retient jusqu'a story de retrait dediee.

## Classification par fichier

| File | Classification | Route / owner | Decision |
|---|---|---|---|
| `pages/landing/LandingPage.tsx` | `routed-page` | `/` via `LandingLayout` sous `RootLayout` | keep |
| `pages/LoginPage.tsx` | `routed-page` | `/login` via `AuthLayout` sous `RootLayout` | keep |
| `pages/RegisterPage.tsx` | `routed-page` | `/register` via `AuthLayout` sous `RootLayout` | keep |
| `pages/DashboardPage.tsx` | `routed-page` | `/dashboard` via `AppLayout` sous `RootLayout` | keep |
| `pages/DailyHoroscopePage.tsx` | `nested-routed-page` | `/dashboard/horoscope` via `AppLayout` | keep |
| `pages/NatalChartPage.tsx` | `routed-page` | `/natal` via `AppLayout` | keep |
| `pages/BirthProfilePage.tsx` | `routed-page` | `/profile` via `AppLayout` | keep |
| `pages/ChatPage.tsx` | `routed-page` | `/chat`, `/chat/:conversationId` via `AppLayout` | keep |
| `pages/AstrologersPage.tsx` | `routed-page` | `/astrologers` via `AppLayout` | keep |
| `pages/AstrologerProfilePage.tsx` | `routed-page` | `/astrologers/:id` via `AppLayout` | keep |
| `pages/ConsultationsPage.tsx` | `nested-routed-page` | `/consultations` via `ConsultationLayout` | keep |
| `pages/ConsultationWizardPage.tsx` | `nested-routed-page` | `/consultations/new` via `ConsultationLayout` | keep |
| `pages/ConsultationResultPage.tsx` | `nested-routed-page` | `/consultations/result` via `ConsultationLayout` | keep |
| `pages/SettingsPage.tsx` | `nested-routed-page` | `/settings` layout secondaire sous `AppLayout` | keep |
| `pages/settings/AccountSettings.tsx` | `nested-routed-page` | `/settings/account` | keep |
| `pages/settings/SubscriptionSettings.tsx` | `nested-routed-page` | `/settings/subscription` | keep |
| `pages/settings/UsageSettings.tsx` | `nested-routed-page` | `/settings/usage` | keep |
| `pages/HelpPage.tsx` | `routed-page` | `/help` via `RoleGuard` et `AppLayout` | keep |
| `pages/SubscriptionGuidePage.tsx` | `routed-page` | `/help/subscriptions` via `RoleGuard` et `AppLayout` | keep |
| `pages/EnterpriseDashboardPage.tsx` | `nested-routed-page` | `/enterprise` via `EnterpriseLayout` | keep |
| `pages/AdminPage.tsx` | `nested-routed-page` | `/admin` owner `AdminLayout` via `AdminPage` | keep |
| `pages/admin/AdminHubPage.tsx` | `nested-routed-page` | `/admin` | keep |
| `pages/admin/AdminDashboardPage.tsx` | `nested-routed-page` | `/admin/dashboard` | keep |
| `pages/admin/AdminUsersPage.tsx` | `nested-routed-page` | `/admin/users` | keep |
| `pages/admin/AdminUserDetailPage.tsx` | `nested-routed-page` | `/admin/users/:userId` | keep |
| `pages/admin/AdminEntitlementsPage.tsx` | `nested-routed-page` | `/admin/entitlements` | keep |
| `pages/admin/AdminAiGenerationsPage.tsx` | `nested-routed-page` | `/admin/ai-generations` | keep |
| `pages/admin/AdminPromptsPage.tsx` | `nested-routed-page` | `/admin/prompts` | keep |
| `pages/admin/AdminContentPage.tsx` | `nested-routed-page` | `/admin/content` | keep |
| `pages/admin/AdminBillingPage.tsx` | `nested-routed-page` | `/admin/billing` | keep |
| `pages/admin/AdminLogsPage.tsx` | `nested-routed-page` | `/admin/logs` | keep |
| `pages/admin/AdminSupportPage.tsx` | `nested-routed-page` | `/admin/support` | keep |
| `pages/admin/AdminSettingsPage.tsx` | `nested-routed-page` | `/admin/settings` | keep |
| `pages/admin/ReconciliationAdmin.tsx` | `nested-routed-page` | `/admin/reconciliation` | keep |
| `pages/admin/AdminPricingPanel.tsx` | `page-adjacent-component` | owner `AdminBillingPage` | keep-classified |
| `pages/support/SupportCategorySelect.tsx` | `page-adjacent-component` | owner `HelpPage` | keep-classified |
| `pages/support/SupportTicketForm.tsx` | `page-adjacent-component` | owner `HelpPage` | keep-classified |
| `pages/support/SupportTicketList.tsx` | `page-adjacent-component` | owner `HelpPage` | keep-classified |
| `pages/landing/sections/FaqSection.tsx` | `page-adjacent-component` | owner `LandingPage` | keep-classified |
| `pages/landing/sections/HeroSection.tsx` | `page-adjacent-component` | owner `LandingPage` | keep-classified |
| `pages/landing/sections/LandingFooter.tsx` | `page-adjacent-component` | owner `LandingLayout` | keep-classified |
| `pages/landing/sections/LandingNavbar.tsx` | `page-adjacent-component` | owner `LandingLayout` | keep-classified |
| `pages/landing/sections/PricingSection.tsx` | `page-adjacent-component` | owner `LandingPage` | keep-classified |
| `pages/landing/sections/ProblemSection.tsx` | `page-adjacent-component` | owner `LandingPage` | keep-classified |
| `pages/landing/sections/SocialProofSection.tsx` | `page-adjacent-component` | owner `LandingPage` | keep-classified |
| `pages/landing/sections/SolutionSection.tsx` | `page-adjacent-component` | owner `LandingPage` | keep-classified |
| `pages/landing/sections/TestimonialsSection.tsx` | `dead/unmounted-page-candidate` | owner `Product removal decision owner`; decisionSource CS-108; aucun import runtime actif detecte | keep pending dedicated removal story |
| `pages/PrivacyPolicyPage.tsx` | `needs-user-decision` | owner `Legal/Product decision owner`; decisionSource CS-108; non routee; expiry `2026-06-30` | block routing/deletion until named legal/product decision |
| `pages/billing/BillingSuccessPage.tsx` | `needs-user-decision` | owner `Billing/Stripe decision owner`; decisionSource CS-108; non routee; expiry `2026-06-30` | block routing/deletion until named billing decision |
| `pages/billing/BillingCancelPage.tsx` | `needs-user-decision` | owner `Billing/Stripe decision owner`; decisionSource CS-108; non routee; expiry `2026-06-30` | block routing/deletion until named billing decision |
| `pages/HomePage.tsx` | `dead/unmounted-page-candidate` | owner `Product removal decision owner`; decisionSource CS-108; aucun export barrel ni route | keep pending dedicated removal story |
| `pages/NotFoundPage.tsx` | `routed-page` | `*` sous `AppLayout` | keep |

## Guard

- `npm run test -- page-architecture` echoue si un fichier page est absent du registre.
- `npm run test -- page-architecture` echoue si une entree `needs-user-decision` est routee dans `routes.tsx`.
- `npm run test -- page-architecture` echoue si une entree `needs-user-decision` ou `dead/unmounted-page-candidate` conserve une decision sans `decisionSource` structuree ou sans sortie explicite.
- `npm run test -- page-architecture` echoue si une entree `dead/unmounted-page-candidate` est routee ou rattachee par import runtime.
- Aucun wildcard ni exception folder-wide n'est present.
