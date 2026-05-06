# CS-061 - Inline styles before

Baseline capture avant migration.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `TwoColumnLayout.tsx --sidebar-width` | CSS custom-property bridge | canonical-active | layout grid | custom property | keep | allowlist | runtime width |
| `DomainRankingCard.tsx width` | runtime geometry | canonical-active | score progress | dynamic width | keep | allowlist | score arbitrary |
| `DayTimelineSectionV4.tsx --period-accent` | color bridge | canonical-active | period accent | custom property | keep | allowlist | dynamic color |
| `TimelineRail.tsx width/left` | fixed geometry | dead | selected period rail | deterministic CSS classes | delete | finite period map | faible |
| `Badge.tsx background` | color bridge | canonical-active | public color prop | component API | keep | allowlist | public API/tests |
| `Skeleton.tsx style` | style-prop-pass-through | canonical-active | public pass-through | component API | keep | allowlist | public API |
| `Skeleton.tsx groupStyle` | CSS custom-property bridge | canonical-active | gap runtime | custom property | keep | allowlist | dynamic gap |

Count before: 9 inline style attributes.
