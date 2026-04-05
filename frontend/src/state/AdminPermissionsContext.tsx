import { createContext, useContext, useMemo } from "react"
import type { ReactNode } from "react"

export interface AdminPermissionsContextValue {
  allowedSections: string[]
  canEdit: (domain: string) => boolean
  canExport: boolean
}

const AdminPermissionsContext = createContext<AdminPermissionsContextValue | undefined>(undefined)

export const ADMIN_SECTIONS = [
  "dashboard",
  "users",
  "entitlements",
  "ai-generations",
  "prompts",
  "content",
  "billing",
  "logs",
  "support",
  "settings",
]

export function AdminPermissionsProvider({ children }: { children: ReactNode }) {
  // In this epic, we hardcode all permissions for the admin role
  // Future epics will derive this from user.role or user.permissions
  const value = useMemo(() => ({
    allowedSections: ADMIN_SECTIONS,
    canEdit: (_domain: string) => true,
    canExport: true,
  }), [])

  return (
    <AdminPermissionsContext.Provider value={value}>
      {children}
    </AdminPermissionsContext.Provider>
  )
}

export function useAdminPermissions(): AdminPermissionsContextValue {
  const context = useContext(AdminPermissionsContext)
  if (context === undefined) {
    throw new Error("useAdminPermissions must be used within AdminPermissionsProvider")
  }
  return context
}
