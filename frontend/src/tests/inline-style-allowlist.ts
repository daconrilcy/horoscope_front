// Allowlist exacte des styles inline dynamiques conserves par politique frontend.
import { INLINE_STYLE_EXCEPTIONS } from "./design-system-allowlist"

export const INLINE_STYLE_DYNAMIC_ALLOWLIST = [
  "frontend/src/components/DomainRankingCard.tsx::width",
  "frontend/src/components/prediction/DayTimelineSectionV4.tsx::--period-accent",
  "frontend/src/components/ui/Skeleton/Skeleton.tsx::style-prop",
  "frontend/src/components/ui/Skeleton/Skeleton.tsx::--skeleton-gap",
] as const

export { INLINE_STYLE_EXCEPTIONS }
