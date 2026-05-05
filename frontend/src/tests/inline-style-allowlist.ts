// Allowlist exacte des styles inline dynamiques conserves par politique frontend.
import { INLINE_STYLE_EXCEPTIONS } from "./design-system-allowlist"

export const INLINE_STYLE_DYNAMIC_ALLOWLIST = [
  "frontend/src/layouts/TwoColumnLayout.tsx::--sidebar-width",
  "frontend/src/components/DomainRankingCard.tsx::width",
  "frontend/src/components/prediction/TimelineRail.tsx::width",
  "frontend/src/components/prediction/TimelineRail.tsx::left",
  "frontend/src/components/prediction/DayTimelineSectionV4.tsx::--period-accent",
  "frontend/src/components/prediction/DayTimelineSectionV4.tsx::backgroundColor",
  "frontend/src/components/prediction/CategoryGrid.tsx::color",
  "frontend/src/components/prediction/DayPredictionCard.tsx::backgroundColor",
  "frontend/src/components/TurningPointCard.tsx::badge-color",
  "frontend/src/components/ui/Badge/Badge.tsx::background",
  "frontend/src/components/ui/Skeleton/Skeleton.tsx::style-prop",
  "frontend/src/components/ui/Skeleton/Skeleton.tsx::--skeleton-gap",
  "frontend/src/features/chat/components/AstrologerPickerModal.tsx::display",
] as const

export { INLINE_STYLE_EXCEPTIONS }
