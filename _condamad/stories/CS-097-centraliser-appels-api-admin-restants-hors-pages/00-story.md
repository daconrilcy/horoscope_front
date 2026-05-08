# Story CS-097 centraliser-appels-api-admin-restants-hors-pages: Centraliser les appels API admin restants hors pages

Status: ready-to-dev

## 1. Objective

Fermer completement les exceptions `apiFetch(` restantes dans les pages admin.
Deplacer contrats, URL builders, parsing et erreurs vers des owners canoniques sous `frontend/src/api/**`.
Apres implementation, aucune page React ne doit appeler `apiFetch(` directement.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-1024/03-story-candidates.md#SC-002`
- Reason for change: `F-002` montre quatre pages admin encore proprietaires d'appels API directs malgre la centralisation partielle livree par CS-091.

## 3. Domain Boundary

- Domain: `frontend-react-pages/admin-api`
- In scope:
  - Migrer les appels directs de `AdminAiGenerationsPage.tsx`, `AdminEntitlementsPage.tsx`, `AdminSettingsPage.tsx`, `AdminSupportPage.tsx`.
  - Creer ou etendre des modules API canoniques sous `frontend/src/api/**`.
  - Preserver loading, error et empty states actuels.
  - Retirer toutes les entrees `DIRECT_API_PAGE_EXCEPTIONS`.
- Out of scope:
  - Modifier les endpoints backend.
  - Changer la forme fonctionnelle visible des pages admin.
  - Refactorer les pages admin non listees.
  - Toucher aux API prompt/admin deja centralisees sauf reuse strict.
- Explicit non-goals:
  - Ne pas affaiblir `RG-064` sur les appels API directs dans les pages.
  - Ne pas garder une exception residuelle ou `PASS with limitation`.
  - Ne pas ajouter de shim, fallback, alias ou wrapper de compatibilite dans les pages.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: service-boundary-refactor
