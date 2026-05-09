<!-- Rapport d'audit CONDAMAD pour la standardisation generique de frontend/src/App.css. -->

# Audit Report - frontend-app-css-standardization

## Domain Closure Status

Status: phased-with-map

Le domaine audite est limite a la standardisation de `frontend/src/App.css` en classes generiques reutilisables. Les audits precedents ont ferme la dette de valeurs visuelles/typographiques hardcodees, mais pas la dette de specificite des classes et variables.

## Prior Audit And Story History Consulted

| Source | Status Under Current Evidence | Evidence | Notes |
|---|---|---|---|
| `_condamad/audits/frontend-design-system/2026-05-08-0054` | closed for tokenization | E-004 | Ne couvre pas la reutilisation generique des classes. |
| `_condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/00-story.md` | still-active as guardrail, superseded for this goal | E-005, E-011 | Protege les literals et noms mecaniques, pas les noms page-specific. |
| `_condamad/stories/regression-guardrails.md` `RG-044` a `RG-063` | still-active | E-003 | Applicables comme contraintes de non-regression. |

## Audit Scope

In scope:

- `frontend/src/App.css`
- TSX consumers of classes defined in `App.css`, inspected only to bound future stories
- design-system guard files and registries as governance surfaces

Out of scope:

- Refactor effectif du CSS applicatif dans cet audit
- CSS page-scoped hors `App.css`, sauf comme deferred non-domain context
- Backend, API, auth, billing, routing behavior

## Evidence Summary

See `01-evidence-log.md`.

Highlights:

- E-006: 4146 lines, 442 `--app-*` variables, 439 single-use variables, 482 unique classes, 243 classes with domain/page words.
- E-007: top variable prefixes are page/component specific.
- E-008: repeated structural declarations prove DRY violation.
- E-012 and E-013: current guard suite and lint pass, so the issue is architectural standardization, not broken syntax.

## Findings Summary

| ID | Severity | Summary | Story |
|---|---|---|---|
| F-001 | High | Centralisation without generic primitives. | SC-001 |
| F-002 | High | Structural DRY violation across layouts, states and actions. | SC-002 |
| F-003 | Medium | Visual component families named by domain instead of reusable variants. | SC-003 |
| F-004 | Medium | Missing anti-return guard for page-specific App selectors and variables. | SC-004 |

## Closure Analysis

Active findings remaining after previous stories:

- F-001 through F-004 are active and in-domain.

Findings now closed:

- Prior hardcoded-value convergence from `CS-087` is treated as closed for value routing by E-011 and E-012.

Complete closure map:

1. Define generic primitives and registry rules (`CS-121`).
2. Migrate structural consumers (`CS-122`).
3. Migrate visual component families (`CS-123`).
4. Add final anti-return guard (`CS-124`).

Stop condition:

- `App.css` exposes only documented generic primitives and accepted base element rules.
- No `--app-*` variable name contains page/service/component domain words except exact, justified semantic owners.
- No class selector in `App.css` uses the audited forbidden domain words unless exact allowlist entry is present with an exit condition.
- Design-system, visual-smoke and lint commands pass.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `frontend/src/App.css` | used | E-006, E-009, E-012 | Global stylesheet imported by the frontend and covered by design-system guards; primary audited surface. | Runtime browser screenshot not captured in this audit. |
| `frontend/src/tests/design-system-guards.test.ts` | test-only | E-011, E-012 | Existing guard owner for App CSS literals and future anti-drift checks. | none |
| `frontend/src/tests/design-system-allowlist.ts` | test-only | E-011, E-012 | Exact allowlist owner for CSS fallback and inline-style exceptions. | none |
| `frontend/src/styles/token-namespace-registry.md` | used | E-003, E-011, E-012 | Governance registry consumed by design-system tests. | none |
| `frontend/src/styles/typography-roles.md` | used | E-011, E-012 | Governance registry for typographic roles referenced by guards. | none |
| `frontend/src/styles/utilities.css` | used | E-011, E-012 | Existing owner for generic typography utilities; expected reuse target. | none |
| `frontend/src/App.tsx` | out-of-domain | E-009 | Potential consumer context only; no direct edit required by audit artifact. | Consumer changes are deferred to stories. |
| `frontend/src/layouts/**/*.tsx` | out-of-domain | E-009 | Potential consumer context for generic layout classes. | Exact files must be inventoried by implementation stories. |
| `frontend/src/pages/**/*.tsx` | out-of-domain | E-009 | Potential consumer context for page class migrations. | Exact files must be inventoried by implementation stories. |
| `frontend/src/features/**/*.tsx` | out-of-domain | E-009 | Potential consumer context for feature class migrations. | Exact files must be inventoried by implementation stories. |
| `frontend/src/components/**/*.tsx` | out-of-domain | E-009 | Potential consumer context for component class migrations. | Exact files must be inventoried by implementation stories. |

## DRY, No Legacy, Mono-Domain, Dependency Direction

- DRY: FAIL. E-008 proves repeated structural declarations and E-006 proves mostly single-use variables.
- No Legacy: FAIL for active comment `/* Consultations Page OLD */`; `fallback` class names require classification but are not automatically legacy.
- Mono-domain: PASS for this audit; the implementation stories must stay in `frontend-app-css-standardization`.
- Dependency direction: PASS; no backend or API dependency issue found.

## Story Candidates

See `03-story-candidates.md`.

