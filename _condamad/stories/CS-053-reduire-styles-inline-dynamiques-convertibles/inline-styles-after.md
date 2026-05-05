<!-- Classification finale des styles inline TSX pour CS-053. -->

# Inline Styles After

After command from `frontend`:

```powershell
rg -n "style=\{" src -g "*.tsx"
```

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `layouts/TwoColumnLayout.tsx` `--sidebar-width` | CSS custom property | `css-custom-property-bridge` | `TwoColumnLayout` | Keep inline bridge consumed by `TwoColumnLayout.css` | keep | Public prop `sidebarWidth` supplies runtime layout width. | Replacing with static CSS would change public layout control. |
| `components/DomainRankingCard.tsx` `width` | width | `runtime-geometry` | `DomainRankingCard` | Keep exact inline progress width | keep | Width is derived from `domain.score_10`. | CSS approximation would desync displayed score and bar. |
| `components/prediction/CategoryGrid.tsx` `color` | color | `color-bridge` | category score | Keep runtime band color | keep | Color comes from `getNoteBand(cat.note_20, lang)`. | Static class mapping remains outside this story. |
| `components/prediction/CategoryGrid.tsx` `color` | color | `color-bridge` | category band label | Keep runtime band color | keep | Same runtime band color as score. | Static class mapping remains outside this story. |
| `components/prediction/DayPredictionCard.tsx` `backgroundColor` | color | `color-bridge` | tone badge | Keep runtime color when no astro background is used | keep | Color comes from `getToneColor(summary.overall_tone)`. | Static class mapping remains outside this story. |
| `components/prediction/DayTimelineSectionV4.tsx` `--period-accent` | CSS custom property | `css-custom-property-bridge` | timeline card accent | Keep narrowed bridge | keep | Card publishes period accent for CSS consumption. | Removing bridge would lose period-specific accents. |
| `components/prediction/DayTimelineSectionV4.css` `.day-timeline-v4__dot` | CSS declaration | `removable-static-style` migrated | timeline dot | `.day-timeline-v4__dot { background-color: var(--period-accent); }` | deleted from TSX | Dot now consumes the existing card custom property. | Low; same runtime value flows through CSS variable. |
| `components/prediction/TimelineRail.tsx` `width` | width | `runtime-geometry` | rail fill | Keep exact inline geometry | keep | Width is computed from selected period percentage. | Static CSS cannot represent arbitrary selected state without changing implementation. |
| `components/prediction/TimelineRail.tsx` `left` | position | `runtime-geometry` | rail ticks | Keep exact inline geometry | keep | Tick positions are data-driven percentages. | Static CSS migration would require separate classes and broader test coverage. |
| `components/prediction/TimelineRail.tsx` `left` | position | `runtime-geometry` | rail thumb | Keep exact inline geometry | keep | Thumb position is computed from selected period. | Static CSS cannot preserve geometry without a mapping refactor. |
| `components/TurningPointCard.tsx` `background` | color | `color-bridge` | turning point rail | Keep runtime badge color | keep | Color depends on `turningPoint.change_type`. | Static class migration would require change-type class mapping. |
| `components/TurningPointCard.tsx` `color` + `background` | color | `color-bridge` | turning point type badge | Keep runtime badge colors | keep | Colors depend on `turningPoint.change_type`. | Static class migration would require change-type class mapping. |
| `components/ui/Badge/Badge.tsx` `background` | color | `color-bridge` | `Badge` primitive | Keep public color prop bridge | keep | `color` is a public prop used by callers. | Removing it would break component API. |
| `components/ui/Skeleton/Skeleton.tsx` `style` | style object | `style-prop-pass-through` | `Skeleton` primitive | Keep width/height prop style | keep | Public `width` and `height` props map to runtime dimensions. | Removing it would break skeleton sizing API. |
| `components/ui/Skeleton/Skeleton.tsx` `--skeleton-gap` | CSS custom property | `css-custom-property-bridge` | `SkeletonGroup` | Keep inline bridge consumed by `Skeleton.css` | keep | Public `gap` prop controls group spacing. | Removing it would break group spacing API. |

Net result: 1 convertible inline declaration removed from TSX; 14 runtime or API-backed inline styles remain allowlisted exactly.
