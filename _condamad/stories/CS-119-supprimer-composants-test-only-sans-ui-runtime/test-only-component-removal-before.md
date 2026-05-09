<!-- Inventaire avant suppression CS-119 des composants frontend test-only. -->

# CS-119 Test-only Component Removal - Before

## Component File Inventory

Inventaire frais execute avant suppression avec:

```powershell
rg --files frontend/src/components -g "*.tsx" -g "*.ts"
```

Fichiers presents sous `frontend/src/components` avant implementation:

```text
AdminGuard.tsx
AstroDailyEvents.tsx
AstroFoundationSection.tsx
B2BAstrologyPanel.tsx
B2BBillingPanel.tsx
B2BEditorialPanel.tsx
B2BReconciliationPanel.tsx
B2BUsagePanel.tsx
BestWindowCard.tsx
ConstellationSVG.tsx
DailyInsightsSection.tsx
DayClimateHero.tsx
DomainRankingCard.tsx
ErrorBoundary/ErrorBoundary.css
ErrorBoundary/ErrorBoundary.tsx
ErrorBoundary/PageErrorBoundary.tsx
ErrorBoundary/SectionErrorBoundary.tsx
ErrorBoundary/index.ts
EnterpriseCredentialsPanel.tsx
HeroHoroscopeCard.tsx
MiniInsightCard.tsx
NatalChartGuide.tsx
OpsMonitoringPanel.tsx
OpsPersonaPanel.tsx
PrivacyPanel.tsx
ShortcutCard.tsx
ShortcutsSection.tsx
StarfieldBackground.tsx
SupportOpsPanel.tsx
TimezoneSelect.tsx
TodayHeader.tsx
TurningPointCard.tsx
astro/AstroMoodBackground.tsx
astro/astroMoodBackgroundUtils.ts
astro/zodiacPatterns.ts
dashboard/DashboardCard.tsx
dashboard/DashboardHoroscopeSummaryCard.tsx
dashboard/DashboardHoroscopeSummaryCardContainer.tsx
dashboard/index.ts
dashboard/useDashboardAstroSummary.ts
icons/DashboardIcons.tsx
icons/index.ts
icons/zodiac/AquariusIcon.tsx
icons/zodiac/AriesIcon.tsx
icons/zodiac/CancerIcon.tsx
icons/zodiac/CapricornIcon.tsx
icons/zodiac/GeminiIcon.tsx
icons/zodiac/LeoIcon.tsx
icons/zodiac/LibraIcon.tsx
icons/zodiac/PiscesIcon.tsx
icons/zodiac/SagittariusIcon.tsx
icons/zodiac/ScorpioIcon.tsx
icons/zodiac/TaurusIcon.tsx
icons/zodiac/VirgoIcon.tsx
icons/zodiac/index.ts
layout/BottomNav.tsx
layout/EnterpriseLayout.tsx
layout/Header.tsx
layout/Sidebar.tsx
layout/index.ts
natal-interpretation/NatalInterpretationContent.tsx
natal-interpretation/NatalInterpretationEvidence.tsx
natal-interpretation/NatalInterpretationMenus.tsx
natal-interpretation/NatalInterpretationTypes.ts
prediction/DailyAdviceCard.tsx
prediction/DailyPageHeader.tsx
prediction/DayPredictionCard.tsx
prediction/DayStateBadge.tsx
prediction/DayTimelineSectionV4.tsx
prediction/DomainIcon.tsx
prediction/TurningPointsList.tsx
settings/DeleteAccountModal.tsx
settings/SettingsTabs.tsx
settings/SubscriptionPlanGrid.tsx
ui/Badge/Badge.test.tsx
ui/Badge/Badge.tsx
ui/Badge/index.ts
ui/Button/Button.test.tsx
ui/Button/Button.tsx
ui/Button/index.ts
ui/Card/Card.test.tsx
ui/Card/Card.tsx
ui/Card/index.ts
ui/EmptyState/EmptyState.test.tsx
ui/EmptyState/EmptyState.tsx
ui/EmptyState/index.ts
ui/ErrorState/ErrorState.tsx
ui/ErrorState/index.ts
ui/Field/Field.test.tsx
ui/Field/Field.tsx
ui/Field/index.ts
ui/Form/Form.test.tsx
ui/Form/Form.tsx
ui/Form/FormField.tsx
ui/Form/index.ts
ui/LockedSection/LockedSection.test.tsx
ui/LockedSection/LockedSection.tsx
ui/LockedSection/index.ts
ui/Modal/Modal.test.tsx
ui/Modal/Modal.tsx
ui/Modal/index.ts
ui/Select/Select.test.tsx
ui/Select/Select.tsx
ui/Select/index.ts
ui/Skeleton/Skeleton.test.tsx
ui/Skeleton/Skeleton.tsx
ui/Skeleton/index.ts
ui/UpgradeCTA/UpgradeCTA.test.tsx
ui/UpgradeCTA/UpgradeCTA.tsx
ui/UpgradeCTA/index.ts
ui/UserAvatar/UserAvatar.tsx
ui/UserAvatar/index.ts
ui/UserMenu/UserMenu.tsx
ui/UserMenu/index.ts
ui/index.ts
zodiacSignIconMap.tsx
```

