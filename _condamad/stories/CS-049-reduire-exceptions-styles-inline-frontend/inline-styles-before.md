<!-- Classification before des styles inline CS-049. -->

# CS-049 Inline Styles Before

| Item | Type | Classification | Decision |
|---|---|---|---|
| `AstrologerPickerModal.tsx::display` | avatar fallback | removable-static-style | delete via `hidden` |
| `TwoColumnLayout.tsx::--sidebar-width` | layout runtime | dynamic-bridge | keep |
| `DomainRankingCard.tsx::width` | score runtime | dynamic-bridge | keep |
| `TimelineRail.tsx::width/left` | position runtime | dynamic-bridge | keep |
| `DayTimelineSectionV4.tsx::--period-accent/backgroundColor` | accent runtime | dynamic-bridge | keep |
| `CategoryGrid.tsx::color` | band color runtime | dynamic-bridge | keep |
| `DayPredictionCard.tsx::backgroundColor` | tone runtime | dynamic-bridge | keep |
| `TurningPointCard.tsx::badge-color` | badge runtime | dynamic-bridge | keep |
| `Badge.tsx::background` | style prop component | component-style-prop-pass-through | keep |
| `Skeleton.tsx::style/style-prop` | layout prop | component-style-prop-pass-through | keep |

