/**
 * Bottom navigation configuration for the horoscope app
 * Source: docs/interfaces/horoscope-ui-spec.md §8, §9
 */

import { CalendarDays, MessageCircle, Star, Layers, User } from './icons'
import type { LucideIcon } from './icons'

export interface NavItem {
  key: string
  label: string
  icon: LucideIcon
  path: string
}

export const navItems: NavItem[] = [
  { key: 'today', label: 'Aujourd\'hui', icon: CalendarDays, path: '/dashboard' },
  { key: 'chat', label: 'Chat', icon: MessageCircle, path: '/chat' },
  { key: 'natal', label: 'Thème', icon: Star, path: '/natal' },
  { key: 'tirages', label: 'Tirages', icon: Layers, path: '/consultations' },
  { key: 'profile', label: 'Profil', icon: User, path: '/settings/account' },
]
