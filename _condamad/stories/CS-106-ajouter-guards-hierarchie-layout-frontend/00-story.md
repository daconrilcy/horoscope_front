# Story CS-106 ajouter-guards-hierarchie-layout-frontend: Ajouter les guards de hierarchie layout frontend

Status: ready-to-dev

## 1. Objective

Rendre la cible d'architecture `frontend-layouts` executable par des guards deterministes.
Les tests doivent bloquer `RootLayout` non monte, un bypass de `LandingLayout`,
une route page sans layout owner et toute exception large.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-004`
- Reason for change: `F-004` montre que les tests actuels passent sans verifier la hierarchie route-to-layout.

## 3. Domain Boundary

- Domain: `frontend-layouts`
- In scope:
  - Ajouter ou etendre des guards Vitest/AST sur la route tree frontend.
  - Verifier `RootLayout` monte.
  - Verifier les principal layout families accepteees et les exceptions exactes.
  - Verifier l'absence de bypass `LandingLayout`.
  - Documenter les exceptions sous forme d'allowlist exacte.
- Out of scope:
  - Refactorer les routes ou layouts applicatifs au-dela du minimum requis pour rendre le guard coherent.
  - Classer tout l'inventaire `pages/**/*.tsx`; story `CS-107`.
  - Changer le design system ou les permissions admin.
- Explicit non-goals:
  - Ne pas remplacer un refactor de route par une exception.
  - Ne pas accepter de wildcard ou dossier entier.
  - Ne pas affaiblir les guards page-architecture existants.
  - Ne pas ajouter une dependance de parsing si les patterns de tests existants suffisent.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story ajoute la source executable de prevention anti-drift pour la hierarchie des layouts.
- Behavior change allowed: no
- Behavior change constraints:
  - Aucun comportement applicatif visible ne doit changer.
  - Les seules modifications runtime acceptables sont celles strictement necessaires si une route deja corrigee n'est pas exposee au guard.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: une route page ne peut pas etre rattachee ou classee sans decision produit.
- Implementation sequencing: `CS-103`, `CS-104`, `CS-105`, and `CS-107` must be implemented first,
  or represented by exact temporary exceptions that name their closing story.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards deviennent la source executable de la politique layout. |
| Baseline Snapshot | yes | Les regles et exceptions de guard doivent etre capturees avant/apres. |
| Ownership Routing | no | La story ne migre pas les owners; elle les valide. |
| Allowlist Exception | yes | Les exceptions de route/layout doivent etre exactes et testees. |
| Contract Shape | no | Aucun contrat API/payload/schema n'est modifie. |
| Batch Migration | no | Pas de migration par lots. |
| Reintroduction Guard | yes | Objet principal de la story. |
| Persistent Evidence | yes | Les preuves de guard/allowlist doivent etre persistantes. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - runtime artifact: `AST guard` over `frontend/src/app/routes.tsx` route object tree;
  - `AST guard` Vitest dans `frontend/src/tests/page-architecture-guards.test.ts` ou `layout-architecture-guards.test.ts`.
- Secondary evidence:
  - scans `LandingLayout.css`, `.landing-layout`, `RootLayout`, direct page elements.
- Static scans alone are not sufficient because:
  - le guard doit raisonner sur les ancetres route-level, pas uniquement sur la presence de symboles.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-106-ajouter-guards-hierarchie-layout-frontend/layout-guard-before.md`.
- Comparison after implementation: `_condamad/stories/CS-106-ajouter-guards-hierarchie-layout-frontend/layout-guard-evidence.md`.
- Required baseline content: tests existants, absence de guard layout, exceptions courantes.
- Expected invariant: le guard final detecte `RootLayout`, les ancestors layout, le bypass landing et les exceptions exactes.
- Allowed differences: fichiers de test/allowlist uniquement.

## 4d. Ownership Routing Rule

