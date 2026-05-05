# Inline styles after CS-057

Scan command: `rg -n "style=\\{" src -g "*.tsx"` from `frontend`.

Final executable allowlist count: 9 entries.
Deleted entries: `CategoryGrid.tsx` x2, `DayPredictionCard.tsx` x1, `TurningPointCard.tsx` x2.

| File | Result | Evidence |
|---|---|---|
| `frontend/src/components/prediction/CategoryGrid.tsx` + `.css` | inline colors converted | score/band use `category-grid__tone--*` classes |
| `frontend/src/components/prediction/DayPredictionCard.tsx` + `.css` | tone background converted | `day-prediction-card__tone--*` classes |
| `frontend/src/components/TurningPointCard.tsx` + `.css` | badge/rail styles converted | `turning-point-card__type--*` and rail classes |
| `frontend/src/tests/inline-style-allowlist.ts` | synchronized | removed deleted dynamic entries |
| `frontend/src/tests/design-system-allowlist.ts` | synchronized | `INLINE_STYLE_EXCEPTIONS` matches runtime scan |
| `Skeleton.tsx` | preserved | `style` and `--skeleton-gap` remain allowlisted |

Validation: `npm run test -- css-fallback design-system theme-tokens inline-style legacy-style visual-smoke` PASS; `npm run lint` PASS.
