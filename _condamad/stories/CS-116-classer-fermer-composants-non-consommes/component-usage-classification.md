<!-- Classification CS-116 des composants F-005. -->

# CS-116 Component Usage Classification

| Item | Classification | Decision | Proof | Risk |
|---|---|---|---|---|
| B2B panels | test-only | keep | imports only from focused tests and architecture registers | none in story scope |
| Ops panels | test-only | keep | imports only from focused tests and architecture registers | none in story scope |
| PrivacyPanel | test-only | keep | imports only from focused tests and architecture registers | none in story scope |
| Daily visual components | test-only | keep | imports only from focused tests and design/visual guards | none in story scope |
| Prediction no-public-export components | remove | delete | no runtime reachability and no public barrel export | none |
| Prediction test-covered components | test-only | keep | direct focused tests only | none in story scope |
| `ConstellationSVG.tsx` | test-only | keep | reachable only through test-only `HeroHoroscopeCard` | none in story scope |
| `MiniInsightCard.tsx` | test-only | keep | reachable only through test-only `DailyInsightsSection`; `useDailyInsights` import is type-only | none in story scope |
| `AppShell.tsx` | remove | delete | pure alias re-export with zero runtime import | none |
| `dashboard/DashboardCard.tsx` | public-library-export | keep | barrel-only dashboard export detected by import-aware guard | none in story scope |
| `ui/Card/Card.tsx` | public-library-export | keep | barrel-only UI primitive detected by import-aware guard | none in story scope |
| `ui/Form/FormField.tsx` | public-library-export | keep | public barrel + tests | none |
| `icons/DashboardIcons.tsx` | public-library-export | keep | named export review + `components/icons/index.ts` public surface | none in story scope |
| `prediction/CategoryGrid.tsx` | remove | delete | no runtime reachability, no direct test, no public barrel export | none |
| `prediction/CategoryIcon.tsx` | remove | delete | no runtime reachability, no direct test, no public barrel export | none |
| `prediction/DayAgenda.tsx` | remove | delete | reachable only through deleted no-runtime `DayTimelineSection` chain | none |
| `prediction/DayPredictionCardContainer.tsx` | remove | delete | no runtime reachability, no direct test, no public barrel export | none |
| `prediction/DayPredictionCard.tsx` | test-only | keep | direct `day-prediction-card-tone.test.ts` import for `getDayPredictionToneClassKey` | none |
| `prediction/DayTimeline.tsx` | remove | delete | no runtime reachability, no direct test, no public barrel export | none |
| `prediction/DayTimelineSection.tsx` | remove | delete | no runtime reachability, no direct test, no public barrel export | none |
| `prediction/DecisionWindowsSection.tsx` | remove | delete | no runtime reachability, no direct test, no public barrel export | none |
| `prediction/PeriodCard.tsx` | remove | delete | reachable only through deleted no-runtime `PeriodCardsRow` chain | none |
| `prediction/PeriodCardsRow.tsx` | remove | delete | reachable only through deleted no-runtime `DayTimelineSection` chain | none |
| `prediction/SectionTitle.tsx` | remove | delete | reachable only through deleted no-runtime `DayTimelineSection` chain | none |
| `prediction/TimelineRail.tsx` | remove | delete | reachable only through deleted no-runtime `DayTimelineSection` chain | none |
| `prediction/TurningPointsList.tsx` | test-only | keep | direct `TurningPointsEnriched.test.tsx` imports only | none |

All files classified `remove` were physically deleted with stale CSS where applicable.
