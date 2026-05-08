# Story CS-096 decomposer-responsabilites-restantes-admin-prompts: Decomposer les responsabilites restantes de AdminPromptsPage

Status: ready-to-dev

## 1. Objective

Reduire `AdminPromptsPage.tsx` a un conteneur de route plus net.
Extraire une tranche coherente des responsabilites encore locales vers
`frontend/src/features/admin-prompts/**` ou vers les composants canoniques existants.
La story doit produire un inventaire before/after et resserrer l'exception de taille page.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-1024/03-story-candidates.md#SC-001`
- Reason for change: `F-001` indique que `AdminPromptsPage.tsx` reste une page de 2909 lignes avec helpers, modals, filtres, mutations et sections JSX extractibles.

## 3. Domain Boundary

- Domain: `frontend-react-pages/admin-prompts`
- In scope:
  - Inspecter et inventorier les responsabilites locales restantes de `AdminPromptsPage.tsx`.
  - Extraire au moins une tranche coherente du finite map audit.
  - Cibles possibles: modals, filtres catalogue, diff release, consommation, rollback archive, execution manuelle.
  - Reutiliser les owners existants `frontend/src/features/admin-prompts/**` et composants admin prompts deja presents.
  - Mettre a jour les tests AdminPrompts et l'allowlist page-size exacte.
- Out of scope:
  - Changer les contrats backend ou endpoints admin LLM.
  - Reconcevoir visuellement la page.
  - Migrer les appels API admin hors pages non lies a admin-prompts.
  - Traiter les autres pages oversized.
- Explicit non-goals:
  - Ne pas affaiblir `RG-064` sur l'architecture des pages React.
  - Ne pas rouvrir les surfaces design-system protegees par `RG-044` a `RG-063`.
  - Ne pas creer de wrapper, re-export, alias ou facade de compatibilite depuis `AdminPromptsPage.tsx`.
  - Ne pas accepter de wildcard ou exception dossier pour `PAGE_SIZE_EXCEPTIONS`.

## 4. Operation Contract

- Operation type: split
- Primary archetype: ownership-routing-refactor
- Archetype reason: la story deplace des responsabilites feature/UI hors d'une page route vers leurs owners canoniques.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une extraction exige un changement produit, un libelle nouveau, ou un contrat backend/API non inferable.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le guard AST `page-architecture` est la source executable de la politique page-size et dette page. |
| Baseline Snapshot | yes | La reduction du monolithe et de l'exception page-size doit etre prouvee before/after. |
| Ownership Routing | yes | Objet principal: router les responsabilites admin-prompts vers owners canoniques. |
| Allowlist Exception | yes | `PAGE_SIZE_EXCEPTIONS` doit etre resserree ou justifiee exactement. |
| Contract Shape | no | Aucun payload API ou type public backend n'est change. |
| Batch Migration | no | Une tranche coherente est extraite, pas une migration multi-domaines. |
| Reintroduction Guard | yes | La page ne doit pas regagner les responsabilites migrees ni `@ts-nocheck`. |
| Persistent Evidence | yes | Les inventaires before/after doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/page-architecture-guards.test.ts`.
  - allowlist exacte in `frontend/src/tests/page-architecture-allowlist.ts`.
- Secondary evidence:
  - `npm run test -- page-architecture`
  - targeted AdminPrompts Vitest tests.
- Static scans alone are not sufficient because:
  - the route page size policy and forbidden page debt must fail deterministically during Vitest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-before.md`.
- Comparison after implementation: `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-after.md`.
- Required baseline content: line count, `PAGE_SIZE_EXCEPTIONS` entry, inventory of local helpers/components/state/mutations/sections targeted by this tranche.
- Expected invariant: every extracted responsibility has one canonical owner and no duplicate active copy remains in `AdminPromptsPage.tsx`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin prompts feature helpers and projections | `frontend/src/features/admin-prompts/**` | local helper blocks in `AdminPromptsPage.tsx` |
| Prompt editor/catalog modal UI | existing admin prompt components or feature components | local modal component definitions in the page |
| Catalog filters and section orchestration | feature hook/component under `frontend/src/features/admin-prompts/**` | page-local state/action cluster |
| Route composition | `frontend/src/pages/admin/AdminPromptsPage.tsx` | feature/business ownership in route page |

