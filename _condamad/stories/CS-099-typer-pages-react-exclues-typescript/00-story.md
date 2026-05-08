# Story CS-099 typer-pages-react-exclues-typescript: Typer les pages React encore exclues de TypeScript

Status: ready-to-dev

## 1. Objective

Lever les trois derniers bypass `// @ts-nocheck` presents dans `frontend/src/pages/**`.
Typer props, route params, donnees API et handlers sans affaiblir TypeScript.
Apres implementation, `TS_NOCHECK_PAGE_EXCEPTIONS` doit etre vide.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-1024/03-story-candidates.md#SC-004`
- Reason for change: `F-004` montre que trois pages restent exclues de TypeScript: `AstrologerProfilePage.tsx`, `ConsultationResultPage.tsx`, `NotFoundPage.tsx`.

## 3. Domain Boundary

- Domain: `frontend-react-pages/type-safety`
- In scope:
  - Lever `// @ts-nocheck` dans les trois pages exactes.
  - Typer les donnees, params, props, state, events et helpers necessaires.
  - Retirer les entrees `TS_NOCHECK_PAGE_EXCEPTIONS`.
  - Ajouter ou adapter des tests cibles si le typage revele une zone non couverte.
- Out of scope:
  - Modifier les payloads backend/API.
  - Refonte UI des pages.
  - Retirer `@ts-nocheck` hors `frontend/src/pages/**`.
  - Modifier `tsconfig.lint.json` pour contourner les erreurs.
- Explicit non-goals:
  - Ne pas affaiblir `RG-064` sur les exceptions `@ts-nocheck`.
  - Ne pas introduire `@ts-ignore`, `@ts-expect-error` non justifie, ou `any` large.
  - Ne pas creer de type wrapper de compatibilite pour masquer un contrat ambigu.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story ferme les exceptions de typage gardees par page-architecture et durcit l'absence de bypass TypeScript dans les pages.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le typage necessite de changer une forme de payload API non couverte par les contrats frontend actuels ou les tests existants.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `npm run lint` et `page-architecture` deviennent la preuve executable d'absence de bypass page. |
| Baseline Snapshot | yes | Le scan before/after des trois `@ts-nocheck` est requis pour fermeture complete. |
| Ownership Routing | no | La story type les pages exactes sans deplacer de responsabilites feature. |
| Allowlist Exception | yes | `TS_NOCHECK_PAGE_EXCEPTIONS` doit devenir vide. |
| Contract Shape | yes | Les types de payload/params consommes par les pages doivent etre explicites sans changer leur shape. |
| Batch Migration | no | Lot fini de trois fichiers exacts. |
| Reintroduction Guard | yes | Le guard doit echouer si `@ts-nocheck` revient sous pages. |
| Persistent Evidence | yes | Les scans et validations finales doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - TypeScript lint via `npm run lint`.
  - AST guard in `frontend/src/tests/page-architecture-guards.test.ts`.
- Secondary evidence:
  - zero-hit scan `rg -n "@ts-nocheck|@ts-ignore" frontend/src/pages -g "*.tsx"`.
- Static scans alone are not sufficient because:
  - TypeScript doit prouver que les pages restent compilees/type-checkees sans bypass.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-099-typer-pages-react-exclues-typescript/type-safety-before.md`.
- Comparison after implementation: `_condamad/stories/CS-099-typer-pages-react-exclues-typescript/type-safety-after.md`.
- Required baseline content: scan `@ts-nocheck`, `TS_NOCHECK_PAGE_EXCEPTIONS`, and any page-specific typing assumptions.
- Expected invariant: zero `@ts-nocheck` under `frontend/src/pages` and empty exception list.

## 4d. Ownership Routing Rule

- Ownership Routing Rule: not applicable
- Reason: the story does not move feature ownership; it removes exact TypeScript bypasses in existing page owners.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/page-architecture-allowlist.ts` | `TS_NOCHECK_PAGE_EXCEPTIONS` | three typed-debt page exceptions from audit | must be empty after this story |

Rules:
- no wildcard;
- no folder-wide exception;
- no residual exception for full closure;
- no `PASS with limitation`.

