# Hardcoded values after CS-058

Chosen cluster: prediction cards and adjacent prediction summary cards.

| File | Result | Evidence |
|---|---|---|
| `PeriodCard.css` | migrated selected radius, shadow, gap, font and fallback literals | uses `--radius-lg`, `--shadow-card`, `--space-*`, `--font-size-md`, canonical color tokens |
| `KeyPointCard.css` | migrated selected radius, padding, font, shadow/color fallbacks | uses `--radius-lg`, `--radius-md`, `--space-2`, `--font-size-*`, canonical hero tokens |
| `CategoryGrid.css` | finite tone classes own visual color | `category-grid__tone--*` classes |
| `DayPredictionCard.css` | finite tone classes own visual background | `day-prediction-card__tone--*` classes |
| `TurningPointCard.css` | finite change-type classes own badge/rail visuals | `turning-point-card__type--*`, `turning-point-card__rail--*` |

No token or typography registry update was needed because no new durable token or role was introduced.

Validation: `npm run test -- css-fallback design-system theme-tokens inline-style legacy-style visual-smoke` PASS; `npm run lint` PASS.
