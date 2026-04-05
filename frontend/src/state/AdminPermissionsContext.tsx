import { createContext, useContext, useMemo } from "react"
import type { ReactNode } from "react"

/**
 * Infrastructure de permissions pour l'espace Admin.
 * 
 * Cette architecture est conçue pour supporter une transition fluide d'un rôle
 * unique "admin" (Epic 65) vers des profils granulaires (Epic 66+) :
 * - admin_business : focus KPIs, billing, exports
 * - admin_support  : focus users, tickets, modération
 * - admin_ops      : focus prompts, configurations, logs
 * - super_admin    : tous les droits
 */

export interface AdminPermissions {
  /** Liste des codes de sections autorisées dans le menu latéral */
  allowedSections: string[]
  /** Vérifie si l'utilisateur peut modifier un domaine spécifique */
  canEdit: (domain: "entitlements" | "prompts" | "content" | "users" | "billing" | "settings") => boolean
  /** Vérifie si l'utilisateur peut effectuer des exports de données sensibles */
  canExport: boolean
}

export interface AdminPermissionsContextValue extends AdminPermissions {}

const AdminPermissionsContext = createContext<AdminPermissionsContextValue | undefined>(undefined)

export const ALL_ADMIN_SECTIONS = [
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

interface AdminPermissionsProviderProps {
  children: ReactNode
  /** Permet d'injecter des permissions spécifiques pour les tests ou simulations */
  overrides?: Partial<AdminPermissions>
}

export function AdminPermissionsProvider({ children, overrides }: AdminPermissionsProviderProps) {
  // Dans l'Epic 65, tout utilisateur ayant le rôle "admin" a tous les droits.
  // Dans un futur epic, ces valeurs seront calculées à partir de user.role et user.permissions
  // reçues depuis le backend via useAuthMe.
  
  const value = useMemo(() => {
    const basePermissions: AdminPermissions = {
      allowedSections: ALL_ADMIN_SECTIONS,
      canEdit: () => true,
      canExport: true,
    }

    if (overrides) {
      return { ...basePermissions, ...overrides }
    }

    return basePermissions
  }, [overrides])

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