## 4f. Contract Shape

Contract type:
- frontend TypeScript types for route params, API values, component props, state, and DOM event handlers.
Fields:
- fields already read by `AstrologerProfilePage.tsx`, `ConsultationResultPage.tsx`, `NotFoundPage.tsx`.
Required fields:
- fields dereferenced without nullish handling in current behavior.
Optional fields:
- values currently handled as optional, nullable, missing, or route-dependent.
Status codes:
- preserve existing API error handling in pages that fetch or display API-backed data.
Serialization names:
- preserve current API/route names; do not rename payload fields.
Frontend type impact:
- replace implicit unchecked values with local or imported exact types.
Generated contract impact:
- none expected; stop if generated contract change is required.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: the story handles a finite exact set of three page files and closes the exception list.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before type inventory | `_condamad/stories/CS-099-typer-pages-react-exclues-typescript/type-safety-before.md` | Capturer les trois hits et allowlist initiale. |
| After type inventory | `_condamad/stories/CS-099-typer-pages-react-exclues-typescript/type-safety-after.md` | Prouver zero hit et allowlist vide. |
| Final validation | `_condamad/stories/CS-099-typer-pages-react-exclues-typescript/generated/10-final-evidence.md` | Persister lint/tests/scans finaux. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: `npm run test -- page-architecture` must fail if a page contains a TS bypass.
- Deterministic source: `frontend/src/tests/page-architecture-guards.test.ts` and `TS_NOCHECK_PAGE_EXCEPTIONS`.
- Required forbidden examples: `// @ts-nocheck`, `@ts-ignore`, broad `any`, tsconfig weakening.
- Guard evidence: lint, page-architecture, and zero-hit scan.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md#F-004`
- Closure proof required: before/after scan, empty `TS_NOCHECK_PAGE_EXCEPTIONS`, `npm run lint`, `page-architecture`, exact page tests.
- Known residual in-domain work: none.
- Deferred non-domain concerns: none.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md#E-013` - three page hits remain.
- Evidence 2: `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md#E-007` - page-architecture allowlist tracks exact `@ts-nocheck` page exceptions.
- Evidence 3: `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md#E-011` - `npm run test -- page-architecture` currently passes with guarded exceptions.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

- The three pages type-check without `@ts-nocheck`.
- `frontend/src/pages/**/*.tsx` contains zero `@ts-nocheck` and zero `@ts-ignore`.
- `TS_NOCHECK_PAGE_EXCEPTIONS` is empty.
- Page behavior and route rendering remain unchanged.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - `@ts-nocheck` page exceptions are an exact protected page-architecture surface.
  - `RG-053` - typing must not preserve hidden compatibility payload handling.
- Non-applicable invariants:
  - `RG-054` - no admin redirects or aliases are touched.
  - `RG-047` - no inline style policy is touched unless incidental page code inspection proves otherwise.
- Required regression evidence:
  - `npm run lint`
  - `npm run test -- page-architecture AstrologerProfilePage ConsultationResultPage NotFoundPage`
  - `rg -n "@ts-nocheck|@ts-ignore" frontend/src/pages -g "*.tsx"` returns zero hits.
- Allowed differences:
  - Type annotations, exact local types, and tests only; no visible behavior change.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before inventory captures page TS bypasses. | `rg -n "@ts-nocheck" frontend/src/pages -g "*.tsx"`; `npm run test -- page-architecture`. |
