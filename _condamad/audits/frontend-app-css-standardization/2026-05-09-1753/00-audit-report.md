<!-- Rapport de re-audit CONDAMAD pour la standardisation generique de frontend/src/App.css. -->

# Audit Report - frontend-app-css-standardization

## Domain Closure Status

Status: phased-with-map

Le domaine audite reste `frontend-app-css-standardization`, limite a `frontend/src/App.css`, ses consommateurs de classes App, et les guards design-system qui protegent cette surface. Les stories annoncees ont ete implementees, mais le stop condition de fermeture n'est pas completement atteint: la garde finale ferme une sous-liste de mots, tandis que des prefixes `--app-*` et familles visuelles non generiques restent actifs.

## Prior Audit And Story History Consulted

| Source | Status Under Current Evidence | Evidence | Notes |
|---|---|---|---|
| `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145` F-001 | still-active | E-003, E-008, E-013 | Les primitives existent, mais la taxonomie `--app-*` reste non fermee avec 442 variables et des prefixes domain/component. |
| `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145` F-002 | closed for structural primitives | E-005, E-011, E-015 | Les layouts/etats/actions consomment des primitives App et les guards ciblés passent. |
| `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145` F-003 | still-active, narrowed | E-006, E-014 | Les familles principales ont converge, mais `precision` et `evidence` restent dans `App.css`. |
| `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145` F-004 | still-active, narrowed | E-007, E-012, E-014 | La garde CS-124 existe, mais son vocabulaire ne couvre pas tous les residus de SC-003. |
| `_condamad/stories/CS-121-definir-primitives-css-generiques-app` | implemented | E-004, E-011 | Primitives App creees et consommees. |
| `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css` | implemented | E-005, E-011 | Migration structurelle confirmee par consumers `app-*`. |
| `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css` | implemented but incomplete for declared residuals | E-006, E-014 | `precision/evidence` etaient dans la surface candidate et restent actifs. |
| `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques` | implemented but partial guard | E-007, E-009, E-012 | `RG-075` protege cinq mots; autres prefixes App non generiques non couverts. |
| `_condamad/stories/regression-guardrails.md` | applicable | E-002 | `RG-044` a `RG-050`, `RG-059`, `RG-061`, `RG-075` consultes. |

## Audit Scope

In scope:

- `frontend/src/App.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- TSX consumers of classes defined in `App.css`, read-only for ownership evidence
- CONDAMAD story and audit artifacts for CS-121 a CS-124

Out of scope:

- CSS page-scoped hors `App.css`, sauf extraction future depuis `App.css`
- Backend, API, auth, billing, DB
- Refactor effectif du CSS dans cet audit

## Evidence Summary

See `01-evidence-log.md`.

Highlights:

- E-008: `App.css` contient 4217 lignes, 442 variables `--app-*`, 375 classes uniques, zero hit sur les cinq mots `RG-075`.
- E-011: les primitives App sont consommees par les surfaces React.
- E-012: la garde CS-124 est active mais limitee a `astrolog|consult|dashboard|settings|wizard|expert|session|preferences|overview`.
- E-013: les prefixes `person`, `activity`, `summary`, `flow`, `premium`, `precision`, `evidence`, `people`, `chat`, `usage` restent dans `--app-*`.
- E-014: `precision-badge` et `evidence-*` restent actifs dans `App.css` et dans des TSX consumers.
- E-015 a E-018: tests ciblés, lint, build et whitespace check passent.

## Findings Summary

| ID | Severity | Summary | Story |
|---|---|---|---|
| F-001 | High | Taxonomie `--app-*` encore non fermee malgre les primitives. | SC-001 |
| F-002 | Medium | Garde CS-124 partielle pour les familles `precision/evidence`. | SC-002 |

## Closure Analysis

Active findings remaining after implemented stories:

- F-001 remains active from the prior audit because `--app-*` still owns many page/component/domain prefixes without a complete classification.
- F-003/F-004 from the prior audit are narrowed into F-002 for the exact residual families `precision/evidence`.

Findings now closed:

- Prior F-002 is closed for structural primitives: TSX consumers use `.app-panel`, `.app-state`, `.app-actions`, `.app-list`, `.app-modal` and related primitives; targeted tests pass.
- The No Legacy comment/vocabulary portion of prior F-004 is closed for `App.css`: zero hit on `OLD|legacy|alias|compat|compatibility|shim|migration-only`.
- The five-word CS-124 guard is closed for `astrologer|consultation|dashboard|settings|wizard`: zero hit in `App.css`.

Complete closure map:

1. SC-001: classify and close every remaining `--app-*` prefix by owner decision, migration, or documented semantic extension.
2. SC-002: close the exact `precision/evidence` visual-family residual or classify it as source-backed public CSS contract.
3. Update the App specificity guard from a narrow forbidden-word regex to a positive allowlist of accepted prefixes/selectors.

Stop condition:

- Every `--app-*` prefix in `App.css` appears in a source-backed allowlist with owner, rationale and exit condition when temporary.
- `precision/evidence` are either absent from `App.css` or documented as intentional public/exported style surfaces with exact guards.
- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`, `npm run lint`, and `npm run build` pass.
- No follow-up audit is required to rediscover the same residual App prefixes.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `frontend/src/App.css` | used | E-008, E-011, E-015 | Global App stylesheet, primary audited surface, consumed by React classes and design-system guards. | Runtime browser screenshot not captured in this audit. |
| `frontend/src/tests/design-system-guards.test.ts` | test-only | E-012, E-015 | Owner of App literal, token and specificity guards. | Guard coverage is partial for F-002. |
| `frontend/src/tests/design-system-allowlist.ts` | test-only | E-012, E-015 | Exact exception registry; `APP_CSS_SPECIFICITY_EXCEPTIONS` is currently empty. | none |
| `frontend/src/styles/token-namespace-registry.md` | used | E-002, E-012, E-015 | Governance registry for token namespaces, including `--app-*`. | Current registry does not itself classify every App prefix. |
| `frontend/src/styles/typography-roles.md` | used | E-002, E-015 | Governance registry for typographic role checks. | No direct change required by this audit unless SC-001 alters typography ownership. |
| `frontend/src/styles/utilities.css` | used | E-003, E-011 | Existing reusable utility surface and potential extraction target. | No direct residual proved in this audit. |
| `frontend/src/features/consultations/components/ConsultationSummaryStep.tsx` | used | E-014 | Active consumer of `.precision-badge*`. | Only class consumption is in-domain. |
| `frontend/src/features/consultations/components/DataCollectionStep.tsx` | used | E-014 | Active consumer of `.precision-badge*`. | Only class consumption is in-domain. |
| `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx` | used | E-014 | Active consumer of `.evidence-pill*` and `.evidence-tags__list`. | Feature logic is out-of-domain. |
| `_condamad/stories/CS-121-definir-primitives-css-generiques-app/**` | test-only | E-004 | Story/evidence capsule consulted for closure ledger. | Historical artifact, not application runtime. |
| `_condamad/stories/CS-122-migrer-layouts-etats-actions-vers-primitives-css/**` | test-only | E-005 | Story/evidence capsule consulted for closure ledger. | Historical artifact, not application runtime. |
| `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/**` | test-only | E-006 | Story/evidence capsule consulted for closure ledger. | Historical artifact, not application runtime. |
| `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/**` | test-only | E-007 | Story/evidence capsule consulted for closure ledger and `RG-075`. | Historical artifact, not application runtime. |
| `frontend/src/pages/**/*.css` | out-of-domain | E-003 | Page-scoped CSS inspected only as boundary context. | Exact files not inventoried because this audit targets `App.css`. |
| `frontend/src/**/*.tsx` consumers not listed above | out-of-domain | E-011 | Consumers prove usage of App primitives; their feature/page logic is not audited. | Exact migration set belongs to implementation story scans. |

## DRY, No Legacy, Mono-Domain, Dependency Direction

- DRY: FAIL for `--app-*` ownership. E-013 proves many residual page/component/domain prefixes remain under the App namespace.
- No Legacy: PASS for explicit legacy vocabulary in `App.css` by E-010; FAIL only in the broader sense that old visual-family names `precision/evidence` remain unclassified by E-014.
- Mono-domain: PASS. Findings are limited to frontend App CSS standardization.
- Dependency direction: PASS. No backend/API dependency issue is in scope or observed.

## Story Candidates

See `03-story-candidates.md`.

