# Story CS-098 classer-centraliser-helpers-formatage-pages: Classer et centraliser les helpers de formatage encore dupliques

Status: ready-to-dev

## 1. Objective

Classer les definitions locales restantes de `formatDate`, `formatPrice` et `getErrorMessage`.
Centraliser uniquement les comportements reellement dupliques sous un owner canonique.
Les helpers conserves localement doivent etre justifies comme one-off page-specific.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-1024/03-story-candidates.md#SC-003`
- Reason for change: `F-003` montre que des helpers date/prix/erreur restent dupliques dans plusieurs pages.

## 3. Domain Boundary

- Domain: `frontend-react-pages/page-helpers`
- In scope:
  - Inventorier les helpers locaux `formatDate`, `formatPrice`, `getErrorMessage`.
  - Centraliser les comportements partages avérés.
  - Classer les helpers conserves avec raison et preuve de non-duplication.
  - Ajouter/adapter les tests de helpers canoniques.
- Out of scope:
  - Changer le copy produit ou les formats visibles sans preuve de comportement equivalent.
  - Refactorer des composants non lies aux helpers cibles.
  - Migrer les appels API admin ou les exceptions `@ts-nocheck`.
- Explicit non-goals:
  - Ne pas affaiblir `RG-064` sur l'architecture des pages.
  - Ne pas rouvrir les compatibilites runtime interdites par `RG-053`.
  - Ne pas creer de wrapper avec ancien nom si ce wrapper n'est pas l'owner canonique.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: ownership-routing-refactor
- Archetype reason: les helpers partages quittent les pages vers un owner utilitaire ou feature canonique.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: deux helpers formattent des concepts produit differents et exigent un copy UI distinct.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | Aucun runtime API/route n'est modifie. |
| Baseline Snapshot | yes | Il faut comparer l'inventaire des helpers before/after. |
| Ownership Routing | yes | Les helpers partages doivent avoir un owner canonique. |
| Allowlist Exception | yes | L'archetype active ce contrat; aucune exception large n'est admise et les helpers retenus doivent etre classes exactement. |
| Contract Shape | no | Aucun contrat API ou DTO n'est change. |
| Batch Migration | no | La story classe un lot fini de helpers cibles. |
| Reintroduction Guard | yes | Les duplications partagees ne doivent pas revenir sans classification. |
| Persistent Evidence | yes | Classification before/after obligatoire pour eviter les micro-stories repetitives. |

## 4b. Runtime Source of Truth

