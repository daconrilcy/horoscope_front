import type { RouteObject } from "react-router-dom"
import { Navigate } from "react-router-dom"

import { AuthGuard } from "./guards/AuthGuard"
import { LandingRedirect } from "./guards/LandingRedirect"
import { RoleGuard } from "./guards/RoleGuard"
import { AdminGuard } from "../components/AdminGuard"
import { AppLayout } from "../layouts/AppLayout"
import { EnterpriseLayout } from "../components/layout/EnterpriseLayout"
import { EnterpriseCredentialsPanel } from "../components/EnterpriseCredentialsPanel"
import { SupportOpsPanel } from "../components/SupportOpsPanel"

// Pages
import { DashboardPage } from "../pages/DashboardPage"
import DailyHoroscopePage from "../pages/DailyHoroscopePage"
import { NatalChartPage } from "../pages/NatalChartPage"
import { BirthProfilePage } from "../pages/BirthProfilePage"
import { ChatPage } from "../pages/ChatPage"
import { AstrologersPage } from "../pages/AstrologersPage"
import { AstrologerProfilePage } from "../pages/AstrologerProfilePage"
import { SettingsPage } from "../pages/SettingsPage"
import { LoginPage } from "../pages/LoginPage"
import { RegisterPage } from "../pages/RegisterPage"
import { NotFoundPage } from "../pages/NotFoundPage"
import { ConsultationsPage } from "../pages/ConsultationsPage"
import { ConsultationWizardPage } from "../pages/ConsultationWizardPage"
import { ConsultationResultPage } from "../pages/ConsultationResultPage"
import HelpPage from "../pages/HelpPage"
import { EnterpriseDashboardPage } from "../pages/EnterpriseDashboardPage"
import { AdminPage } from "../pages/AdminPage"
import { SubscriptionGuidePage } from "../pages/SubscriptionGuidePage"
import { ConsultationLayout } from "../features/consultations/components/ConsultationLayout"
import { AccountSettings } from "../pages/settings/AccountSettings"
import { SubscriptionSettings } from "../pages/settings/SubscriptionSettings"
import { UsageSettings } from "../pages/settings/UsageSettings"

import {
  AdminDashboardPage,
  AdminUsersPage,
  AdminUserDetailPage,
  AdminEntitlementsPage,
  AdminAiGenerationsPage,
  AdminPromptsPage,
  AdminContentPage,
  AdminBillingPage,
  AdminLogsPage,
  AdminSupportPage,
  AdminSettingsPage,
  AdminHubPage,
  ReconciliationAdmin
} from "../pages/admin"

/** Enfant de route pour les sections prompts : le rendu réel est entièrement dans `AdminPromptsPage`. */
function AdminPromptsRouteSlot() {
  return null
}

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <LandingRedirect />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    path: "/",
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
            element: <DashboardPage />,
          },
          {
            path: "horoscope",
            element: <DailyHoroscopePage />,
          },
        ],
      },
      {
        path: "today",
        element: <Navigate to="/dashboard/horoscope" replace />,
      },
      {
        path: "natal",
        element: <NatalChartPage />,
      },
      {
        path: "natal-chart",
        element: <NatalChartPage />,
      },
      {
        path: "profile",
        element: <BirthProfilePage />,
      },
      {
        path: "birth-profile",
        element: <Navigate to="/profile" replace />,
      },
      {
        path: "chat",
        element: <ChatPage />,
      },
      {
        path: "chat/:conversationId",
        element: <ChatPage />,
      },
      {
        path: "astrologers",
        element: <AstrologersPage />,
      },
      {
        path: "astrologers/:id",
        element: <AstrologerProfilePage />,
      },
      {
        path: "consultations",
        element: <ConsultationLayout />,
        children: [
          {
            index: true,
            element: <ConsultationsPage />,
          },
          {
            path: "new",
            element: <ConsultationWizardPage />,
          },
          {
            path: "result",
            element: <ConsultationResultPage />,
          },
        ],
      },
      {
        path: "settings",
        element: <SettingsPage />,
        children: [
          {
            index: true,
            element: <Navigate to="account" replace />,
          },
          {
            path: "account",
            element: <AccountSettings />,
          },
          {
            path: "subscription",
            element: <SubscriptionSettings />,
          },
          {
            path: "usage",
            element: <UsageSettings />,
          },
        ],
      },
      {
        path: "help",
        element: (
          <RoleGuard roles={["user", "admin", "ops", "support"]}>
            <HelpPage />
          </RoleGuard>
        ),
      },
      {
        path: "help/subscriptions",
        element: (
          <RoleGuard roles={["user", "admin", "ops", "support"]}>
            <SubscriptionGuidePage />
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
            element: <EnterpriseDashboardPage />,
          },
          {
            path: "credentials",
            element: <EnterpriseCredentialsPanel />,
          },
        ],
      },
      {
        path: "admin",
        element: (
          <AdminGuard>
            <AdminPage />
          </AdminGuard>
        ),
        children: [
          {
            index: true,
            element: <AdminHubPage />,
          },
          {
            path: "dashboard",
            element: <AdminDashboardPage />,
          },
          {
            path: "users",
            element: <AdminUsersPage />,
          },
          {
            path: "users/:userId",
            element: <AdminUserDetailPage />,
          },
          {
            path: "entitlements",
            element: <AdminEntitlementsPage />,
          },
          {
            path: "ai-generations",
            element: <AdminAiGenerationsPage />,
          },
          {
            path: "prompts",
            element: <AdminPromptsPage />,
            children: [
              { index: true, element: <Navigate to="catalog" replace /> },
              { path: "catalog", element: <AdminPromptsRouteSlot /> },
              { path: "release", element: <AdminPromptsRouteSlot /> },
              { path: "consumption", element: <AdminPromptsRouteSlot /> },
              { path: "personas", element: <AdminPromptsRouteSlot /> },
              { path: "sample-payloads", element: <AdminPromptsRouteSlot /> },
              { path: "*", element: <Navigate to="/admin/prompts/catalog" replace /> },
            ],
          },
          {
            path: "content",
            element: <AdminContentPage />,
          },
          {
            path: "billing",
            element: <AdminBillingPage />,
          },
          {
            path: "logs",
            element: <AdminLogsPage />,
          },
          {
            path: "support",
            element: <AdminSupportPage />,
          },
          {
            path: "settings",
            element: <AdminSettingsPage />,
          },
          // Legacy redirects
          {
            path: "pricing",
            element: <Navigate to="/admin/billing" replace />,
          },
          {
            path: "monitoring",
            element: <Navigate to="/admin/logs" replace />,
          },
          {
            path: "personas",
            element: <Navigate to="/admin/prompts/personas" replace />,
          },
          {
            path: "reconciliation",
            element: <ReconciliationAdmin />,
          },
        ],
      },
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]
