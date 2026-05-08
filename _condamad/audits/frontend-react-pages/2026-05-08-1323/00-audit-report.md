<!-- Rapport d'audit CONDAMAD de cloture des pages React frontend. -->

# CONDAMAD Domain Audit - frontend-react-pages

Date: 2026-05-08 13:23 Europe/Paris

## Domain

- Domain key: `frontend-react-pages`
- Target: `frontend/src/pages/**`, `frontend/src/app/routes.tsx`, page-facing feature owners, page architecture guards, and directly related CONDAMAD stories.
- Archetypes: `legacy-surface-audit`, `dependency-direction-audit`, `test-guard-coverage-audit`, `no-legacy-dry-audit-contract`.
- Mode: read-only application audit. Only audit artifacts were written.

## Domain Closure Status

Status: `closed`

The three residual findings from the 11:42 audit are closed in the current worktree:

1. `CS-100` reduced `AdminPromptsPage.tsx` to an 81-line route shell and moved the catalog, consumption, release, personas, and sample-payload surfaces behind `frontend/src/features/admin-prompts/**`.
2. `CS-101` emptied `PAGE_SIZE_EXCEPTIONS`; no `frontend/src/pages/**/*.tsx` file is above the 700-line guard threshold.
3. `CS-102` centralized page date/time UI formatting through `frontend/src/utils/formatDate.ts`; the residual scan hits are numeric-only formatting.

No in-domain implementation story remains for `frontend-react-pages` from the prior audit chain.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/**`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/**`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/**`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/**`
- `_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/**`
- `_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/**`
- `_condamad/stories/CS-093-converger-barrels-pages-exports-stale/**`
- `_condamad/stories/CS-094-classer-converger-routes-alias-publiques/**`
- `_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/**`
- `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/**`
- `_condamad/stories/CS-097-centraliser-appels-api-admin-restants-hors-pages/**`
- `_condamad/stories/CS-098-classer-centraliser-helpers-formatage-pages/**`
- `_condamad/stories/CS-099-typer-pages-react-exclues-typescript/**`
- `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/**`
- `_condamad/stories/CS-101-decomposer-pages-volumineuses-allowlistees/**`
- `_condamad/stories/CS-102-centraliser-formatage-date-heure-pages/**`

## Regression Guardrails Consulted

- `RG-064` - page architecture guard: `@ts-nocheck`, direct page API calls, public aliases, stale admin exports, and page size exceptions.
- `RG-065` - AdminPrompts route shell must delegate active sections to feature owners.
- `RG-066` - page-size exceptions outside AdminPrompts must remain exact or absent.
- `RG-067` - page date/time UI formatting must use `frontend/src/utils/formatDate.ts` or be classified.

No new durable invariant was discovered beyond the existing guardrails above, so `_condamad/stories/regression-guardrails.md` was not changed.

## Prior Finding Closure Ledger

| Prior finding | Current classification | Current evidence | Notes |
|---|---|---|---|
| 11:42 F-001 AdminPrompts route container still has extractable sections | `closed` | E-002, E-003, E-006, E-007, E-008 | `AdminPromptsPage.tsx` is 81 lines and delegates active surfaces to `features/admin-prompts`; `PAGE_SIZE_EXCEPTIONS` is empty. |
| 11:42 F-002 oversized page allowlist outside AdminPrompts remains active | `closed` | E-003, E-004, E-006, E-007 | No page file exceeds 700 lines; `PAGE_SIZE_EXCEPTIONS` is empty and `page-architecture` passes. |
| 11:42 F-003 inline date/time formatting remains duplicated in pages | `closed` | E-005, E-006, E-007, E-009 | Final date/time scan has only numeric-only hits; date/time helpers are owned by `formatDate.ts` and tested. |
| 10:24 F-002 admin direct API exceptions | `closed` | E-004, E-006 | Zero `apiFetch(` hits under `frontend/src/pages`; allowlist is empty. |
| 10:24 F-004 page `@ts-nocheck` | `closed` | E-004, E-006 | Zero page `@ts-nocheck` hits; allowlist is empty. |
| 01:23 F-004 stale and duplicate page barrels | `closed` | E-004, E-006 | Forbidden admin barrel exports remain absent. |
| 01:23 F-005 public route aliases | `closed` | E-004, E-006 | Forbidden public route aliases remain absent. |
| 01:23 F-006 missing page architecture drift guard | `closed` | E-003, E-006, RG-064 | `page-architecture` guard exists and passes. |

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Info | 1 |

The single Info entry records the closure observation for traceability; it does not require an implementation story.

## Exhaustive Remaining Implementation Surfaces

Application files: none.

Governance/test files: none.

Deferred non-domain context:

- Numeric formatting hits in `AdminDashboardPage`, `SubscriptionGuidePage`, and `UsageSettings` are not date/time UI formatting and do not keep `frontend-react-pages` open.
- Broader API-client consistency inside `frontend/src/api/**` remains outside this page-domain audit.
- Design-system token/CSS work remains governed by `RG-044` through `RG-063` and is not reopened here.

## Validation

- `npm run lint` from `frontend/`: PASS.
- `npm run test -- page-architecture formatDate AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow AstrologerProfile BirthProfile SubscriptionSettings AdminSamplePayloads` from `frontend/`: PASS, 9 files passed, 121 tests passed, 8 skipped.
- Audit artifact validation and lint were run after report generation; see `01-evidence-log.md`.