- Runtime Source of Truth: not applicable
- Reason: les formats sont verifies par tests unitaires/frontend; aucun endpoint ou route runtime ne change.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-098-classer-centraliser-helpers-formatage-pages/page-helpers-before.md`.
- Comparison after implementation: `_condamad/stories/CS-098-classer-centraliser-helpers-formatage-pages/page-helpers-after.md`.
- Required baseline content: scan des definitions locales, classification initiale par concept (`date`, `price`, `error`), expected canonical owner.
- Expected invariant: every hit after implementation is canonical, imported from canonical owner, or explicitly classified page-specific with no shared duplicate.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Shared date formatting | `frontend/src/utils/formatDate.ts` or a documented date utility owner | page-local `formatDate` duplicates |
| Shared money formatting | `frontend/src/config/pricingConfig.ts` or exact new utility | page-local `formatPrice` duplicates |
| Shared API/error message formatting | existing `frontend/src/utils/apiErrorSupport.ts` plus exact utility when proven | page-local `getErrorMessage` duplicates |

Rules:
- centralize only identical or intentionally equivalent behavior;
- do not normalize two product concepts into one helper if the UI copy differs;
- any retained local helper must cite why a shared owner would be wrong.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `page-helpers-after.md` | retained helper classification | only proven page-specific helpers | expires if duplicated elsewhere |

Rules:
- no wildcard;
- no folder-wide exception;
- no unclassified retained helper;
- no `PASS with limitation`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: the lot is finite and target-specific, not an open batch migration program.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before helper inventory | `_condamad/stories/CS-098-classer-centraliser-helpers-formatage-pages/page-helpers-before.md` | Capturer definitions locales et duplication presumee. |
| After helper inventory | `_condamad/stories/CS-098-classer-centraliser-helpers-formatage-pages/page-helpers-after.md` | Prouver owner canonique ou classification one-off. |
| Final validation | `_condamad/stories/CS-098-classer-centraliser-helpers-formatage-pages/generated/10-final-evidence.md` | Persister tests/scans finaux. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: targeted scan for local helper definitions must be captured and explained after implementation.
- Deterministic source: `rg` scan over `frontend/src` for the three helper name patterns.
- Required forbidden examples: duplicate shared helper behavior, convenience wrapper, broad mixed "format helper" utility.
- Guard evidence: helper tests plus before/after inventory.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md#F-003`
- Closure proof required: helper inventory before/after, tests for canonical helpers, targeted scan of helper definitions.
- Known residual in-domain work: local helper definitions may remain only when classified as page-specific one-offs.
- Remaining closure map: `page-helpers-after.md` must classify every scan hit; no unclassified helper may remain.
- Stop condition: every hit is either canonical, imported from canonical helper, or classified as a page-specific one-off with no shared duplicate.
- Deferred non-domain concerns: none.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md#E-008` - local `formatDate`, `formatPrice`, and `getErrorMessage` definitions remain.
- Evidence 2: `frontend/src/utils/formatDate.ts` - existing canonical date utility already exists.
- Evidence 3: `frontend/src/utils/apiErrorSupport.ts` - CS-092 created a support-error utility owner.
- Evidence 4: `_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/00-story.md` - prior helper slice did not close all helper duplication.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

- Repeated date, price and error formatting behavior has one canonical owner where sharing is valid.
- Pages import canonical helpers instead of redefining duplicated behavior.
- Retained local helpers are explicitly classified and tested where needed.
- No compatibility helper wrappers are introduced.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page architecture should not regain unclassified duplicate helper ownership.
  - `RG-053` - error/runtime compatibility must not be preserved through hidden fallback mapping.
- Non-applicable invariants:
  - `RG-054` - no route aliases or redirects are touched.
  - `RG-047` - no inline style surface is touched.
- Required regression evidence:
  - `npm run test -- formatDate`
  - exact tests for any new or modified money/error utility
  - `npm run lint`
  - final helper definition scan.
- Allowed differences:
  - Imports and helper owners change; visible formatted output must remain equivalent unless a blocker is recorded.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before inventory captures every local target helper definition. | `rg -n "formatDate|formatPrice|getErrorMessage" frontend/src -g "*.ts" -g "*.tsx"`. |
| AC2 | Shared duplicate behavior is centralized. | `npm run test -- formatDate`; `rg -n "canonical-owner" _condamad/stories/CS-098*/page-helpers-after.md`. |
| AC3 | Retained local helpers are classified with reason. | `rg -n "page-specific-retained|canonical-owner" _condamad/stories/CS-098*/page-helpers-after.md`. |
| AC4 | Canonical helper behavior is covered by tests. | Evidence profile: `runtime_behavior`; `npm run test -- formatDate`; exact money/error tests for changed helpers. |
| AC5 | No duplicate active helper remains. | `rg -n "unclassified|duplicate-shared" _condamad/stories/CS-098*/page-helpers-after.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture before helper inventory and classify each hit by concept. (AC: AC1)
- [ ] Task 2 - Select canonical owner(s) for genuinely duplicated helper behavior. (AC: AC2)
- [ ] Task 3 - Replace page-local duplicates with imports and preserve output behavior. (AC: AC2, AC4)
- [ ] Task 4 - Classify retained local helpers in after evidence. (AC: AC3)
- [ ] Task 5 - Run tests/scans and persist final evidence. (AC: AC4, AC5)
  - [ ] Add exact tests for every new or modified canonical money/error helper.
  - [ ] Mark every after-scan hit as `canonical-owner`, `canonical-import-consumer`, or `page-specific-retained`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/utils/formatDate.ts` for shared date formatting when behavior matches.
