export type NavItem = {
  path: string
  label: string
  mobileLabel?: string
  roles?: string[]
  showOnMobile?: boolean
}

export const baseNavItems: NavItem[] = [
  { path: "/dashboard", label: "Tableau de bord", mobileLabel: "Accueil", showOnMobile: true },
  { path: "/natal", label: "Thème natal", mobileLabel: "Thème", showOnMobile: true },
  { path: "/chat", label: "Chat", showOnMobile: true },
  { path: "/profile", label: "Données de naissance", mobileLabel: "Naissance", showOnMobile: true },
  { path: "/billing", label: "Abonnement", mobileLabel: "Compte", showOnMobile: true },
  { path: "/privacy", label: "Confidentialité", showOnMobile: false },
]

export const supportNavItems: NavItem[] = [
  { path: "/support", label: "Support", roles: ["support", "ops"], showOnMobile: false },
]

export const opsNavItems: NavItem[] = [
  { path: "/admin/monitoring", label: "Monitoring", roles: ["ops", "admin"], showOnMobile: false },
  { path: "/admin/persona", label: "Persona", roles: ["ops", "admin"], showOnMobile: false },
  { path: "/admin/reconciliation", label: "Réconciliation", roles: ["ops"], showOnMobile: false },
]

export const enterpriseNavItems: NavItem[] = [
  { path: "/enterprise/credentials", label: "API", roles: ["enterprise_admin"], showOnMobile: false },
  { path: "/enterprise/astrology", label: "Astrologie", roles: ["enterprise_admin"], showOnMobile: false },
  { path: "/enterprise/usage", label: "Usage", roles: ["enterprise_admin"], showOnMobile: false },
  { path: "/enterprise/editorial", label: "Éditorial", roles: ["enterprise_admin"], showOnMobile: false },
  { path: "/enterprise/billing", label: "Facturation", roles: ["enterprise_admin"], showOnMobile: false },
]

export function filterByRole(items: NavItem[], role: string | null): NavItem[] {
  return items.filter((item) => {
    if (!item.roles) return true
    if (!role) return false
    return item.roles.includes(role)
  })
}

export function getMobileNavItems(role: string | null = null): NavItem[] {
  const allItems = [
    ...baseNavItems,
    ...filterByRole(supportNavItems, role),
    ...filterByRole(opsNavItems, role),
    ...filterByRole(enterpriseNavItems, role),
  ]
  return allItems.filter((item) => item.showOnMobile)
}

export function getAllNavItems(role: string | null): NavItem[] {
  return [
    ...baseNavItems,
    ...filterByRole(supportNavItems, role),
    ...filterByRole(opsNavItems, role),
    ...filterByRole(enterpriseNavItems, role),
  ]
}