| AC2 | The three audited pages compile without `@ts-nocheck`. | Evidence profile: `typecheck_lint`; `npm run lint`. |
| AC3 | No page contains TS bypass markers. | `rg -n "@ts-nocheck\|@ts-ignore" frontend/src/pages -g "*.tsx"`. |
| AC4 | `TS_NOCHECK_PAGE_EXCEPTIONS` is empty. | Evidence profile: `reintroduction_guard`; `npm run test -- page-architecture`. |
| AC5 | Existing route/page behavior remains covered. | AST guard; `npm run test -- AstrologersPage ConsultationMigration ConsultationReconnection NotFoundPage`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture before type inventory and inspect current unchecked assumptions. (AC: AC1)
- [ ] Task 2 - Type `AstrologerProfilePage.tsx` without changing payload shape or UI behavior. (AC: AC2, AC3, AC5)
- [ ] Task 3 - Type `ConsultationResultPage.tsx` without changing payload shape or UI behavior. (AC: AC2, AC3, AC5)
- [ ] Task 4 - Type `NotFoundPage.tsx` and remove the exception list entries. (AC: AC2, AC3, AC4)
- [ ] Task 5 - Run lint, page-architecture and exact page tests; persist after evidence. (AC: AC3, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse existing API/domain frontend types where present before declaring local equivalents.
- Reuse route and i18n helper types already used in neighboring pages.
- Do not duplicate broad payload interfaces if a canonical API module exports the shape.
- Shared type extraction is allowed only when at least two edited pages or an existing owner need the same type.

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
- `// @ts-nocheck` in `frontend/src/pages/**/*.tsx`.
- `@ts-ignore` in `frontend/src/pages/**/*.tsx`.
- broad `any` or `unknown as X` assertions used to bypass actual typing.
- changes to `tsconfig.lint.json` that weaken checks.
- non-empty `TS_NOCHECK_PAGE_EXCEPTIONS`.
- `PASS with limitation`, broad allowlists, wildcard exceptions, compatibility, shim, alias, TODO, or hidden residual in-domain work.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Page type safety guard | `frontend/src/tests/page-architecture-guards.test.ts` | manual audit only |
| `@ts-nocheck` exception list | `frontend/src/tests/page-architecture-allowlist.ts` | inline page bypass |
| Page-specific UI behavior | the three page components | broad unchecked payloads |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md`
- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/pages/NotFoundPage.tsx`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- Existing tests matching `AstrologerProfilePage`, `ConsultationResultPage`, `NotFoundPage`.

## 19. Expected Files to Modify

Likely files:
- `frontend/src/pages/AstrologerProfilePage.tsx` - remove `@ts-nocheck` and add exact typing.
- `frontend/src/pages/ConsultationResultPage.tsx` - remove `@ts-nocheck` and add exact typing.
- `frontend/src/pages/NotFoundPage.tsx` - remove `@ts-nocheck` and add exact typing.
- `frontend/src/tests/page-architecture-allowlist.ts` - empty `TS_NOCHECK_PAGE_EXCEPTIONS`.

Likely tests:
- `frontend/src/tests/page-architecture-guards.test.ts` - guard still green.
- `frontend/src/tests/AstrologersPage.test.tsx` - existing coverage for `AstrologerProfilePage`.
- `frontend/src/tests/ConsultationMigration.test.tsx` - existing coverage for `ConsultationResultPage`.
- `frontend/src/tests/ConsultationReconnection.test.tsx` - existing coverage for `ConsultationResultPage`.
- `frontend/src/tests/NotFoundPage.test.tsx` - create if no existing NotFound route behavior test exists.

Files not expected to change:
- `backend/**` - no backend contract change.
- `frontend/tsconfig.lint.json` - must not be weakened.
- `frontend/package.json` - existing scripts are sufficient.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- page-architecture AstrologerProfilePage ConsultationResultPage NotFoundPage
rg -n "@ts-nocheck|@ts-ignore" src/pages -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-099-typer-pages-react-exclues-typescript/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: typing changes null/empty branch behavior.
  - Guardrail: exact page tests listed in section 19 and no behavior change allowed.
- Risk: bypass moves from `@ts-nocheck` to `any` assertions.
  - Guardrail: AC3 and diff review.
- Risk: API payload ambiguity causes invented type.
  - Guardrail: explicit blocker on unsupported payload shape changes.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not create compatibility shims, aliases, fallbacks, wrappers or re-exports.
- Do not accept limitation, broad allowlists, wildcard exceptions, compatibility, shim, alias, TODO, or hidden residual work.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-1024/03-story-candidates.md#SC-004`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md#F-004`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md`
- `_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/00-story.md`
- `_condamad/stories/regression-guardrails.md`