Rules:
- classify each retained local responsibility as route-only or extractable;
- extracted code must be imported from canonical owner, not re-exported from the page;
- no duplicate helper with old name may remain unless it is the canonical owner.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/page-architecture-allowlist.ts` | `PAGE_SIZE_EXCEPTIONS` | temporary route size exception | remove or narrow after this tranche |

Rules:
- no wildcard;
- no folder-wide exception;
- no `PASS with limitation`;
- no exception may grow as part of this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: this is a bounded ownership slice; the remaining closure map is declared in Source Finding Closure.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-before.md` | Capturer taille, exception et responsabilites. |
| After inventory | `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-after.md` | Prouver owners finaux, taille et exception resserree. |
| Final validation | `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/generated/10-final-evidence.md` | Persister les validations. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: `npm run test -- page-architecture` must keep `AdminPromptsPage.tsx` exact and must fail if forbidden page debt returns.
- Deterministic source: `frontend/src/tests/page-architecture-guards.test.ts` and `frontend/src/tests/page-architecture-allowlist.ts`.
- Required forbidden examples: `@ts-nocheck`, `@ts-ignore`, copied extracted component/helper in the page, broad page-size exception.
- Guard evidence: targeted tests plus scans under `frontend/src/pages/admin/AdminPromptsPage.tsx` and `frontend/src/features/admin-prompts`.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md#F-001`
- Closure proof required: before/after inventory, line-count delta, tightened `PAGE_SIZE_EXCEPTIONS`, page-architecture and AdminPrompts tests.
- Known residual in-domain work: finite-map items not selected in this tranche.
- Remaining closure map: `admin-prompts-after.md` must classify each item as `extracted`, `route-only`, or `remaining-next-slice`.
- Stop condition: the page-size exception is removed or narrowed to a permanent route-container rationale with no known extractable feature/UI slice left.
- Deferred non-domain concerns: none.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md#E-004` - `AdminPromptsPage.tsx` has 2909 lines.
- Evidence 2: `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md#E-005` - the page still owns helpers, modals, state, mutations and large JSX sections.
- Evidence 3: `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md#E-014` - no TS bypass remains in target files.
- Evidence 4: `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/00-story.md` - prior extraction started the feature owner.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

- `AdminPromptsPage.tsx` composes route-level layout and imports the extracted tranche from canonical owners.
- The selected tranche has no duplicate active implementation in the page.
- `PAGE_SIZE_EXCEPTIONS` is reduced or carries a tighter route-container rationale.
- Admin prompts route, catalog and flow tests still pass.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page architecture exceptions for size and forbidden page debt must remain exact.
  - `RG-047` - CSS movement, if any, must not introduce static inline styles.
  - `RG-049` - extracted markup must not reintroduce legacy style surfaces.
- Non-applicable invariants:
  - `RG-054` - no admin route redirect is changed.
  - `RG-053` - no runtime payload compatibility is changed.
- Required regression evidence:
  - `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow page-architecture`
  - `npm run lint`
  - targeted scans for `@ts-nocheck`, `@ts-ignore`, `apiFetch(` in the edited admin-prompts surface.
- Allowed differences:
  - File ownership and line count changes from the selected extraction tranche only.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before inventory records the selected finite-map item. | `rg -n "line-count|selected-finite-map-item" _condamad/stories/CS-096*/admin-prompts-before.md`. |
