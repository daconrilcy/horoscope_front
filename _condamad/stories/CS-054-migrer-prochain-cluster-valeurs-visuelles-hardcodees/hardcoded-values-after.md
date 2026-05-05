<!-- Decisions finales CS-054 pour le cluster DayPredictionCard apres migration conservatrice. -->

# CS-054 - Hardcoded Values After

## Cluster

- Cluster choisi: `frontend/src/components/prediction/DayPredictionCard.css`
- Files: `frontend/src/components/prediction/DayPredictionCard.css`
- Resultat: aucune migration CSS appliquee, car aucun literal restant n'a de mapping exact et semantiquement sur vers un token, role ou variable existant.
- Registry updates: none. Aucun namespace token ni role typographique durable n'a ete cree.

## Counters after

| Metric | Before | After | Delta | Decision |
|---|---:|---:|---:|---|
| Total scanned declarations | 21 | 21 | 0 | Scan stable; pas de changement UX. |
| Already tokenized declarations | 7 | 7 | 0 | Conservees telles quelles. |
| Hardcoded literal declarations | 14 | 14 | 0 | Toutes classees ci-dessous. |
| Clear exact migrations applied | 0 | 0 | 0 | Bloque par absence d'owner exact. |
| Declarations sans decision finale | 14 | 0 | -14 | 100% des valeurs ont une decision finale. |

## Final decision table

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `font-size: var(--font-size-lg)` line 9 | typography | already-canonical | summary text | `--font-size-lg` | keep | token exists in `design-tokens.css` | none |
| `border-radius: 0.75rem` line 16 | radius | keep-classified | calibration notice | none exact | keep | `--radius-sm: 8px`, `--radius-md: 14px`, `--radius-lg: 20px`; no `12px` token | revisit only if a component-card radius token of `12px` is introduced |
| `font-size: 0.9rem` line 17 | typography | keep-classified | calibration notice | none exact | keep | existing nearest `--font-size-sm` is `0.875rem`; no exact role | revisit if a compact notice typography role is defined |
| `rgba(255, 184, 77, 0.12)` line 18 | color | keep-classified | calibration notice background | none exact | keep | admin warning token has different hue/value | revisit if a public warning surface token is added |
| `rgba(255, 184, 77, 0.35)` line 19 | color | keep-classified | calibration notice border | none exact | keep | admin warning token has different hue/value | revisit if a public warning border token is added |
| `rgba(255, 255, 255, 0.15)` line 23 | color | keep-classified | astro calibration background | none exact | keep | existing glass tokens use different theme-dependent opacities | revisit with prediction astro surface tokens |
| `rgba(255, 255, 255, 0.3)` line 24 | color | keep-classified | astro calibration border | none exact | keep | existing border tokens are not exact or are premium/admin scoped | revisit with prediction astro border tokens |
| `border-radius: 0.75rem` line 30 | radius | keep-classified | best-window panel | none exact | keep | repeated `12px` radius has no exact global radius token | revisit if a component-card radius token of `12px` is introduced |
| `rgba(255, 255, 255, 0.05)` line 31 | color | keep-classified | best-window background | none exact | keep | no exact neutral surface token | revisit with prediction panel surface tokens |
| `rgba(255, 255, 255, 0.1)` line 32 | color | keep-classified | best-window border | none exact | keep | exact value appears in dark token context only, not as stable global border semantic | revisit with prediction panel border tokens |
| `rgba(255, 255, 255, 0.1)` line 36 | color | keep-classified | astro best-window background | none exact | keep | exact value appears in dark token context only, not as stable global surface semantic | revisit with prediction astro surface tokens |
| `rgba(255, 255, 255, 0.2)` line 37 | color | keep-classified | astro best-window border | none exact | keep | no exact neutral border token | revisit with prediction astro border tokens |
| `font-size: 0.9rem` line 42 | typography | keep-classified | best-window title | none exact | keep | `eyebrow` role changes size, weight, line-height and letter-spacing | revisit if a compact uppercase title role is defined |
| `font-size: var(--font-size-md)` line 48 | typography | already-canonical | best-window time | `--font-size-md` | keep | token exists in `design-tokens.css` | none |
| `font-weight: var(--font-weight-medium)` line 49 | typography | already-canonical | best-window time | `--font-weight-medium` | keep | token exists in `design-tokens.css` | none |
| `font-size: var(--font-size-sm)` line 54 | typography | already-canonical | best-window description | `--font-size-sm` | keep | token exists in `design-tokens.css` | none |
| `font-size: var(--font-size-2xl)` line 60 | typography | already-canonical | date title | `--font-size-2xl` | keep | token exists in `design-tokens.css` | none |
| `border-radius: 1rem` line 68 | radius | keep-classified | tone badge | none exact | keep | `--radius-pill` is semantic but not exact; `--space-4` is exact but wrong namespace for radius | revisit if a `16px` radius token is introduced or tone badge is explicitly redesigned as pill |
| `font-size: var(--font-size-sm)` line 69 | typography | already-canonical | tone badge | `--font-size-sm` | keep | token exists in `design-tokens.css` | none |
| `font-weight: var(--font-weight-bold)` line 70 | typography | already-canonical | tone badge | `--font-weight-bold` | keep | token exists in `design-tokens.css` | none |
| `box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.1)` line 72 | shadow | keep-classified | tone badge | none exact | keep | `--shadow-card`, `--shadow-hero`, `--shadow-nav` are larger elevation roles | revisit if a compact badge shadow token is introduced |

## Validation notes

- AC1: cluster explicit in this file and in `hardcoded-values-before.md`.
- AC2: aucun marqueur de decision ouverte ne reste.
- AC3: no clear mapping was found, so no CSS migration was applied.
- AC4: no semantic extension was created; registry updates are not required.
- AC5: hardcoded counter did not decrease because all 14 candidates are blocked by exactness or ownership risk.
- AC6: frontend validation must be reported from command output.