- Ownership Routing Rule: not applicable
- Reason: la story ne deplace pas d'owner; elle valide les owners attendus par guard.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| layout allowlist | exact route exception | route blocked/pending decision | expires by named story before closure |
| layout allowlist | exact page-adjacent exception | not a route leaf | permanent only with owner and classification |

Rules:
- No wildcard.
- No folder-wide exception.
- No `PASS with limitation`.
- Every exception must name route/file, owner, reason, expiry/permanence.
- Temporary exceptions may only reference `CS-103`, `CS-104`, `CS-105`, or `CS-107`.
- A temporary exception cannot remain when this story is marked `done`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: aucune migration applicative par lots.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guard evidence | `_condamad/stories/CS-106-ajouter-guards-hierarchie-layout-frontend/layout-guard-evidence.md` | Capturer les regles, exceptions exactes et commandes. |
| Final evidence | `_condamad/stories/CS-106-ajouter-guards-hierarchie-layout-frontend/generated/10-final-evidence.md` | Conserver resultats lint/test/scans. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: guard Vitest qui echoue sur master layout absent, bypass landing, route leaf page directe, ou exception large.
- Deterministic source: route tree plus sources TSX cibles.
- Required forbidden examples:
  - `RootLayout` absent de `routes.tsx`;
  - `LandingRedirect` important `LandingLayout.css`;
  - `.landing-layout` rendu hors `LandingLayout.tsx`;
  - route leaf page sans `RootLayout` et principal layout ancestor ou exception exacte.
- Guard evidence: `npm run test -- page-architecture layout`.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-004`
- Closure proof required: deterministic guard added/updated, exact allowlist, negative scans, `npm run test -- page-architecture layout`.
- Known residual in-domain work: pending implementation of `CS-103`, `CS-104`, `CS-105`, and `CS-107`,
  or exact temporary exceptions that name those closing stories.
- Deferred non-domain concerns: none
- Remaining closure map: once prerequisite stories are implemented, rerun this story to remove any temporary exceptions and mark the guard full-closure.
- Stop condition: deterministic guard exists, every temporary exception is exact and expires by a named story, and no wildcard exception exists.
- Full-closure rule after prerequisites: do not accept `PASS with limitation`, broad allowlists,
  wildcard exceptions, unclassified fallback, compatibility, legacy,
  migration-only, shim, alias, TODO, or hidden residual in-domain work.

## 5. Current State Evidence

- Evidence 1: `frontend/src/tests/page-architecture-guards.test.ts` - current guards cover page smells and route aliases, not layout ancestry.
- Evidence 2: `frontend/src/tests/page-architecture-allowlist.ts` - existing allowlist model can be reused with exact entries.
- Evidence 3: `frontend/src/app/routes.tsx` - route tree is exported and available to tests.
- Evidence 4: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-004` - audit says tests can pass while hierarchy is violated.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - frontend guard invariants consulted before scope was finalized.

## 6. Target State

- Layout hierarchy policy is enforced by deterministic frontend tests.
- Temporary exceptions are exact, auditable, and tied to CS-103 through CS-107.
- Landing bypass and unmounted `RootLayout` fail the guard.
- Existing page-architecture guards remain intact.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - this story extends page architecture guards without weakening them.
  - `RG-065` - admin prompts ownership guard must remain green.
  - `RG-066` - page-size allowlists remain exact.
  - `RG-067` - date/time page helper ownership remains untouched.
- Non-applicable invariants:
  - `RG-044` - no token namespace change.
  - `RG-053` - no runtime payload compatibility change.
- Required regression evidence:
  - `npm run test -- page-architecture layout`
  - `npm run lint`
  - targeted scans for bypass examples.
- Allowed differences:
  - tests/allowlist artifacts only.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Guard proves `RootLayout` is mounted. | Evidence profile: `reintroduction_guard`; `npm run test -- page-architecture layout`. |