| AC2 | After inventory records the extracted owner path. | `rg -n "extracted-owner-path" _condamad/stories/CS-096*/admin-prompts-after.md`. |
| AC3 | `PAGE_SIZE_EXCEPTIONS` is removed or narrowed exactly. | Evidence profile: `allowlist_register_validated`; `npm run test -- page-architecture`. |
| AC4 | AdminPrompts behavior remains covered. | Evidence profile: `runtime_behavior`; `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow`. |
| AC5 | No forbidden TS/API debt is introduced. | AST guard; `npm run test -- page-architecture`; `rg -n "@ts-nocheck\|@ts-ignore\|apiFetch\\(" frontend/src/pages/admin`. |
| AC6 | After inventory records page absence proof. | `rg -n "page-absence-proof" _condamad/stories/CS-096*/admin-prompts-after.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture the before inventory and choose the tranche. (AC: AC1)
- [ ] Task 2 - Extract the selected responsibility to the canonical owner without changing behavior. (AC: AC2, AC4, AC6)
  - [ ] Record `extracted-owner-path` and `page-absence-proof` in `admin-prompts-after.md`.
- [ ] Task 3 - Update imports, tests and CSS ownership only where the extracted component requires it. (AC: AC2, AC4, AC5)
- [ ] Task 4 - Tighten `PAGE_SIZE_EXCEPTIONS` and document the remaining closure map. (AC: AC1, AC3)
- [ ] Task 5 - Run validation and persist final evidence. (AC: AC3, AC4, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/features/admin-prompts/**` for feature ownership.
- Reuse existing admin prompt components when they are the owner.
- Do not recreate API hooks already available in `frontend/src/api/adminPrompts.ts`.
- Shared abstraction allowed only if it removes an actual duplicate from the selected tranche.

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
- `@ts-nocheck` and `@ts-ignore` in admin-prompts page/feature files.
- `apiFetch(` in `AdminPromptsPage.tsx`.
- wildcard or folder-wide `PAGE_SIZE_EXCEPTIONS`.
- re-exporting extracted owners from `AdminPromptsPage.tsx`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin prompts route shell | `frontend/src/pages/admin/AdminPromptsPage.tsx` | feature helpers and modal internals in page |
| Admin prompts API contracts | `frontend/src/api/adminPrompts.ts` | page-local endpoint construction |
| Admin prompts feature UI/state | `frontend/src/features/admin-prompts/**` or existing named admin prompt components | duplicated JSX/state in page |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-react-pages/2026-05-08-1024/00-audit-report.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md`
- `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/00-story.md`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/features/admin-prompts/**`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/pages/admin/AdminPromptsPage.tsx` - remove selected local responsibility and compose canonical owner.
- `frontend/src/features/admin-prompts/**` - add or extend canonical owner for selected tranche.
- `frontend/src/pages/admin/AdminPromptsPage.css` - only if extracted JSX needs class ownership movement.
- `frontend/src/tests/page-architecture-allowlist.ts` - narrow or remove page-size exception.

Likely tests:
- `frontend/src/tests/AdminPromptsPage.test.tsx` - behavior coverage for selected tranche.
- `frontend/src/tests/AdminPromptsRouting.test.tsx` - route continuity.
- `frontend/src/tests/AdminPromptsCatalogFlow.test.tsx` - catalog flow continuity if tranche touches catalog.
- `frontend/src/tests/page-architecture-guards.test.ts` - guard remains green.

Files not expected to change:
- `backend/**` - no backend contract change.
- `frontend/src/api/adminPrompts.ts` - not expected unless extracted tranche proves an existing API helper is missing.
- `frontend/package.json` - existing scripts are sufficient.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow page-architecture
rg -n "@ts-nocheck|@ts-ignore|apiFetch\\(" src/pages/admin/AdminPromptsPage.tsx src/features/admin-prompts
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: extraction changes route behavior or local state timing.
  - Guardrail: AdminPrompts targeted tests and no behavior change allowed.
- Risk: page-size exception remains broad.
  - Guardrail: AC3 requires exact narrowing/removal and `page-architecture`.
- Risk: duplicate owner appears in page and feature.
  - Guardrail: ownership inventory and targeted scans.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not create compatibility shims, aliases, fallbacks, wrappers or re-exports.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-1024/03-story-candidates.md#SC-001`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md#F-001`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md`
- `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/00-story.md`
- `_condamad/stories/regression-guardrails.md`
