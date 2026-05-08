# Story CS-114 supprimer-suppressions-typescript-composants: Supprimer les suppressions TypeScript non gardees dans les composants

Status: done

## 1. Objective

Supprimer les `@ts-nocheck` presents dans les composants listes par `F-002`, ou
conserver uniquement une exception exacte, owned et expirante si un blocage
TypeScript externe empeche la correction immediate.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md#SC-002`
- Reason for change: des fichiers composants peuvent echapper au typage sans garde de domaine.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - `EnterpriseCredentialsPanel.tsx`, `OpsMonitoringPanel.tsx`, `SupportOpsPanel.tsx`, `ui/Form/Form.tsx`, `ui/Form/Form.test.tsx`.
  - Guard et allowlist exacts pour `@ts-nocheck` sous `frontend/src/components/**`.
- Out of scope:
  - Suppressions TypeScript sous `frontend/src/pages/**`.
  - Refactor d'ownership API des composants, couvert par `CS-113`.
  - Changement de configuration TypeScript globale.
- Explicit non-goals:
  - Ne pas affaiblir `tsconfig.lint.json`, ESLint ou les tests existants.
  - Ne pas introduire de conversions `any` larges pour masquer les erreurs.
  - Ne pas modifier les invariants `RG-050` et `RG-064`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: la story retire une surface de code mort de typage (`@ts-nocheck`) et garde son absence.
- Behavior change allowed: no
- Behavior change constraints:
  - Le rendu et les workflows des composants listes doivent rester identiques.
  - Les changements sont limites au typage, aux tests et aux guards.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une suppression restante depend d'un choix produit ou d'un bug de typage tiers impossible a borner sans exception explicite.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | le guard executable devient source de verite de la regle `@ts-nocheck`. |
| Baseline Snapshot | yes | le scan avant/apres des directives est obligatoire pour prouver la fermeture. |
| Ownership Routing | no | aucun owner fonctionnel n'est deplace dans cette story. |
| Allowlist Exception | yes | toute suppression restante doit etre exacte, owned et expirante. |
| Contract Shape | no | aucun contrat API ou type public n'est change. |
| Batch Migration | no | la surface est une liste finie de fichiers F-002. |
| Reintroduction Guard | yes | le guard doit echouer pour les nouvelles suppressions non allowlistees. |
| Persistent Evidence | yes | les scans before/after et l'allowlist doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/component-architecture-guards.test.ts`, execute par `npm run test -- component-architecture`.
- Secondary evidence:
  - scan `rg -n '@ts-nocheck' frontend/src/components -g '*.ts' -g '*.tsx'`.
- Static scans alone are not sufficient for this story because:
  - le guard doit echouer automatiquement lors des regressions futures.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-114-supprimer-suppressions-typescript-composants/component-ts-nocheck-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-114-supprimer-suppressions-typescript-composants/component-ts-nocheck-after.md`
- Expected invariant:
  - zero `@ts-nocheck` sous `components`, ou uniquement des exceptions exactes avec owner, raison, exit condition et garde passante.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `component-architecture-allowlist.ts` | `@ts-nocheck` exact | exception temporaire | owner, raison, exit condition et commande |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before scan | `_condamad/stories/CS-114-supprimer-suppressions-typescript-composants/component-ts-nocheck-before.md` | prouver la surface initiale F-002 |
| after scan | `_condamad/stories/CS-114-supprimer-suppressions-typescript-composants/component-ts-nocheck-after.md` | prouver zero suppression ou exceptions exactes |
| exception register | `frontend/src/tests/component-architecture-allowlist.ts` | source executable des exceptions restantes |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- unallowlisted `@ts-nocheck` in `frontend/src/components/**/*.ts`
- unallowlisted `@ts-nocheck` in `frontend/src/components/**/*.tsx`
- Deterministic source: forbidden symbols scan plus AST guard.
- Deterministic source: AST guard in `frontend/src/tests/component-architecture-guards.test.ts`.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- component-architecture` checks component TypeScript suppressions.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md#F-002`
- Closure proof required: before/after scans, exact exception register when one remains, and failing guard for new suppressions.
- Known residual in-domain work: none
- Deferred non-domain concerns: page suppressions remain under `frontend-react-pages`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md` - `F-002` lists five files with `@ts-nocheck`.
- Evidence 2: `_condamad/audits/frontend-components/2026-05-08-2303/01-evidence-log.md` - `E-004` and `E-008` show the current guard gap.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

- The listed component files compile without `@ts-nocheck`, or exact temporary exceptions are guarded.
- New component-domain `@ts-nocheck` cannot be introduced silently.
- Lint and targeted tests remain passing.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-050` - architecture/design-system guard suite must stay exact and executable.
  - `RG-064` - page `@ts-nocheck` guardrails must not be weakened while adding component coverage.
- Non-applicable invariants:
  - `RG-047`, `RG-048`, `RG-068` - no style, fallback or layout hierarchy change is required.
- Required regression evidence:
  - `npm run test -- Form EnterpriseCredentialsPanel OpsMonitoringPanel SupportOpsPanel component-architecture`
  - `npm run lint`
  - targeted `@ts-nocheck` scan.
