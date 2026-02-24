/**
 * Bottom navigation and application navigation configuration (Epic 17+)
 * Source: docs/interfaces/horoscope-ui-spec.md §8, §9
 */

import { 
  CalendarDays, 
  MessageCircle, 
  Star, 
  Layers, 
  User, 
  Shield, 
  FileText, 
  Settings,
  Bell
} from './icons.tsx'
import type { LucideIcon } from 'lucide-react'

export interface NavItem {
  key: string
  label: string
  icon: LucideIcon
  path: string
  roles?: string[]
  showOnMobile?: boolean
}

export const navItems: NavItem[] = [
  // Consumer Base
  { key: 'today', label: 'Aujourd\'hui', icon: CalendarDays, path: '/dashboard', showOnMobile: true },
  { key: 'chat', label: 'Chat', icon: MessageCircle, path: '/chat', showOnMobile: true },
  { key: 'natal', label: 'Thème', icon: Star, path: '/natal', showOnMobile: true },
  { key: 'tirages', label: 'Tirages', icon: Layers, path: '/consultations', showOnMobile: true },
  { key: 'profile', label: 'Profil', icon: User, path: '/settings', showOnMobile: true },
  
  // Public
  { key: 'privacy', label: 'Confidentialité', icon: Shield, path: '/privacy', showOnMobile: false },
  
  // Support / Ops
  { key: 'support', label: 'Support', icon: MessageCircle, path: '/support', roles: ['support', 'ops'], showOnMobile: false },
  
  // Admin / Ops
  { key: 'monitoring', label: 'Monitoring', icon: FileText, path: '/admin/monitoring', roles: ['ops', 'admin'], showOnMobile: false },
  { key: 'persona', label: 'Persona', icon: User, path: '/admin/persona', roles: ['ops', 'admin'], showOnMobile: false },
  { key: 'reconciliation', label: 'Réconciliation', icon: FileText, path: '/admin/reconciliation', roles: ['ops'], showOnMobile: false },
  
  // Enterprise
  { key: 'ent_api', label: 'API', icon: Shield, path: '/enterprise/credentials', roles: ['enterprise_admin'], showOnMobile: false },
  { key: 'ent_astro', label: 'Astrologie', icon: Star, path: '/enterprise/astrology', roles: ['enterprise_admin'], showOnMobile: false },
  { key: 'ent_usage', label: 'Usage', icon: FileText, path: '/enterprise/usage', roles: ['enterprise_admin'], showOnMobile: false },
  { key: 'ent_editorial', label: 'Éditorial', icon: FileText, path: '/enterprise/editorial', roles: ['enterprise_admin'], showOnMobile: false },
  { key: 'ent_billing', label: 'Facturation', icon: FileText, path: '/enterprise/billing', roles: ['enterprise_admin'], showOnMobile: false },
]

export function filterByRole(items: NavItem[], role: string | null): NavItem[] {
  return items.filter((item) => {
    if (!item.roles) return true
    if (!role) return false
    return item.roles.includes(role)
  })
}

export function getMobileNavItems(role: string | null = null): NavItem[] {
  return filterByRole(navItems, role).filter((item) => item.showOnMobile)
}

export function getAllNavItems(role: string | null): NavItem[] {
  return filterByRole(navItems, role)
}
