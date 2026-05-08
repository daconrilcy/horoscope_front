# Story CS-113 classer-converger-composants-consommateurs-api: Classer et converger les composants frontend consommateurs d'API

Status: done

## 1. Objective

Converger la surface `frontend/src/components/**` qui consomme `api`, `features`,
`fetch`, `apiFetch` ou `axios` vers des owners explicites. La sortie attendue
est un owner feature/page, un container classe avec exception exacte, ou un
composant presentational API-free.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md#SC-001`
- Reason for change: `frontend/src/components` agit comme second owner d'orchestration API/feature au lieu de rester une couche de composants reutilisables.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - Classer tous les hits de la regle `F-001`.
  - Relocaliser ou scinder les containers qui ne doivent pas rester sous `components`.
  - Ajouter ou mettre a jour une allowlist exacte et un guard executable des imports API/feature dans les composants.
- Out of scope:
  - Refonte des routes pages, deja couverte par `frontend-react-pages`.
  - Refonte de la hierarchie layout, deja couverte par `frontend-layouts`.
  - Changement de contrat backend/API.
- Explicit non-goals:
  - Ne pas modifier les invariants `RG-047`, `RG-048`, `RG-049`, `RG-050`, `RG-064`, `RG-067`, `RG-068`.
  - Ne pas creer de barrels legacy, aliases, wrappers ou hooks API dupliques.
  - Ne pas accepter d'exception dossier ou wildcard.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: ownership-routing-refactor
- Archetype reason: la story repartit l'ownership API/feature entre owners canoniques et exceptions exactes.
- Behavior change allowed: no
- Behavior change constraints:
  - Les ecrans et workflows existants doivent conserver leur comportement observable.
  - Les differences autorisees sont limitees aux chemins d'import et a l'ownership interne.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le owner canonique d'un fichier liste par `F-001` ne peut pas etre determine par imports, route de montage ou usage runtime.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | le guard AST executable devient source de verite de l'architecture composants/API. |
| Baseline Snapshot | yes | l'inventaire avant/apres des imports interdits est obligatoire. |
| Ownership Routing | yes | chaque hit doit recevoir un owner canonique ou une exception exacte. |
| Allowlist Exception | yes | les containers conserves sous `components` doivent etre exacts, motives et dates. |
| Contract Shape | no | aucun DTO, OpenAPI ou type public d'API n'est change. |
| Batch Migration | yes | le lot couvre plusieurs familles de composants avec une fermeture bornee. |
| Reintroduction Guard | yes | un guard doit echouer si un nouvel import API/feature non allowliste apparait. |
| Persistent Evidence | yes | les inventaires before/after et l'allowlist doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/component-architecture-guards.test.ts`, executed by `npm run test -- component-architecture`.
- Secondary evidence:
  - targeted `rg` scan for API, feature, `apiFetch`, `fetch` and `axios` usage under `frontend/src/components`.
