import React from 'react'
import {
  Heart,
  Briefcase,
  Rocket,
  Zap,
  Brain,
  Leaf,
  DollarSign,
  Landmark,
  Flame,
  Home,
  Users,
  MessageCircle,
  Palette,
  Sparkles,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

const CATEGORY_ICON_MAP: Record<string, LucideIcon> = {
  love:                Heart,
  work:                Briefcase,
  career:              Rocket,
  energy:              Zap,
  mood:                Brain,
  health:              Leaf,
  money:               DollarSign,
  finances:            Landmark,
  sex_intimacy:        Flame,
  family_home:         Home,
  social_network:      Users,
  communication:       MessageCircle,
  pleasure_creativity: Palette,
}

interface CategoryIconProps {
  code: string
  size?: number
  className?: string
}

export const CategoryIcon: React.FC<CategoryIconProps> = ({ code, size = 13, className }) => {
  const Icon = CATEGORY_ICON_MAP[code] ?? Sparkles
  return <Icon size={size} className={className} strokeWidth={1.8} aria-hidden="true" />
}