- Archetype reason: les pages cessent d'appeler le client HTTP bas niveau et consomment des services/API owners canoniques.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: un endpoint ou payload ne peut pas etre inferable depuis le comportement actuel, les tests existants ou les contrats API frontend deja presents.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le guard AST `page-architecture` devient la source executable de l'absence d'appels API directs en pages. |
| Baseline Snapshot | yes | Il faut prouver les quatre hits before et zero hit after sous `frontend/src/pages`. |
| Ownership Routing | yes | Les responsabilites endpoint/parsing quittent les pages vers `frontend/src/api/**`. |
| Allowlist Exception | yes | L'allowlist `DIRECT_API_PAGE_EXCEPTIONS` doit devenir vide, sans wildcard. |
| Contract Shape | yes | Les types de reponse/requete admin doivent etre explicites dans les modules API. |
| Batch Migration | no | Le lot est fini et exact: quatre pages, fermeture complete. |
| Reintroduction Guard | yes | `page-architecture` doit echouer si un appel direct revient. |
| Persistent Evidence | yes | Les scans before/after et validations doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/page-architecture-guards.test.ts`.
  - allowlist exacte in `frontend/src/tests/page-architecture-allowlist.ts`.
- Secondary evidence:
  - `npm run test -- page-architecture`
  - zero-hit direct API scan in `frontend/src/pages`.
- Static scans alone are not sufficient because:
  - the architecture rule must fail deterministically in Vitest if direct `apiFetch(` is reintroduced.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-097-centraliser-appels-api-admin-restants-hors-pages/admin-api-before.md`.
- Comparison after implementation: `_condamad/stories/CS-097-centraliser-appels-api-admin-restants-hors-pages/admin-api-after.md`.
- Required baseline content: output de `rg -n "apiFetch\\(" frontend/src/pages -g "*.tsx"` et contenu des entrees `DIRECT_API_PAGE_EXCEPTIONS`.
- Expected invariant: zero `apiFetch(` sous `frontend/src/pages` et allowlist directe vide.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin AI generation metrics | `frontend/src/api/**` admin AI owner | `AdminAiGenerationsPage.tsx` direct `apiFetch` |
| Admin entitlement matrix/update | `frontend/src/api/**` entitlement owner | `AdminEntitlementsPage.tsx` direct `apiFetch` |
| Admin settings exports | `frontend/src/api/**` settings/export owner | `AdminSettingsPage.tsx` direct `apiFetch` |
| Admin support tickets/content | `frontend/src/api/**` support owner | `AdminSupportPage.tsx` direct `apiFetch` |

Rules:
- endpoint construction, response parsing and error normalization live outside pages;
- pages may call typed functions/hooks only;
- no API owner may be duplicated if an existing module already owns the endpoint family.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/page-architecture-allowlist.ts` | `DIRECT_API_PAGE_EXCEPTIONS` | four known direct API page exceptions from audit | must be empty after this story |

Rules:
- no wildcard;
- no folder-wide exception;
- no residual exception for full closure;
- no `PASS with limitation`, hidden residual implementation work, shim, alias, compatibility or migration-only state.

## 4f. Contract Shape

Contract type:
- frontend admin API functions and response/request TypeScript types.
Fields:
- exact fields currently consumed by the four pages.
Required fields:
- every field dereferenced by the pages after migration.
Optional fields:
- only fields already treated as optional/nullish by current page behavior.
Status codes:
- preserve current success/error handling; do not invent backend status changes.
Serialization names:
- preserve current endpoint parameter names such as `period`, `status`, `planId`, `featureId`, and export `type`.
Frontend type impact:
- pages import typed API functions/results instead of `apiFetch` and local response parsing.
Generated contract impact:
- none expected; stop if generated API client/schema changes are required.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: although four files are migrated, this is a finite full-closure service-boundary refactor with exact files rather than an open batch program.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before direct API inventory | `_condamad/stories/CS-097-centraliser-appels-api-admin-restants-hors-pages/admin-api-before.md` | Capturer les quatre pages et allowlist initiale. |
| After direct API inventory | `_condamad/stories/CS-097-centraliser-appels-api-admin-restants-hors-pages/admin-api-after.md` | Prouver zero hit pages et allowlist vide. |
| Final validation | `_condamad/stories/CS-097-centraliser-appels-api-admin-restants-hors-pages/generated/10-final-evidence.md` | Persister commandes sans limitation. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: `npm run test -- page-architecture` must fail for any `apiFetch(` under `frontend/src/pages`.
- Deterministic source: `frontend/src/tests/page-architecture-guards.test.ts` and `DIRECT_API_PAGE_EXCEPTIONS`.
- Required forbidden examples: direct `apiFetch(` in `.tsx` pages, local endpoint builders in pages for migrated endpoints, broad allowlist entry.
- Guard evidence: `npm run test -- page-architecture` and zero-hit `rg`.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md#F-002`
- Closure proof required: before/after direct API scan, empty `DIRECT_API_PAGE_EXCEPTIONS`, exact page/API tests, `npm run test -- page-architecture`.
- Known residual in-domain work: none.
- Deferred non-domain concerns: none.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md#E-006` - direct `apiFetch(` remains in four admin pages.
- Evidence 2: `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md#E-007` - page-architecture allowlist tracks the exact remaining exceptions.
- Evidence 3: `_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/00-story.md` - prior story established the owner pattern.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

- `frontend/src/pages/**/*.tsx` contains zero direct `apiFetch(` calls.
- The four admin pages consume typed API owner functions/hooks.
- `DIRECT_API_PAGE_EXCEPTIONS` is empty and guarded.
- Loading, error and empty states remain equivalent.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - direct API calls in pages are part of the protected page architecture surface.
  - `RG-053` - frontend runtime compatibility must not be preserved via hidden mappers/fallbacks.
- Non-applicable invariants:
  - `RG-054` - no admin redirect route is touched.
  - `RG-047` - no inline style surface is touched.
- Required regression evidence:
  - `npm run test -- page-architecture AdminAiGenerationsPage AdminEntitlementsPage AdminSettingsPage AdminSupportPage`
  - `npm run lint`
  - `rg -n "apiFetch\\(" frontend/src/pages -g "*.tsx"` returns zero hits.
- Allowed differences:
  - API ownership moves from pages to `frontend/src/api/**`; visible behavior unchanged.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before inventory lists direct API pages. | AST guard; `rg -n "apiFetch\\(" frontend/src/pages -g "*.tsx"`; `npm run test -- page-architecture`. |
| AC2 | Each migrated endpoint family has a canonical typed API owner. | AST guard; `npm run test -- page-architecture`; exact tests listed in section 19. |
| AC3 | Pages contain zero direct `apiFetch(` calls. | `rg -n "apiFetch\\(" frontend/src/pages -g "*.tsx"`. |
| AC4 | `DIRECT_API_PAGE_EXCEPTIONS` is empty. | Evidence profile: `reintroduction_guard`; `npm run test -- page-architecture`. |
| AC5 | Loading/error/empty behavior remains covered. | `npm run test -- AdminAiGenerationsPage AdminEntitlementsPage AdminSettingsPage AdminSupportPage`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture before scan and map each page call to endpoint family. (AC: AC1)
- [ ] Task 2 - Create or extend canonical API owner modules with typed request/response functions. (AC: AC2)
- [ ] Task 3 - Replace page-local `apiFetch` usage with canonical owner calls while preserving states. (AC: AC3, AC5)
- [ ] Task 4 - Empty `DIRECT_API_PAGE_EXCEPTIONS` and keep guard exact. (AC: AC4)
- [ ] Task 5 - Run validation and persist after evidence. (AC: AC3, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/api/client.ts` only from API owner modules.
- Reuse existing admin API modules such as `adminDashboard.ts`, `adminLogs.ts`, `adminUsers.ts`, `adminPrompts.ts`, or create similarly scoped modules only when no owner exists.
- Do not duplicate endpoint URL construction in pages.
- Shared abstraction allowed only if at least two migrated endpoint families need the same parsing/error behavior.

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
- `apiFetch(` in `frontend/src/pages/**/*.tsx`.
- non-empty `DIRECT_API_PAGE_EXCEPTIONS`.
- page-local endpoint builder for the four migrated admin domains.
- `PASS with limitation`, broad allowlists, wildcard exceptions, unclassified fallback, compatibility, legacy, migration-only, shim, alias, TODO, or hidden residual in-domain work.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| HTTP client primitive | `frontend/src/api/client.ts` | pages |
| Admin API endpoint owners | `frontend/src/api/**` exact modules | `frontend/src/pages/admin/*.tsx` direct calls |
| Page presentation/state | four admin page components | endpoint construction and raw response parsing |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected unless endpoint ambiguity blocks the story.

## 18. Files to Inspect First

- `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md`
- `_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/00-story.md`
- `frontend/src/pages/admin/AdminAiGenerationsPage.tsx`
- `frontend/src/pages/admin/AdminEntitlementsPage.tsx`
- `frontend/src/pages/admin/AdminSettingsPage.tsx`
- `frontend/src/pages/admin/AdminSupportPage.tsx`
- `frontend/src/api/**`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/pages/admin/AdminAiGenerationsPage.tsx` - consume canonical API owner.
- `frontend/src/pages/admin/AdminEntitlementsPage.tsx` - consume canonical API owner.
- `frontend/src/pages/admin/AdminSettingsPage.tsx` - consume canonical API owner.
- `frontend/src/pages/admin/AdminSupportPage.tsx` - consume canonical API owner.
- `frontend/src/api/**` - add or extend exact admin API owners.
- `frontend/src/tests/page-architecture-allowlist.ts` - empty direct API page exceptions.

Likely tests:
- `frontend/src/tests/page-architecture-guards.test.ts` - guard still green with empty allowlist.
- `frontend/src/tests/AdminAiGenerationsPage.test.tsx` - create if absent; cover loading, success, error, empty state.
- `frontend/src/tests/AdminEntitlementsPage.test.tsx` - create if absent; cover loading, success, error, empty state.
- `frontend/src/tests/AdminSettingsPage.test.tsx` - extend existing export behavior coverage.
- `frontend/src/tests/AdminSupportPage.test.tsx` - create if absent; cover tickets and flagged content states.
- New API owner tests under `frontend/src/tests/*Api.test.ts` when page tests do not prove parsing/error behavior.

Files not expected to change:
- `backend/**` - endpoint contracts are not changed.
- `frontend/package.json` - existing scripts are sufficient.
- `frontend/src/api/client.ts` - no client primitive change expected.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- page-architecture AdminAiGenerationsPage AdminEntitlementsPage AdminSettingsPage AdminSupportPage
rg -n "apiFetch\\(" src/pages -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-097-centraliser-appels-api-admin-restants-hors-pages/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: API owner changes response interpretation.
  - Guardrail: typed contract plus exact page/API tests listed in section 19.
- Risk: direct calls remain through allowlist.
  - Guardrail: full-closure AC forbids residual exceptions.
- Risk: endpoint ambiguity causes guessed contract.
  - Guardrail: explicit blocker condition.

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

- `_condamad/audits/frontend-react-pages/2026-05-08-1024/03-story-candidates.md#SC-002`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md#F-002`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md`
- `_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/00-story.md`
- `_condamad/stories/regression-guardrails.md`
