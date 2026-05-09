// Declare les routes applicatives avec chargement differe des ecrans lourds.
import { lazy, Suspense, type ReactNode } from "react"
import type { RouteObject } from "react-router-dom"
import { Navigate } from "react-router-dom"

import { AuthGuard } from "./guards/AuthGuard"
import { LandingRedirect } from "./guards/LandingRedirect"
import { RoleGuard } from "./guards/RoleGuard"
import { AdminGuard } from "./guards/AdminGuard"
import { AppLayout } from "../layouts/AppLayout"
import { AuthLayout } from "../layouts/AuthLayout"
import { LandingLayout } from "../layouts/LandingLayout"
import { RootLayout } from "../layouts/RootLayout"
import { EnterpriseLayout } from "../components/layout/EnterpriseLayout"
import { EnterpriseCredentialsPanel } from "../features/enterprise/EnterpriseCredentialsPanel"
import { SupportOpsPanel } from "../features/support/SupportOpsPanel"

import { ConsultationLayout } from "../features/consultations/components/ConsultationLayout"
import { LoginPage } from "../pages/LoginPage"
import { RegisterPage } from "../pages/RegisterPage"

const DashboardPage = lazy(() =>
  import("../pages/DashboardPage").then(({ DashboardPage }) => ({
    default: DashboardPage,
  })),
)
const DailyHoroscopePage = lazy(() => import("../pages/DailyHoroscopePage"))
const PrivacyPolicyPage = lazy(() =>
  import("../pages/PrivacyPolicyPage").then(({ PrivacyPolicyPage }) => ({
    default: PrivacyPolicyPage,
  })),
)
const BillingSuccessPage = lazy(() =>
  import("../pages/billing/BillingSuccessPage").then(
    ({ BillingSuccessPage }) => ({
      default: BillingSuccessPage,
    }),
  ),
)
const BillingCancelPage = lazy(() =>
  import("../pages/billing/BillingCancelPage").then(
    ({ BillingCancelPage }) => ({
      default: BillingCancelPage,
    }),
  ),
)
const NatalChartPage = lazy(() =>
  import("../pages/NatalChartPage").then(({ NatalChartPage }) => ({
    default: NatalChartPage,
  })),
)
const BirthProfilePage = lazy(() =>
  import("../pages/BirthProfilePage").then(({ BirthProfilePage }) => ({
    default: BirthProfilePage,
  })),
)
const ChatPage = lazy(() =>
  import("../pages/ChatPage").then(({ ChatPage }) => ({ default: ChatPage })),
)
const AstrologersPage = lazy(() =>
  import("../pages/AstrologersPage").then(({ AstrologersPage }) => ({
    default: AstrologersPage,
  })),
)
const AstrologerProfilePage = lazy(() =>
  import("../pages/AstrologerProfilePage").then(
    ({ AstrologerProfilePage }) => ({ default: AstrologerProfilePage }),
  ),
)
const SettingsPage = lazy(() =>
  import("../pages/SettingsPage").then(({ SettingsPage }) => ({
    default: SettingsPage,
  })),
)
const NotFoundPage = lazy(() =>
  import("../pages/NotFoundPage").then(({ NotFoundPage }) => ({
    default: NotFoundPage,
  })),
)
const ConsultationsPage = lazy(() =>
  import("../pages/ConsultationsPage").then(({ ConsultationsPage }) => ({
    default: ConsultationsPage,
  })),
)
const ConsultationWizardPage = lazy(() =>
  import("../pages/ConsultationWizardPage").then(
    ({ ConsultationWizardPage }) => ({
      default: ConsultationWizardPage,
    }),
  ),
)
const ConsultationResultPage = lazy(() =>
  import("../pages/ConsultationResultPage").then(
    ({ ConsultationResultPage }) => ({
      default: ConsultationResultPage,
    }),
  ),
)
const HelpPage = lazy(() => import("../pages/HelpPage"))
const EnterpriseDashboardPage = lazy(() =>
  import("../pages/EnterpriseDashboardPage").then(
    ({ EnterpriseDashboardPage }) => ({
      default: EnterpriseDashboardPage,
    }),
  ),
)
const AdminPage = lazy(() =>
  import("../pages/AdminPage").then(({ AdminPage }) => ({
    default: AdminPage,
  })),
)
const SubscriptionGuidePage = lazy(() =>
  import("../pages/SubscriptionGuidePage").then(
    ({ SubscriptionGuidePage }) => ({
      default: SubscriptionGuidePage,
    }),
  ),
)
const AccountSettings = lazy(() =>
  import("../pages/settings/AccountSettings").then(({ AccountSettings }) => ({
    default: AccountSettings,
  })),
)
const SubscriptionSettings = lazy(() =>
  import("../pages/settings/SubscriptionSettings").then(
    ({ SubscriptionSettings }) => ({
      default: SubscriptionSettings,
    }),
  ),
)
const UsageSettings = lazy(() =>
  import("../pages/settings/UsageSettings").then(({ UsageSettings }) => ({
    default: UsageSettings,
  })),
)
const AdminDashboardPage = lazy(() =>
  import("../pages/admin/AdminDashboardPage").then(
    ({ AdminDashboardPage }) => ({ default: AdminDashboardPage }),
  ),
)
const AdminUsersPage = lazy(() =>
  import("../pages/admin/AdminUsersPage").then(({ AdminUsersPage }) => ({
    default: AdminUsersPage,
  })),
)
const AdminUserDetailPage = lazy(() =>
  import("../pages/admin/AdminUserDetailPage").then(
    ({ AdminUserDetailPage }) => ({ default: AdminUserDetailPage }),
  ),
)
const AdminEntitlementsPage = lazy(() =>
  import("../pages/admin/AdminEntitlementsPage").then(
    ({ AdminEntitlementsPage }) => ({
      default: AdminEntitlementsPage,
    }),
  ),
)
const AdminAiGenerationsPage = lazy(() =>
  import("../pages/admin/AdminAiGenerationsPage").then(
    ({ AdminAiGenerationsPage }) => ({
      default: AdminAiGenerationsPage,
    }),
  ),
)
const AdminPromptsPage = lazy(() =>
  import("../pages/admin/AdminPromptsPage").then(({ AdminPromptsPage }) => ({
    default: AdminPromptsPage,
  })),
)
const AdminContentPage = lazy(() =>
  import("../pages/admin/AdminContentPage").then(({ AdminContentPage }) => ({
    default: AdminContentPage,
  })),
)
const AdminBillingPage = lazy(() =>
  import("../pages/admin/AdminBillingPage").then(({ AdminBillingPage }) => ({
    default: AdminBillingPage,
  })),
)
const AdminLogsPage = lazy(() =>
  import("../pages/admin/AdminLogsPage").then(({ AdminLogsPage }) => ({
    default: AdminLogsPage,
  })),
)
const AdminSupportPage = lazy(() =>
  import("../pages/admin/AdminSupportPage").then(({ AdminSupportPage }) => ({
    default: AdminSupportPage,
  })),
)
const AdminSettingsPage = lazy(() =>
  import("../pages/admin/AdminSettingsPage").then(({ AdminSettingsPage }) => ({
    default: AdminSettingsPage,
  })),
)
const AdminHubPage = lazy(() =>
  import("../pages/admin/AdminHubPage").then(({ AdminHubPage }) => ({
    default: AdminHubPage,
  })),
)
const ReconciliationAdmin = lazy(() =>
  import("../pages/admin/ReconciliationAdmin").then(
    ({ ReconciliationAdmin }) => ({ default: ReconciliationAdmin }),
  ),
)