- Allowed differences:
  - Type annotations, helper types and exact exception metadata only.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before/after component `@ts-nocheck` scans are persisted. | Evidence profile: `baseline_before_after_diff`; `rg -n '@ts-nocheck' frontend/src/components`. |
| AC2 | Direct typing fixes are attempted for all five `F-002` files. | Evidence profile: `ast_architecture_guard`; `npm run test -- Form EnterpriseCredentialsPanel`. |
| AC3 | Any retained directive is exact in the exception register. | Evidence profile: `allowlist_register_validated`; `npm run test -- component-architecture`. |
| AC4 | New unallowlisted component `@ts-nocheck` fails the architecture suite. | Evidence profile: `reintroduction_guard`; `npm run test -- component-architecture`. |
| AC5 | Lint passes without TS config weakening. | Evidence profile: `frontend_typecheck_no_orphan`; AST guard, `npm run lint`, `rg -n '@ts-nocheck' frontend/src/components`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture baseline (AC: AC1)
  - [ ] Run and persist the targeted `@ts-nocheck` scan.
- [ ] Task 2 - Remove suppressions through typing fixes (AC: AC2, AC5)
  - [ ] Fix `EnterpriseCredentialsPanel.tsx`, `OpsMonitoringPanel.tsx`, `SupportOpsPanel.tsx`, `ui/Form/Form.tsx`, `ui/Form/Form.test.tsx`.
  - [ ] Avoid broad `any` and config weakening.
- [ ] Task 3 - Add exact guard and exception registry (AC: AC3, AC4)
  - [ ] Add/update component architecture allowlist and guard.
  - [ ] Ensure wildcard and folder exceptions fail.
- [ ] Task 4 - Persist after evidence and validate (AC: AC1, AC4, AC5)
  - [ ] Write after scan and run targeted tests/lint.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - existing component props/types where available.
  - existing architecture guard/test helpers under `frontend/src/tests`.
- Do not recreate:
  - local duplicate type models if a project type already exists.
  - separate suppression allowlist when component architecture allowlist can own it.
- Shared abstraction allowed only if:
  - the same typing helper is needed by multiple listed components.

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

- unallowlisted `@ts-nocheck` under `frontend/src/components/**`
- weakening `frontend/tsconfig.lint.json` or equivalent TS config
- broad `any` conversions whose only purpose is hiding the original error

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: directive required by a first-party production component after typed fix attempt and exact guard evidence.
- `external-active`: directive required only because an external library typing defect blocks compilation and has exact issue/risk evidence.
- `historical-facade`: directive exists only to preserve an old untyped component surface.
- `dead`: directive has no remaining technical need after typing fix.
- `needs-user-decision`: ambiguity remains after required scans and must block removal.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| each directive | TS directive | classify during implementation | owner file | typed code | keep/delete/replace-consumer/needs-user-decision | `rg`, `npm run lint` | type risk |

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Component type safety | typed component source plus component tests | unguarded `@ts-nocheck` directive |
| Temporary type exception | exact component architecture allowlist | broad TS config weakening |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/components/EnterpriseCredentialsPanel.tsx`
- `frontend/src/components/OpsMonitoringPanel.tsx`
- `frontend/src/components/SupportOpsPanel.tsx`
- `frontend/src/components/ui/Form/Form.tsx`
- `frontend/src/components/ui/Form/Form.test.tsx`
- `frontend/src/tests/page-architecture-allowlist.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/components/EnterpriseCredentialsPanel.tsx` - remove suppression through typing.
- `frontend/src/components/OpsMonitoringPanel.tsx` - remove suppression through typing.
- `frontend/src/components/SupportOpsPanel.tsx` - remove suppression through typing.
- `frontend/src/components/ui/Form/Form.tsx` - remove suppression through typing.
- `frontend/src/tests/component-architecture-allowlist.ts` - exact exceptions if unavoidable.
- `frontend/src/tests/component-architecture-guards.test.ts` - guard.

Likely tests:

- `frontend/src/components/ui/Form/Form.test.tsx` - remove suppression and keep coverage.
- `frontend/src/tests/component-architecture-guards.test.ts` - suppression guard.

Files not expected to change:

- `frontend/tsconfig.lint.json` - config must not be weakened.
- `backend/app/**` - backend not involved.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- Form EnterpriseCredentialsPanel OpsMonitoringPanel SupportOpsPanel component-architecture
npm run lint
rg -n '@ts-nocheck' src/components -g '*.ts' -g '*.tsx'
```

## 22. Regression Risks

- Risk: typings are fixed by hiding errors under broad `any`.
  - Guardrail: lint plus code review of changed type annotations.
- Risk: future component suppressions appear outside page guards.
  - Guardrail: component architecture guard with exact allowlist.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass the guard through wrapper, alias, fallback, config weakening or hidden broad `any`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work because this story is `full-closure`.

## 24. References

- `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md#F-002` - source finding.
- `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md#SC-002` - story candidate contract.
- `_condamad/stories/regression-guardrails.md` - regression invariants.
