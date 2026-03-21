import React from 'react'
import {
  Briefcase,
  Users,
  Zap,
  DollarSign,
  Heart,
  Sparkles
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

const DOMAIN_ICON_MAP: Record<string, LucideIcon> = {
  pro_ambition:       Briefcase,
  relations_echanges: Users,
  energie_bienetre:   Zap,
  argent_ressources:  DollarSign,
  vie_personnelle:    Heart,
  work:               Briefcase,
  career:             Briefcase,
  love:               Heart,
  health:             Sparkles,
  energy:             Zap,
  mood:               Sparkles,
  money:              DollarSign,
  social_network:     Users,
  communication:      Users,
  pleasure_creativity:Sparkles,
}

interface DomainIconProps {
  code: string
  size?: number
  className?: string
}

export const DomainIcon: React.FC<DomainIconProps> = ({ code, size = 16, className }) => {
  const Icon = DOMAIN_ICON_MAP[code] ?? Sparkles
  return <Icon size={size} className={className} strokeWidth={2} aria-hidden="true" />
}
