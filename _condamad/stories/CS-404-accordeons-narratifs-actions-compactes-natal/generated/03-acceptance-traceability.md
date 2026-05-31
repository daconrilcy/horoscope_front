# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `NatalNarrativeReading` owns five chapter accordions. | `NatalNarrativeReading.tsx` maps ordered `reading.chapters`; `natalNarrativeReading.test.tsx` asserts five accordion toggles. | `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard NatalChartPage` PASS. | PASS |
| AC2 | The first chapter starts open. | Local `expandedKeys` initializes from first ordered chapter. | `natalNarrativeReading` PASS asserts first `aria-expanded=true` and second `false`. | PASS |
| AC3 | Chapter buttons expose ARIA linkage. | Buttons set `aria-expanded`, `aria-controls`; panels set `aria-labelledby`. | `natalNarrativeReading` PASS asserts linkage to the controlled panel. | PASS |
| AC4 | Each chapter toggles by keyboard. | Native `<button type="button">` handles keyboard activation. | `natalNarrativeReading` PASS asserts Enter and Space toggles. | PASS |
| AC5 | Collapsed chapters show a short unique preview. | `chapterPreview` derives preview; preview renders only when collapsed. | `natalNarrativeReading` PASS asserts preview on collapsed chapter and no first-chapter body duplication in its open toggle. | PASS |
| AC6 | Sources remain collapsed after narrative chapters. | `InterpretationContent` renders `NatalReadingSources` after `NatalNarrativeReading`. | `natalPublicDomGuard` and `natalNarrativeReading` PASS assert sources button collapsed by default. | PASS |
| AC7 | Astrologer mode remains collapsed by default. | `NatalChartPage` keeps `NatalAstrologerMode` after public interpretation surface. | `NatalChartPage` PASS within targeted suite. | PASS |
| AC8 | Secondary actions use the compact surface. | `NatalInterpretation.tsx` keeps `ni-actions ni-actions--compact`; CSS owns compact rules. | Targeted `rg` positive scan PASS for `ni-actions--compact`; `NatalChartPage` PASS. | PASS |
| AC9 | Public DOM hides technical markers. | Modern narrative branch avoids legacy markers and raw evidence IDs. | `natalPublicDomGuard` PASS; forbidden `rg` scans for `ni-evidence-tags`, `ni-projections`, `LockedSection`, `NatalInterpretationLegacyBody`, `style=` PASS with no matches in scoped files. | PASS |
| AC10 | Styling uses CSS variables without inline style. | Accordion/action visual rules live in CSS; touched TSX test adds no inline style. | `pnpm --dir frontend lint` PASS; `rg ... style=` PASS no matches in `NatalNarrativeReading.tsx`. | PASS |
| AC11 | Existing natal interaction states stay reachable. | No page/API flow changes; tests retain loading, empty, error, quota, upsell, regeneration, history coverage. | `NatalChartPage` targeted suite PASS. | PASS |
| AC12 | Story evidence artifacts are persisted. | Evidence files under `evidence/`; traceability/final evidence updated. | `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ... --final` PASS. | PASS |
| AC13 | Each chapter toggles by mouse. | `onClick` toggles chapter key. | `natalNarrativeReading` PASS asserts click expansion. | PASS |

All listed ACs are complete for implementation review.
