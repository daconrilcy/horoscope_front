import { Suspense, lazy } from "react"
import type { RouteObject } from "react-router-dom"
import { Navigate, useNavigate, useSearchParams } from "react-router-dom"

import { AppShell } from "../components/AppShell"
import { AuthGuard } from "./guards/AuthGuard"
import { RoleGuard } from "./guards/RoleGuard"
import { AdminGuard } from "../components/AdminGuard"
import { AppLayout } from "../layouts/AppLayout"
import { PageErrorBoundary } from "../components/PageErrorBoundary"

// Pages
import { DashboardPage } from "../pages/DashboardPage"
import { TodayPage } from "../pages/TodayPage"
import { NatalChartPage } from "../pages/NatalChartPage"
import { ChatPage } from "../pages/ChatPage"
import { SettingsPage } from "../pages/SettingsPage"
import { LoginPage } from "../pages/LoginPage"
import { RegisterPage } from "../pages/RegisterPage"
import { NotFoundPage } from "../pages/NotFoundPage"
import { ConsultationsPage } from "../pages/ConsultationsPage"
import { ConsultationWizardPage } from "../pages/ConsultationWizardPage"
import { SupportPage } from "../pages/SupportPage"
import { EnterpriseDashboardPage } from "../pages/EnterpriseDashboardPage"
import { AdminPage } from "../pages/AdminPage"

import {
  PricingAdmin,
  MonitoringAdmin,
  PersonasAdmin,
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

export const routes: RouteObject[] = [
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
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: "dashboard",
        element: <DashboardPage />,
      },
      {
        path: "today",
        element: <TodayPage />,
      },
      {
        path: "natal",
        element: <NatalChartPage />,
      },
      {
        path: "chat",
        element: <ChatPage />,
      },
      {
        path: "consultations",
        children: [
          {
            index: true,
            element: <ConsultationsPage />,
          },
          {
            path: "new",
            element: <ConsultationWizardPage />,
          },
        ],
      },
      {
        path: "settings",
        element: <SettingsPage />,
      },
      {
        path: "support",
        element: (
          <RoleGuard roles={["user", "admin", "ops", "support"]}>
            <SupportPage />
          </RoleGuard>
        ),
      },
      {
        path: "enterprise",
        element: (
          <RoleGuard roles={["enterprise_admin", "admin"]}>
            <EnterpriseDashboardPage />
          </RoleGuard>
        ),
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
            element: <Navigate to="../billing" replace />,
          },
          {
            path: "monitoring",
            element: <Navigate to="../logs" replace />,
          },
          {
            path: "personas",
            element: <Navigate to="../prompts" replace />,
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
