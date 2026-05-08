# Story CS-105 rattacher-routes-auth-publiques-layout: Rattacher les routes auth publiques a un layout

Status: ready-to-dev

## 1. Objective

Definir et appliquer `AuthLayout` comme layout secondaire explicite pour `/login` et `/register`.
`AuthLayout` vit sous le master `RootLayout` et evite d'imposer la navbar/footer landing
ou le shell applicatif a des visiteurs publics.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-003`
- Reason for change: `F-003` indique que `/login` et `/register` rendent directement `LoginPage` et `RegisterPage` sans layout route-level.

## 3. Domain Boundary

- Domain: `frontend-layouts`
- In scope:
  - Monter `/login` et `/register` sous `AuthLayout`.
  - Monter `AuthLayout` sous le master `RootLayout`.
  - Preserver navigation login/register et comportements d'auth existants.
  - Ajouter une garde contre les routes auth directes.
- Out of scope:
  - Modifier le backend auth, les contrats API ou les schemas.
  - Redessiner les formulaires auth.
  - Modifier la landing sauf si elle est explicitement choisie comme famille owner.
- Explicit non-goals:
  - Ne pas creer un layout auth concurrent.
  - Ne pas afficher navbar/footer landing par defaut sans decision.
  - Ne pas reutiliser `AppLayout` si cela expose le shell applicatif a des visiteurs publics sans decision.
  - Ne pas affaiblir `RG-064`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: ownership-routing-refactor
- Archetype reason: les routes auth doivent etre routees vers un owner canonique de layout.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: ajout du layout ancestor decide.
  - Interdit: changement des formulaires, API auth, URLs `/login` et `/register`, ou redirects sans decision.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le produit refuse explicitement `AuthLayout` comme layout secondaire pour les routes auth publiques.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La route tree frontend doit etre prouvee par `AST guard` sur `routes.tsx`. |
| Baseline Snapshot | yes | La route tree before/after doit prouver la suppression des routes directes. |
| Ownership Routing | yes | L'objet de la story est la classification d'ownership auth. |
| Allowlist Exception | yes | Toute exception temporaire doit etre exacte, mais la cible est zero route directe. |
| Contract Shape | no | Aucun payload, DTO, schema ou contrat HTTP n'est change. |
| Batch Migration | no | Deux routes auth sont traitees comme une meme responsabilite. |
| Reintroduction Guard | yes | Les routes directes login/register ne doivent pas revenir. |
| Persistent Evidence | yes | La decision et la route inventory doivent etre persistantes. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - runtime artifact: `AST guard` over `frontend/src/app/routes.tsx` route object tree.
  - router/App tests rendering `/login` and `/register`.
- Secondary evidence:
  - targeted scan for direct auth page route elements.
- Static scans alone are not sufficient because:
  - a direct page import can remain while the effective route ancestry is correct or incorrect.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/auth-layout-before.md`.
- Comparison after implementation: `_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/auth-layout-after.md`.
- Required baseline content: routes `/login` et `/register`, layout ancestor courant, owner decision, tests affectes.
- Expected invariant: aucune route auth publique ne rend directement une page sans layout owner.
- Allowed differences: wrapper/layout ancestor choisi et classes CSS associees au layout existant.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Auth route ownership | `AuthLayout` under `RootLayout` | direct `LoginPage`/`RegisterPage` route |
| Auth page content | `LoginPage` / `RegisterPage` | layout component |
| Auth visual shell | selected layout owner | page-local duplicated wrapper |

Rules:
- La decision canonique est `AuthLayout` secondaire sous `RootLayout`.
- `needs-user-decision` est reserve a un refus produit explicite de ce choix.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `auth-layout-after.md` | `/login` or `/register` direct route | allowed only if product explicitly rejects `AuthLayout` | expires immediately; implementation stops |

Rules:
- No wildcard route exception.
- No folder-wide auth exception.
- Une exception directe doit bloquer la story, pas la rendre `done`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: `/login` et `/register` forment une seule surface auth publique.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before auth route inventory | `_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/auth-layout-before.md` | Capturer les routes directes. |
| After auth route inventory | `_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/auth-layout-after.md` | Capturer decision owner et route tree finale ou blocker. |
| Final evidence | `_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/generated/10-final-evidence.md` | Conserver commandes, decision et resultats. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: test qui echoue si `/login` ou `/register` a un `element` direct `LoginPage`/`RegisterPage` sans layout ancestor.
- Deterministic source: route tree `frontend/src/app/routes.tsx`.
- Required forbidden examples:
  - direct `/login` route rendering `LoginPage`;
  - direct `/register` route rendering `RegisterPage`;
  - local auth shell duplique dans les pages.