- Reuse `frontend/src/utils/apiErrorSupport.ts` for support-error classification and do not duplicate its logic.
- Reuse `frontend/src/config/pricingConfig.ts` only if the helper is product pricing config; create a generic money utility only if duplication proves a generic owner is needed.
- Do not create catch-all utility modules with unrelated date, price and error responsibilities.

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
- duplicated local `formatDate`, `formatPrice`, or `getErrorMessage` with shared behavior.
- helper wrappers whose only purpose is preserving an old local name.
- `any` broadening to avoid typing a helper.
- `PASS with limitation`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Date formatting | `frontend/src/utils/formatDate.ts` unless classified one-off | page-local `formatDate` |
| Product price formatting | `frontend/src/config/pricingConfig.ts` or exact utility owner selected by evidence | page-local `formatPrice` |
| API/error message formatting | `frontend/src/utils/**` exact owner | page-local `getErrorMessage` |

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
- `_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/00-story.md`
- `frontend/src/pages/admin/PersonasAdmin.tsx`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx`
- `frontend/src/pages/admin/AdminContentPage.tsx`
- `frontend/src/pages/admin/AdminPricingPanel.tsx`
- `frontend/src/pages/SubscriptionGuidePage.tsx`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/settings/AccountSettings.tsx`
- `frontend/src/utils/formatDate.ts`
- `frontend/src/utils/apiErrorSupport.ts`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/pages/admin/PersonasAdmin.tsx` - replace or classify local date helper.
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx` - replace or classify local date helper.
- `frontend/src/pages/admin/AdminContentPage.tsx` - replace or classify local date helper.
- `frontend/src/pages/admin/AdminPricingPanel.tsx` - replace or classify price helper.
- `frontend/src/pages/SubscriptionGuidePage.tsx` - replace or classify price helper.
- `frontend/src/pages/settings/SubscriptionSettings.tsx` - replace or classify price helper.
- `frontend/src/pages/settings/AccountSettings.tsx` - replace or classify date helper.
- `frontend/src/utils/formatDate.ts` - extend only if existing shared date behavior needs a typed variant.
- `frontend/src/utils/**` - add exact money/error utility only if classification proves shared behavior.

Likely tests:
- `frontend/src/tests/formatDate.test.ts` - update shared date coverage.
- `frontend/src/tests/formatPrice.test.ts` - create if generic money helper is added or modified.
- `frontend/src/tests/apiErrorMessage.test.ts` - create if generic error-message helper is added or modified.
- Existing page tests only if behavior is not otherwise covered.

Files not expected to change:
- `backend/**` - no backend contract change.
- `frontend/src/tests/page-architecture-allowlist.ts` - no page-architecture exception expected.
- `frontend/package.json` - existing scripts are sufficient.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- formatDate
rg -n "function formatDate|const formatDate|function formatPrice|const formatPrice|function getErrorMessage|const getErrorMessage" src -g "*.ts" -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-098-classer-centraliser-helpers-formatage-pages/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: shared helper changes visible locale/currency/date output.
  - Guardrail: tests compare current behavior and blocker condition prevents product-copy changes.
- Risk: over-centralized helper mixes unrelated concepts.
  - Guardrail: ownership classification by concept and KISS/DRY constraints.
- Risk: retained locals hide duplicates.
  - Guardrail: after inventory must classify every hit.

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

- `_condamad/audits/frontend-react-pages/2026-05-08-1024/03-story-candidates.md#SC-003`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md#F-003`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/01-evidence-log.md`
- `_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/00-story.md`
- `_condamad/stories/regression-guardrails.md`
