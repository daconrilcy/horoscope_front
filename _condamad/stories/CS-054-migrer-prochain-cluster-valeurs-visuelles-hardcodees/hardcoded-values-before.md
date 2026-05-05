<!-- Baseline CS-054 pour le cluster DayPredictionCard avant decision de migration. -->

# CS-054 - Hardcoded Values Before

## Cluster

- Cluster choisi: `frontend/src/components/prediction/DayPredictionCard.css`
- Files: `frontend/src/components/prediction/DayPredictionCard.css`
- Scope: valeurs visuelles et typographiques detectees par le scan cible demande.
- Non-goal: aucune modification UX, React, route, API, token global ou role typographique global.

## Scan source

Commande depuis la racine du depot:

```powershell
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|font-size:|font-weight:|box-shadow:|border-radius:" frontend\src\components\prediction\DayPredictionCard.css
```

## Counters before

| Metric | Count | Notes |
|---|---:|---|
| Total scanned declarations | 21 | Declarations retournees par le scan cible. |
| Already tokenized declarations | 7 | `font-size` et `font-weight` deja routes vers tokens existants. |
| Hardcoded literal declarations | 14 | Valeurs a classifier avant changement. |
| Clear exact migrations available | 0 | Aucun owner exact et semantiquement sur trouve dans les tokens/roles existants. |
| Ambiguous or local visual decisions | 14 | A documenter dans l'artefact after si conservees. |

## Baseline decision table

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `font-size: var(--font-size-lg)` line 9 | typography | already-canonical | summary text | `--font-size-lg` | keep | token exists in `design-tokens.css` | none |
| `border-radius: 0.75rem` line 16 | radius | keep-classified | calibration notice | none exact | classify after | closest radius tokens are `8px`, `14px`, `20px`, `999px` | near-equivalent radius may alter shape |
| `font-size: 0.9rem` line 17 | typography | keep-classified | calibration notice | none exact | classify after | closest typography token is `--font-size-sm: 0.875rem` | near-equivalent type may alter density |
| `rgba(255, 184, 77, 0.12)` line 18 | color | keep-classified | calibration notice background | none exact | classify after | warning/admin tokens differ in hue and alpha | semantic color change risk |
| `rgba(255, 184, 77, 0.35)` line 19 | color | keep-classified | calibration notice border | none exact | classify after | warning/admin tokens differ in hue and alpha | semantic color change risk |
| `rgba(255, 255, 255, 0.15)` line 23 | color | keep-classified | astro calibration background | none exact | classify after | no global surface token for this exact opacity | contrast change risk |
| `rgba(255, 255, 255, 0.3)` line 24 | color | keep-classified | astro calibration border | none exact | classify after | no exact component-neutral border token | contrast change risk |
| `border-radius: 0.75rem` line 30 | radius | keep-classified | best-window panel | none exact | classify after | closest radius tokens are `8px`, `14px`, `20px`, `999px` | near-equivalent radius may alter shape |
| `rgba(255, 255, 255, 0.05)` line 31 | color | keep-classified | best-window background | none exact | classify after | no global surface token for this exact opacity | contrast change risk |
| `rgba(255, 255, 255, 0.1)` line 32 | color | keep-classified | best-window border | none exact | classify after | exact dark token exists only theme-scoped, not stable globally | theme behavior risk |
| `rgba(255, 255, 255, 0.1)` line 36 | color | keep-classified | astro best-window background | none exact | classify after | exact dark token exists only theme-scoped, not stable globally | theme behavior risk |
| `rgba(255, 255, 255, 0.2)` line 37 | color | keep-classified | astro best-window border | none exact | classify after | no exact component-neutral border token | contrast change risk |
| `font-size: 0.9rem` line 42 | typography | keep-classified | best-window title | none exact | classify after | closest role is `eyebrow`, but size is `0.75rem` and includes letter spacing | role mismatch risk |
| `font-size: var(--font-size-md)` line 48 | typography | already-canonical | best-window time | `--font-size-md` | keep | token exists in `design-tokens.css` | none |
| `font-weight: var(--font-weight-medium)` line 49 | typography | already-canonical | best-window time | `--font-weight-medium` | keep | token exists in `design-tokens.css` | none |
| `font-size: var(--font-size-sm)` line 54 | typography | already-canonical | best-window description | `--font-size-sm` | keep | token exists in `design-tokens.css` | none |
| `font-size: var(--font-size-2xl)` line 60 | typography | already-canonical | date title | `--font-size-2xl` | keep | token exists in `design-tokens.css` | none |
| `border-radius: 1rem` line 68 | radius | keep-classified | tone badge | none exact | classify after | `--radius-pill` is semantic but not exact; `--space-4` is exact but not a radius owner | near-equivalent or wrong-namespace risk |
| `font-size: var(--font-size-sm)` line 69 | typography | already-canonical | tone badge | `--font-size-sm` | keep | token exists in `design-tokens.css` | none |
| `font-weight: var(--font-weight-bold)` line 70 | typography | already-canonical | tone badge | `--font-weight-bold` | keep | token exists in `design-tokens.css` | none |
| `box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.1)` line 72 | shadow | keep-classified | tone badge | none exact | classify after | global shadows are larger elevation roles | elevation change risk |

## Proposed migration stance

- No new token or typography role should be created for this cluster.
- Preserve current literals when no exact semantic owner exists.
- Final evidence must classify every preserved literal in `hardcoded-values-after.md`.