## Removal Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `components/B2BAstrologyPanel.tsx` | component | dead | focused test, usage/API allowlists | none | delete | no runtime import; exact test-only allowlist row | low |
| `components/B2BBillingPanel.tsx` | component | dead | focused test, usage/API allowlists | none | delete | no runtime import; exact test-only allowlist row | low |
| `components/B2BEditorialPanel.tsx` | component | dead | focused test, usage/API allowlists | none | delete | no runtime import; exact test-only allowlist row | low |
| `components/B2BUsagePanel.tsx` | component | dead | focused test, usage/API allowlists | none | delete | no runtime import; exact test-only allowlist row | low |
| `components/OpsMonitoringPanel.tsx` | component | dead | focused test, usage/API allowlists | none | delete | no runtime import; exact test-only allowlist row | low |
| `components/OpsPersonaPanel.tsx` | component | dead | focused test, usage/API allowlists | none | delete | no runtime import; exact test-only allowlist row | low |
| `components/PrivacyPanel.tsx` | component | dead | focused test, usage/API allowlists | none | delete | no runtime import; exact test-only allowlist row | low |
| `components/DailyInsightsSection.tsx` | component | dead | `MiniInsightCard.test.tsx`, usage allowlist, design guard | none | delete | no runtime import; only test/guard consumers | low |
| `components/MiniInsightCard.tsx` | component | dead | focused test, `visual-smoke`, type-only hook import, usage allowlist | internal type only | delete | hook import is type-only and can be localized | low |
| `components/MiniInsightCard.css` | CSS | dead | `MiniInsightCard.tsx`, focused test | none | delete | dedicated CSS for deleted component | low |
| `components/ConstellationSVG.tsx` | component | dead | `HeroHoroscopeCard.tsx`, usage allowlist | none | delete | only reachable through deleted test-only owner | low |
| `components/HeroHoroscopeCard.tsx` | component | dead | focused test, visual/design guards, usage allowlist | none | delete | no runtime import; only test/guard consumers | low |
| `components/HeroHoroscopeCard.css` | CSS | dead | `HeroHoroscopeCard.tsx`, focused test, visual/design guards | none | delete | dedicated CSS for deleted component | low |
| `components/TodayHeader.tsx` | component | dead | focused test, usage allowlist | none | delete | no runtime import; exact test-only allowlist row | low |
| `components/prediction/DayPredictionCard.tsx` | component | dead | tone test, usage allowlist, design guard | none | delete | direct test-only helper owner only | low |
| `components/prediction/DayPredictionCard.css` | CSS | dead | `DayPredictionCard.tsx`, design guard | none | delete | dedicated CSS for deleted component | low |
| `components/prediction/TurningPointsList.tsx` | component | dead | focused enriched test, usage allowlist, design guard | none | delete | direct test-only consumer only | low |
| `components/prediction/TurningPointsList.css` | CSS | dead | `TurningPointsList.tsx`, design guard | none | delete | dedicated CSS for deleted component | low |
| `components/ErrorBoundary/ErrorBoundary.tsx` | component | canonical-active | `features/natal-chart/NatalInterpretation.tsx`, `PageErrorBoundary`, `SectionErrorBoundary` | keep current owner | keep | runtime imports through feature/page error boundaries | none |
| `components/ErrorBoundary/PageErrorBoundary.tsx` | component | canonical-active | `layouts/AppLayout.tsx` | keep current owner | keep | runtime import from app layout | none |
| `components/ErrorBoundary/SectionErrorBoundary.tsx` | component | canonical-active | `DashboardPage`, `ChatPage`, `DailyHoroscopePage` | keep current owner | keep | runtime imports from pages | none |
| `components/ErrorBoundary/index.ts` | barrel | canonical-active | `@components/ErrorBoundary` and relative imports | keep current owner | keep | barrel exports runtime error-boundary owner | none |
| `components/ErrorBoundary/ErrorBoundary.css` | CSS | canonical-active | `ErrorBoundary.tsx`, `PageErrorBoundary.tsx`, design guard | keep current owner | keep | dedicated CSS for runtime-used ErrorBoundary family | none |

## Keep Decisions

Les surfaces explicitement hors suppression restent presentes:

- `B2BReconciliationPanel.tsx`, `EnterpriseCredentialsPanel.tsx`,
  `SupportOpsPanel.tsx`, `settings/DeleteAccountModal.tsx`: `used`.
- `dashboard/DashboardCard.tsx`, `icons/DashboardIcons.tsx`,
  `ui/Card/Card.tsx`, `ui/Form/FormField.tsx`: `public-library-export`.
- `ErrorBoundary/**`: `canonical-active`, consomme par layouts/pages/features
  runtime.
- `natal-interpretation/**`: hors scope CS-119.

## Before Scan Summary

- B2B/ops/privacy: hits limites aux composants, tests dedies et allowlists.
- Daily/dashboard visuals: hits limites aux composants, tests dedies,
  `visual-smoke`, `design-system`, allowlist et import type-only
  `useDailyInsights`.
- Prediction: hits limites aux composants, CSS dedies, tests dedies,
  `design-system` et allowlist.
- CSS dedies: seuls les composants supprimes et tests/guards les lisent.

Conclusion before: aucun target CS-119 n'a de consommateur runtime non-test ou
de barrel public; les candidats sont supprimables dans cette story.