- Static scans alone are not sufficient for this story because:
  - the AST guard must enforce exact allowlist entries and fail deterministically when a new forbidden import appears.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-113-classer-converger-composants-consommateurs-api/component-api-imports-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-113-classer-converger-composants-consommateurs-api/component-api-imports-after.md`
- Expected invariant:
  - le scan cible est zero-hit ou chaque hit restant est exact, owned, teste et assorti d'une condition de sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Orchestration API admin/B2B/ops | `frontend/src/features/**` ou page owner prouve | composant shared non classe |
| Formulaires auth avec appels API | `frontend/src/features/auth/**` ou exception container exacte | helper UI shared |
| Consommation auth de layout | layout owner si intentionnellement shell container | composant presentational |
| Composant presentational reusable | `frontend/src/components/**` sans import API/feature | feature API hook local duplique |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `component-architecture-allowlist.ts` | entries exactes | containers retenus | owner, raison, commande et exit condition |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| admin-ops | admin/B2B/ops panels | feature owners or exceptions | imports | `npm run test -- component-architecture` | scan | owner absent |
| auth-layout | auth/layout/settings/dashboard | auth/layout owners | imports | `npm run test -- component-architecture` | no re-export | shell ambigu |
| natal-privacy | `NatalInterpretation`, `PrivacyPanel` | natal/privacy owners | tests/pages | `npm run test -- natalInterpretation` | imports documented | CS-115 dependency |

Closure map:

- Total affected surface: tous les fichiers listes sous `F-001` dans `03-story-candidates.md`.
- Batches included in this story: inventaire complet, classification et convergence/allowlist exacte de chaque hit.
- Batches intentionally deferred: none, sauf blocage `needs-user-decision` fichier par fichier.
- Stop condition for the source finding: scan zero-hit ou hits tous exacts, owned, testes, dates.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before inventory | `_condamad/stories/CS-113-classer-converger-composants-consommateurs-api/component-api-imports-before.md` | prouver la surface initiale F-001 |
| after inventory | `_condamad/stories/CS-113-classer-converger-composants-consommateurs-api/component-api-imports-after.md` | prouver la fermeture ou les exceptions exactes |
| classification table | `_condamad/stories/CS-113-classer-converger-composants-consommateurs-api/component-api-ownership.md` | documenter owner, decision, preuve, exit condition |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `from "../api"` or `from "../../api"` in `frontend/src/components/**/*.tsx`
- `from "../features"` or `from "../../features"` in `frontend/src/components/**/*.tsx`
- `apiFetch(`, raw `fetch(` and `axios` in shared components unless exact allowlist entry exists

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- component-architecture` checks forbidden component API/feature ownership.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md#F-001`
- Closure proof required: before/after inventory, ownership table, exact allowlist diff and passing component architecture guard.
- Known residual in-domain work: none if every hit is closed or exact; otherwise only files explicitly marked `needs-user-decision` with owner ambiguity and risk.
- Deferred non-domain concerns: page route ownership remains in `frontend-react-pages`; layout hierarchy remains in `frontend-layouts`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md` - `F-001` lists API/feature orchestration in component files.
- Evidence 2: `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md` - exact selection rule and expected closure map.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

- Every `F-001` hit has a canonical owner, exact retained exception, or blocker.
- Shared presentational components do not import API/feature modules or perform network orchestration.
- Component architecture guard fails on unclassified new API/feature imports.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-050` - design-system and component guards remain executable.
  - `RG-064` - page architecture suppressions/imports must not be weakened while moving ownership.
  - `RG-068` - layout shell ownership must remain explicit for layout consumers.
- Non-applicable invariants:
  - `RG-047` and `RG-048` - no inline style or CSS fallback change is required.
- Required regression evidence:
  - `npm run test -- component-architecture components design-system inline-style legacy-style`
  - targeted import scan from `SC-001`.
- Allowed differences:
  - Import paths and file ownership may change only as documented in `component-api-ownership.md`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `F-001` after inventory matches the closure rule. | Evidence profile: `baseline_before_after_diff`; `rg -n 'apiFetch|fetch|axios|from .*api' frontend/src/components`. |
| AC2 | Every hit has an owner decision or exact blocker. | Evidence profile: `allowlist_register_validated`; `npm run test -- component-architecture`. |
| AC3 | No forbidden escape hatch is added. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n 'apiFetch|axios' frontend/src/components`. |
| AC4 | New unallowlisted component API/feature access fails the guard. | Evidence profile: `reintroduction_guard`; AST guard via `npm run test -- component-architecture`. |
| AC5 | Existing design/page/layout guards still pass. | Evidence profile: `ast_architecture_guard`; `npm run test -- components design-system` and `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture baseline inventory (AC: AC1)
  - [ ] Run the exact `F-001` scan and persist results.
  - [ ] Record current allowlist or absence of allowlist.
- [ ] Task 2 - Classify and converge each hit (AC: AC2, AC3)
  - [ ] Move, split or classify each exact file listed by `SC-001`.
  - [ ] Stop on ambiguous owners and record `needs-user-decision` only for exact files.
- [ ] Task 3 - Add deterministic guard (AC: AC4)
  - [ ] Add/update `component-architecture-allowlist.ts` and guard tests.
  - [ ] Prove no wildcard exception exists.
- [ ] Task 4 - Persist after evidence and run validation (AC: AC1, AC5)
  - [ ] Write after inventory and ownership table.
  - [ ] Run targeted tests, scans and lint.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - existing frontend API clients/hooks under `frontend/src/api` or existing feature owners.
  - existing architecture test conventions in `frontend/src/tests`.
- Do not recreate:
  - duplicate API hooks inside components.
  - barrel compatibility paths.
- Shared abstraction allowed only if:
  - at least two current consumers use the same responsibility and no existing module owns it.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- unallowlisted `apiFetch(`, raw `fetch(`, `axios` in `frontend/src/components/**`
- wildcard allowlists in `frontend/src/tests/component-architecture-allowlist.ts`
- re-export paths that preserve moved containers as legacy facades

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| API/feature orchestration | feature, page or layout owner proven by runtime usage | reusable presentational components |
| Shared UI rendering | `frontend/src/components/**` without API/feature imports | feature workflow modules |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- all files listed under `F-001` in `03-story-candidates.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/component-architecture-allowlist.ts` - exact component API/feature exceptions.
- `frontend/src/tests/component-architecture-guards.test.ts` - guard implementation.
- one or more files listed under `F-001` - owner convergence or import cleanup.

Likely tests:

- `frontend/src/tests/component-architecture-guards.test.ts` - import direction guard.

Files not expected to change:

- `backend/app/**` - no backend contract change.
- `frontend/src/styles/design-tokens.css` - no token change required.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- component-architecture components
npm run test -- design-system inline-style legacy-style
npm run lint
rg -n 'from ["''](\.\./api|\.\./\.\./api|@/api|@api|\.\./features|\.\./\.\./features|@/features)|apiFetch\(|fetch\(|axios' src/components -g '*.ts' -g '*.tsx'
```

## 22. Regression Risks

- Risk: moving a component breaks route/page imports.
  - Guardrail: targeted component/page tests plus no-shim proof.
- Risk: broad allowlist hides future component API drift.
  - Guardrail: exact allowlist schema and `component-architecture` guard.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass convergence through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work for exact files in this story.

## 24. References

- `_condamad/audits/frontend-components/2026-05-08-2303/00-audit-report.md` - audit scope and active findings.
- `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md#F-001` - source finding.
- `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md#SC-001` - story candidate contract.
- `_condamad/stories/regression-guardrails.md` - regression invariants.