- Guard evidence: `npm run test -- App router page-architecture layout`.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-003`
- Closure proof required: user/product decision captured, route tree after inventory, guard against direct auth routes.
- Known residual in-domain work: none
- Deferred non-domain concerns: auth API/security contract changes are out of scope.
- Full-closure rule: do not accept direct auth page routes, guessed alternate layout family,
  broad allowlists, wildcard exceptions, compatibility, shim, alias, TODO, or hidden residual work.

## 5. Current State Evidence

- Evidence 1: `frontend/src/app/routes.tsx` - `/login` maps directly to `LoginPage`.
- Evidence 2: `frontend/src/app/routes.tsx` - `/register` maps directly to `RegisterPage`.
- Evidence 3: `frontend/src/pages/LoginPage.tsx` and `frontend/src/pages/RegisterPage.tsx` - page components exist and should remain content owners.
- Evidence 4: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-003` - audit identifies a boundary violation.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - frontend invariants consulted before scope was finalized.

## 6. Target State

- `/login` and `/register` have an explicit layout ancestor under the master route.
- `AuthLayout` ownership is documented and guarded.
- Auth page behavior remains stable.
- If product rejects `AuthLayout`, the story records a blocker instead of shipping a guessed alternate layout.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page architecture guards must stay exact.
  - `RG-047` - no inline style workaround should be added to auth pages.
  - `RG-048` - no new CSS fallback debt should be introduced.
- Non-applicable invariants:
  - `RG-065` - admin prompts ownership is not touched.
  - `RG-067` - date/time formatting is not touched.
- Required regression evidence:
  - `npm run test -- App router page-architecture layout`
  - before/after auth route inventory.
- Allowed differences:
  - layout ancestor decided by user/product owner.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `AuthLayout` ownership is recorded. | Evidence profile: `persistent_evidence`; runtime evidence `AST guard`; command `rg -n "AuthLayout" auth-layout-after.md`. |
| AC2 | Auth routes are no longer direct page routes. | Evidence profile: `baseline_before_after_diff`; runtime evidence `AST guard`; test `npm run test -- router layout`. |
| AC3 | Login/register behavior remains stable. | Evidence profile: `reintroduction_guard`; command `npm run test -- App router` with auth route assertions. |
| AC4 | Guard prevents direct auth routes. | Evidence profile: `reintroduction_guard`; runtime evidence `AST guard`; command `npm run test -- page-architecture`. |
| AC5 | Story stops cleanly if product rejects `AuthLayout`. | Evidence profile: `external_usage_blocker`; command `rg -n "needs-user-decision" auth-layout-after.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture before auth route inventory. (AC: AC1, AC2)
- [ ] Task 2 - Record `AuthLayout` ownership decision or explicit product rejection. (AC: AC1, AC5)
- [ ] Task 3 - Route `/login` and `/register` through the selected layout. (AC: AC2, AC3)
- [ ] Task 4 - Add or extend guard against direct auth routes. (AC: AC4)
- [ ] Task 5 - Capture after evidence and run validation. (AC: AC2, AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse existing `LoginPage` and `RegisterPage` as content owners.
- Reuse existing `AuthLayout` as the selected secondary layout.
- Do not reuse `LandingLayout` unless this story is revised with explicit product decision.
- Do not create a duplicate auth wrapper in each page.

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
- direct `/login` route rendering `LoginPage` after closure.
- direct `/register` route rendering `RegisterPage` after closure.
- page-local auth shell wrappers used to avoid a route layout.
- alternate layout family without explicit product decision.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Auth route layout ownership | `AuthLayout` recorded in `auth-layout-after.md` | direct auth page routes |
| Auth form content | `LoginPage` / `RegisterPage` | layout owner |
| Auth route guard evidence | page/layout architecture guard | manual audit only |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

If the product owner rejects `AuthLayout`, implementation must stop. The blocker must name the requested alternate family and risk; no fallback layout is allowed.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-003`
- `frontend/src/app/routes.tsx`
- `frontend/src/layouts/AuthLayout.tsx`
- `frontend/src/layouts/LandingLayout.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/RegisterPage.tsx`
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/page-architecture-guards.test.ts`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/app/routes.tsx` - nest auth routes under selected layout.
- `frontend/src/tests/page-architecture-guards.test.ts` - guard direct auth routes.
- `frontend/src/tests/App.test.tsx` or router test file - preserve login/register behavior.

Likely tests:
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/page-architecture-guards.test.ts`

Files not expected to change:
- `backend/**` - no auth API change.
- `frontend/src/api/**` - no auth client change expected.
- `frontend/package.json` - no dependency/script change expected.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- App router page-architecture layout
rg -n "LoginPage|RegisterPage" src/app/routes.tsx
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: auth pages inherit an unwanted landing/application shell.
  - Guardrail: AC1 requires decision before edit.
- Risk: direct routes remain through broad exception.
  - Guardrail: AC4 and No Legacy forbid direct route residual.
- Risk: auth API behavior changes accidentally.
  - Guardrail: API/client files are out of scope.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not choose a layout family other than `AuthLayout` without product/user decision.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-003` - source candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-003` - source finding.
- `frontend/src/app/routes.tsx` - current direct routes.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