| AC2 | Guard proves page route layout ancestry. | Evidence profile: `allowlist_register_validated`; runtime evidence `AST guard`; test `npm run test -- page-architecture`. |
| AC3 | Guard blocks landing layout bypass. | Evidence profile: `targeted_forbidden_symbol_scan`; command `rg -n "LandingLayout.css" frontend/src/app frontend/src/layouts`. |
| AC4 | Allowlist contains no wildcard or folder-wide exception. | Evidence profile: `allowlist_register_validated`; command `rg -n "wildcard" frontend/src/tests`. |
| AC5 | Existing page-architecture tests remain green. | Evidence profile: `reintroduction_guard`; command `npm run test -- page-architecture`. |
| AC6 | Frontend lint remains green. | Evidence profile: `reintroduction_guard`; command `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inspect current page-architecture guard helpers and route tree. (AC: AC1, AC2)
- [ ] Task 2 - Add layout hierarchy guard for `RootLayout` and principal layout ancestors. (AC: AC1, AC2)
- [ ] Task 3 - Add landing bypass guard. (AC: AC3)
- [ ] Task 4 - Add exact allowlist structure only if required by current state. (AC: AC2, AC4)
- [ ] Task 4.1 - Tie every temporary exception to CS-103, CS-104, CS-105, or CS-107. (AC: AC2, AC4)
- [ ] Task 5 - Persist guard evidence and run validation. (AC: AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/tests/page-architecture-guards.test.ts` helpers where possible.
- Reuse `frontend/src/tests/design-system-policy` file readers instead of ad hoc filesystem code if suitable.
- Do not duplicate route parsing logic across multiple test files unless a shared helper would be more complex than the duplication.
- Do not add parsing dependencies.

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
- wildcard layout exceptions.
- folder-wide `frontend/src/pages/**` layout exception.
- guard relying only on reviewer memory.
- `PASS with limitation`.
- disabling existing page-architecture assertions.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Layout architecture guard | `frontend/src/tests/page-architecture-guards.test.ts` or dedicated layout guard test | manual audit only |
| Layout exception registry | exact allowlist under `frontend/src/tests` | wildcard comments |
| Landing bypass prevention | guard plus route/layout scans | review-only convention |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-004`
- `frontend/src/app/routes.tsx`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/design-system-policy.ts`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/LandingLayout.tsx`
- `frontend/src/app/guards/LandingRedirect.tsx`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/tests/page-architecture-guards.test.ts` - add layout hierarchy tests.
- `frontend/src/tests/page-architecture-allowlist.ts` - add exact layout exceptions only if required.
- `frontend/src/tests/layout-architecture-guards.test.ts` - optional if keeping layout guards separate is clearer.

Likely tests:
- `frontend/src/tests/page-architecture-guards.test.ts`
- Optional `frontend/src/tests/layout-architecture-guards.test.ts`

Files not expected to change:
- `frontend/src/pages/**/*.tsx` - no page refactor.
- `backend/**` - no backend surface.
- `frontend/package.json` - existing test/lint scripts should suffice.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- page-architecture layout
rg -n "wildcard|folder-wide|PASS with limitation|frontend/src/pages/\\*\\*" src/tests/page-architecture* src/tests/*layout*
rg -n "LandingLayout.css|className=\"landing-layout\"|className='landing-layout'" src/app src/layouts -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-106-ajouter-guards-hierarchie-layout-frontend/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: guard too strict blocks phased stories.
  - Guardrail: exact exception registry with expiry story.
- Risk: guard too weak accepts current bypasses.
  - Guardrail: AC3 and forbidden examples.
- Risk: existing page architecture guard is weakened.
  - Guardrail: AC5 requires the existing suite remains green.

## 23. Dev Agent Instructions

- Implement only this story.
- Keep this story phased until CS-103, CS-104, CS-105, and CS-107 are implemented.
- Do not mark this story `done` while temporary exceptions remain.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup or route migration.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-004` - source candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-004` - source finding.
- `frontend/src/tests/page-architecture-guards.test.ts` - existing guard surface.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