/** Affiche un retour accessible pendant le chargement d'un chunk de route. */
export function RouteLoadingFallback() {
  return (
    <div className="panel">
      <div
        className="state-line state-loading"
        role="status"
        aria-busy="true"
        aria-live="polite"
      >
        Chargement de la page...
      </div>
    </div>
  )
}

/** Enveloppe un ecran charge a la demande dans une limite Suspense locale. */
function lazyElement(element: ReactNode) {
  return <Suspense fallback={<RouteLoadingFallback />}>{element}</Suspense>
}

/** Enfant de route pour les sections prompts : le rendu réel est entièrement dans `AdminPromptsPage`. */
function AdminPromptsRouteSlot() {
  return null
}

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <RootLayout />,
    children: [
      {
        element: <LandingLayout />,
        children: [
          {
            index: true,
            element: <LandingRedirect />,
          },
          {
            path: "privacy",
            element: lazyElement(<PrivacyPolicyPage />),
          },
        ],
      },
      {
        element: <AuthLayout />,
        children: [
          {
            path: "login",
            element: <LoginPage />,
          },
          {
            path: "register",
            element: <RegisterPage />,
          },
        ],
      },
      {
        element: (
          <AuthGuard>
            <AppLayout />
          </AuthGuard>
        ),
        children: [
          {
            path: "dashboard",
            children: [
              {
                index: true,
                element: lazyElement(<DashboardPage />),
              },
              {
                path: "horoscope",
                element: lazyElement(<DailyHoroscopePage />),
              },
            ],
          },
          {
            path: "natal",
            element: lazyElement(<NatalChartPage />),
          },
          {
            path: "profile",
            element: lazyElement(<BirthProfilePage />),
          },
          {
            path: "billing/success",
            element: lazyElement(<BillingSuccessPage />),
          },
          {
            path: "billing/cancel",
            element: lazyElement(<BillingCancelPage />),
          },
          {
            path: "chat",
            element: lazyElement(<ChatPage />),
          },
          {
            path: "chat/:conversationId",
            element: lazyElement(<ChatPage />),
          },
          {
            path: "astrologers",
            element: lazyElement(<AstrologersPage />),
          },
          {
            path: "astrologers/:id",
            element: lazyElement(<AstrologerProfilePage />),
          },
          {
            path: "consultations",
            element: <ConsultationLayout />,
            children: [
              {
                index: true,
                element: lazyElement(<ConsultationsPage />),
              },
              {
                path: "new",
                element: lazyElement(<ConsultationWizardPage />),
              },
              {
                path: "result",
                element: lazyElement(<ConsultationResultPage />),
              },
            ],
          },
          {
            path: "settings",
            element: lazyElement(<SettingsPage />),
            children: [
              {
                index: true,
                element: <Navigate to="account" replace />,
              },
              {
                path: "account",
                element: lazyElement(<AccountSettings />),
              },
              {
                path: "subscription",
                element: lazyElement(<SubscriptionSettings />),
              },
              {
                path: "usage",
                element: lazyElement(<UsageSettings />),
              },
            ],
          },
          {
            path: "help",
            element: (
              <RoleGuard roles={["user", "admin", "ops", "support"]}>
                {lazyElement(<HelpPage />)}
              </RoleGuard>
            ),
          },
          {
            path: "help/subscriptions",
            element: (
              <RoleGuard roles={["user", "admin", "ops", "support"]}>
                {lazyElement(<SubscriptionGuidePage />)}
              </RoleGuard>
            ),
          },
          {
            path: "support",
            element: (
              <RoleGuard roles={["admin", "ops", "support"]}>
                <SupportOpsPanel />
              </RoleGuard>
            ),
          },
          {
            path: "enterprise",
            element: (
              <RoleGuard roles={["enterprise_admin", "admin"]}>
                <EnterpriseLayout />
              </RoleGuard>
            ),
            children: [
              {
                index: true,
                element: lazyElement(<EnterpriseDashboardPage />),
              },
              {
                path: "credentials",
                element: <EnterpriseCredentialsPanel />,
              },
            ],
          },
          {
            path: "admin",
            element: <AdminGuard>{lazyElement(<AdminPage />)}</AdminGuard>,
            children: [
              {
                index: true,
                element: lazyElement(<AdminHubPage />),
              },
              {
                path: "dashboard",
                element: lazyElement(<AdminDashboardPage />),
              },
              {
                path: "users",
                element: lazyElement(<AdminUsersPage />),
              },
              {
                path: "users/:userId",
                element: lazyElement(<AdminUserDetailPage />),
              },
              {
                path: "entitlements",
                element: lazyElement(<AdminEntitlementsPage />),
              },
              {
                path: "ai-generations",
                element: lazyElement(<AdminAiGenerationsPage />),
              },
              {
                path: "prompts",
                element: lazyElement(<AdminPromptsPage />),
                children: [
                  { index: true, element: <Navigate to="catalog" replace /> },
                  { path: "catalog", element: <AdminPromptsRouteSlot /> },
                  { path: "archive", element: <AdminPromptsRouteSlot /> },
                  { path: "release", element: <AdminPromptsRouteSlot /> },
                  { path: "consumption", element: <AdminPromptsRouteSlot /> },
                  { path: "personas", element: <AdminPromptsRouteSlot /> },
                  {
                    path: "sample-payloads",
                    element: <AdminPromptsRouteSlot />,
                  },
                  {
                    path: "*",
                    element: <Navigate to="/admin/prompts/catalog" replace />,
                  },
                ],
              },
              {
                path: "content",
                element: lazyElement(<AdminContentPage />),
              },
              {
                path: "billing",
                element: lazyElement(<AdminBillingPage />),
              },
              {
                path: "logs",
                element: lazyElement(<AdminLogsPage />),
              },
              {
                path: "support",
                element: lazyElement(<AdminSupportPage />),
              },
              {
                path: "settings",
                element: lazyElement(<AdminSettingsPage />),
              },
              {
                path: "reconciliation",
                element: lazyElement(<ReconciliationAdmin />),
              },
            ],
          },
          {
            path: "*",
            element: lazyElement(<NotFoundPage />),
          },
        ],
      },
    ],
  },
]
