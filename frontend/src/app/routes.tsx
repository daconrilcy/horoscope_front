import type { RouteObject } from "react-router-dom"
import { Navigate, useNavigate, useSearchParams } from "react-router-dom"

import { AppShell } from "../components/AppShell"
import { RootLayout, AuthLayout, LandingLayout } from "../layouts"
import { EnterpriseLayout } from "../components/layout"
import { AuthGuard } from "./guards/AuthGuard"
import { RoleGuard } from "./guards/RoleGuard"
import { RootRedirect } from "./guards/RootRedirect"
import { LandingRedirect } from "./guards/LandingRedirect"

import { SignInForm } from "../components/SignInForm"
import { SignUpForm } from "../components/SignUpForm"
import { NatalChartPage } from "../pages/NatalChartPage"
import { ChatPage } from "../pages/ChatPage"
import { BirthProfilePage } from "../pages/BirthProfilePage"
import { NotFoundPage } from "../pages/NotFoundPage"
import DailyHoroscopePage from "../pages/DailyHoroscopePage"
import HelpPage from "../pages/HelpPage"
import { SubscriptionGuidePage } from "../pages/SubscriptionGuidePage"

import { DashboardPage } from "../pages/DashboardPage"
import { PrivacyPolicyPage } from "../pages/PrivacyPolicyPage"
import { ConsultationsPage } from "../pages/ConsultationsPage"
import { ConsultationWizardPage } from "../pages/ConsultationWizardPage"
import { ConsultationResultPage } from "../pages/ConsultationResultPage"
import { AstrologersPage } from "../pages/AstrologersPage"
import { AstrologerProfilePage } from "../pages/AstrologerProfilePage"
import { SettingsPage } from "../pages/SettingsPage"
import { AccountSettings } from "../pages/settings/AccountSettings"
import { SubscriptionSettings } from "../pages/settings/SubscriptionSettings"
import { UsageSettings } from "../pages/settings/UsageSettings"
import { ConsultationLayout } from "../features/consultations"
import { BillingSuccessPage } from "../pages/billing/BillingSuccessPage"
import { BillingCancelPage } from "../pages/billing/BillingCancelPage"
import { PrivacyPanel } from "../components/PrivacyPanel"
import { SupportOpsPanel } from "../components/SupportOpsPanel"
import { AdminPage } from "../pages/AdminPage"
import { PricingAdmin, MonitoringAdmin, PersonasAdmin, ReconciliationAdmin } from "../pages/admin"
import { EnterpriseCredentialsPanel } from "../components/EnterpriseCredentialsPanel"
import { B2BAstrologyPanel } from "../components/B2BAstrologyPanel"
import { B2BUsagePanel } from "../components/B2BUsagePanel"
import { B2BEditorialPanel } from "../components/B2BEditorialPanel"
import { B2BBillingPanel } from "../components/B2BBillingPanel"

function LoginPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const returnTo = searchParams.get("returnTo")
  const registerUrl = returnTo ? `/register?returnTo=${encodeURIComponent(returnTo)}` : "/register"
  return <SignInForm onRegister={() => navigate(registerUrl)} />
}

function RegisterPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const returnTo = searchParams.get("returnTo")
  const loginUrl = returnTo ? `/login?returnTo=${encodeURIComponent(returnTo)}` : "/login"
  return <SignUpForm onSignIn={() => navigate(loginUrl)} />
}


export const routes: RouteObject[] = [
  {
    element: <RootLayout />,
    children: [
      {
        element: <LandingLayout />,
        children: [
          {
            path: "/",
            element: <LandingRedirect />,
          },
          {
            path: "/landing",
            element: <Navigate to="/" replace />,
          },
          {
            path: "/privacy",
            element: <PrivacyPolicyPage />,
          },
        ],
      },
      {
        element: <AuthLayout />,
        children: [
          {
            path: "/login",
            element: <LoginPage />,
          },
          {
            path: "/register",
            element: <RegisterPage />,
          },
        ],
      },
      {
        element: (
          <AuthGuard>
            <AppShell />
          </AuthGuard>
        ),
        children: [
      {
        path: "/dashboard",
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
        path: "/natal",
        element: <NatalChartPage />,
      },
      {
        path: "/chat",
        element: <ChatPage />,
      },
      {
        path: "/chat/:conversationId",
        element: <ChatPage />,
      },
      {
        path: "/profile",
        element: <BirthProfilePage />,
      },
      {
        path: "/billing/success",
        element: <BillingSuccessPage />,
      },
      {
        path: "/billing/cancel",
        element: <BillingCancelPage />,
      },
      {
        path: "/privacy-settings",
        element: <PrivacyPanel />,
      },
      {
        path: "/help",
        element: <HelpPage />,
      },
      {
        path: "/help/subscriptions",
        element: <SubscriptionGuidePage />,
      },
      {
        path: "/consultations",
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
        path: "/astrologers",
        element: <AstrologersPage />,
      },
      {
        path: "/astrologers/:id",
        element: <AstrologerProfilePage />,
      },
      {
        path: "/settings",
        element: <SettingsPage />,
        children: [
          { index: true, element: <Navigate to="account" replace /> },
          { path: "account", element: <AccountSettings /> },
          { path: "subscription", element: <SubscriptionSettings /> },
          { path: "usage", element: <UsageSettings /> },
        ],
      },
      {
        path: "/support",
        element: (
          <RoleGuard roles={["support", "ops"]}>
            <SupportOpsPanel />
          </RoleGuard>
        ),
      },
      {
        path: "/admin",
        element: (
          <RoleGuard roles={["ops", "admin"]}>
            <AdminPage />
          </RoleGuard>
        ),
        children: [
          {
            path: "pricing",
            element: <PricingAdmin />,
          },
          {
            path: "monitoring",
            element: <MonitoringAdmin />,
          },
          {
            path: "personas",
            element: <PersonasAdmin />,
          },
          {
            path: "reconciliation",
            element: <ReconciliationAdmin />,
          },
        ],
      },
      {
        path: "/enterprise/*",
        element: (
          <RoleGuard roles={["enterprise_admin"]}>
            <EnterpriseLayout />
          </RoleGuard>
        ),
        children: [
          {
            index: true,
            element: <Navigate to="/enterprise/credentials" replace />,
          },
          {
            path: "credentials",
            element: <EnterpriseCredentialsPanel />,
          },
          {
            path: "astrology",
            element: <B2BAstrologyPanel />,
          },
          {
            path: "usage",
            element: <B2BUsagePanel />,
          },
          {
            path: "editorial",
            element: <B2BEditorialPanel />,
          },
          {
            path: "billing",
            element: <B2BBillingPanel />,
          },
        ],
      },
      {
        path: "*",
        element: <NotFoundPage />,
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

