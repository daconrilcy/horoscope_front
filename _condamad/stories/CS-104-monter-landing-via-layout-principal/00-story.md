# Story CS-104 monter-landing-via-layout-principal: Monter la landing via son layout principal

Status: ready-to-dev

## 1. Objective

Fermer le bypass actif de `LandingLayout` sur la route publique `/`.
`LandingRedirect` conserve uniquement la decision de redirection et purge de token.
Il ne doit plus recreer `.landing-layout`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-002`
- Reason for change: `F-002` montre que `LandingRedirect` importe `LandingLayout.css` et recree un wrapper `.landing-layout` alors que `LandingLayout` existe.

## 3. Domain Boundary

- Domain: `frontend-layouts`
- In scope:
  - Router la landing via `frontend/src/layouts/LandingLayout.tsx`.
  - Retirer le wrapper local `ScopedLandingPage` ou equivalent de `LandingRedirect`.
  - Preserver purge du token expire et redirect token actif vers `/dashboard`.
  - Ajouter une preuve negative contre l'import direct de `LandingLayout.css` et `.landing-layout` hors owner.
- Out of scope:
  - Modifier le contenu de `frontend/src/pages/landing/**`.
  - Decider l'ownership des routes auth; story `CS-105`.
  - Migrer les tokens/style landing.
- Explicit non-goals:
  - Ne pas creer de layout landing secondaire.
  - Ne pas remplacer le bypass par un autre wrapper.
  - Ne pas supprimer `LandingLayout`.
  - Ne pas affaiblir `RG-064`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: `LandingRedirect` agit comme facade/wrapper local d'un layout canonique existant.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: rendu de navbar/footer si cela correspond au layout canonique.
  - Interdit: changement du redirect authentifie, de la purge du token expire et du contenu landing.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: le produit confirme que la landing publique ne doit pas afficher navbar/footer de `LandingLayout`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La route `/` doit prouver son layout ancestor par route tree/test. |
| Baseline Snapshot | yes | Le bypass `.landing-layout` before/after doit etre capture. |
| Ownership Routing | yes | La responsabilite wrapper landing doit revenir a `LandingLayout`. |
| Allowlist Exception | no | Aucune exception au bypass landing n'est autorisee. |
| Contract Shape | no | Aucun contrat API/payload/type genere n'est change. |
| Batch Migration | no | Une seule facade de layout est retiree. |
| Reintroduction Guard | yes | Le bypass ne doit pas revenir via import CSS ou wrapper local. |
| Persistent Evidence | yes | Les scans before/after doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - runtime artifact: `AST guard` over route tree `frontend/src/app/routes.tsx`;
  - tests App/router/visual-smoke qui rendent `/`.
- Secondary evidence:
  - scan de `LandingRedirect.tsx` et des imports `LandingLayout.css`.
- Static scans alone are not sufficient because:
  - l'absence d'import CSS ne prouve pas que `/` passe bien par `LandingLayout`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-104-monter-landing-via-layout-principal/landing-layout-before.md`.
- Comparison after implementation: `_condamad/stories/CS-104-monter-landing-via-layout-principal/landing-layout-after.md`.
- Required baseline content: route `/`, owner courant, wrapper `.landing-layout`, imports CSS, tests existants.
- Expected invariant: seul `LandingLayout` cree `.landing-layout` pour la route landing.
- Allowed differences: route nesting sous `LandingLayout` et suppression du wrapper local.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Landing wrapper `.landing-layout` | `frontend/src/layouts/LandingLayout.tsx` | `LandingRedirect` ou page locale |
| Landing redirect/token purge | `frontend/src/app/guards/LandingRedirect.tsx` | `LandingLayout` |
| Landing page content | `frontend/src/pages/landing/LandingPage.tsx` | guard ou layout |

Rules:
- `LandingRedirect` ne doit pas importer `LandingLayout.css`.
- `LandingLayout` ne doit pas contenir de logique de token.

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune exception au bypass landing n'est permise pour une story full-closure.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: une seule facade/wrapper est retiree.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before landing layout audit | `_condamad/stories/CS-104-monter-landing-via-layout-principal/landing-layout-before.md` | Capturer le bypass existant. |
| After landing layout audit | `_condamad/stories/CS-104-monter-landing-via-layout-principal/landing-layout-after.md` | Prouver owner canonique et absence de bypass. |
| Final evidence | `_condamad/stories/CS-104-monter-landing-via-layout-principal/generated/10-final-evidence.md` | Conserver commandes et resultats. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: scan/test echoue si `LandingRedirect` importe `LandingLayout.css` ou rend `.landing-layout`.
- The architecture guard must fail if the bypass is reintroduced.
- Deterministic source: frontend route table and forbidden symbols.
- Required forbidden examples:
  - `import "../../layouts/LandingLayout.css"` dans `LandingRedirect.tsx`;
  - `className="landing-layout"` hors `LandingLayout.tsx`;
  - `ScopedLandingPage` wrapper local.
- Guard evidence: `npm run test -- App visual-smoke page-architecture layout` et scans cibles.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-002`
- Closure proof required: route `/` sous `LandingLayout`, negative scan du bypass, App/visual-smoke green.
- Known residual in-domain work: none
- Deferred non-domain concerns: none
- Full-closure rule: do not accept `PASS with limitation`, broad allowlists,
  wildcard exceptions, unclassified fallback, compatibility, legacy,
  migration-only, shim, alias, TODO, or hidden residual in-domain work.

## 5. Current State Evidence

- Evidence 1: `frontend/src/app/guards/LandingRedirect.tsx` - imports `../../layouts/LandingLayout.css` and defines `ScopedLandingPage`.
- Evidence 2: `frontend/src/app/guards/LandingRedirect.tsx` - renders a local `landing-layout` wrapper around `LandingPage`.
- Evidence 3: `frontend/src/layouts/LandingLayout.tsx` - already owns navbar, `main`, footer and `.landing-layout`.
- Evidence 4: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-002` - audit classifies duplicate layout responsibility.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - frontend invariants consulted before scope was finalized.

## 6. Target State

- `/` renders landing content through `LandingLayout`.
- `LandingRedirect` only decides expired-token purge or redirect to `/dashboard`.
- No local landing wrapper or CSS import bypass remains.
- Guard blocks a future bypass.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - route/page architecture must stay guarded.
  - `RG-047` - no inline style workaround should be introduced.
  - `RG-048` - no CSS fallback debt should be added while touching layout CSS imports.
- Non-applicable invariants:
  - `RG-065` - admin prompts ownership is not touched.
  - `RG-067` - date/time formatting is not touched.
- Required regression evidence:
  - `npm run test -- App visual-smoke page-architecture`
  - targeted scans for `LandingLayout.css`, `landing-layout`, and `ScopedLandingPage`.
- Allowed differences:
  - navbar/footer appearance follows `LandingLayout` unless product decision blocks.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Route `/` renders through `LandingLayout`. | Evidence profile: `runtime_behavior`; runtime evidence `AST guard`; command `npm run test -- App visual-smoke`. |
| AC2 | Guard no longer imports landing CSS. | Evidence profile: `targeted_forbidden_symbol_scan`; command `rg -n "LandingLayout.css" src/app/guards/LandingRedirect.tsx`. |
| AC3 | Landing redirect behavior remains intact. | Evidence profile: `reintroduction_guard`; command `npm run test -- App router`. |
| AC4 | No landing bypass exception remains. | Evidence profile: `repo_wide_negative_scan`; command `rg -n "className=.*landing-layout" frontend/src -g "*.tsx"`. |
| AC5 | Frontend lint remains green. | Evidence profile: `reintroduction_guard`; command `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture before landing ownership evidence. (AC: AC1, AC2, AC4)
- [ ] Task 2 - Route landing through `LandingLayout`. (AC: AC1, AC3)
- [ ] Task 3 - Remove local wrapper/import from `LandingRedirect`. (AC: AC2, AC4)
- [ ] Task 4 - Add/extend guard against landing layout bypass. (AC: AC2, AC4)
- [ ] Task 5 - Capture after evidence and run validation. (AC: AC1, AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/layouts/LandingLayout.tsx` as the only landing wrapper owner.
- Reuse `LandingRedirect` only for redirect/token decisions.
- Do not duplicate `LandingNavbar`, `LandingFooter`, or `.landing-layout` responsibility.
- Do not create a new auth/landing hybrid layout in this story.

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
- `ScopedLandingPage` in `LandingRedirect`.
- `LandingLayout.css` import from `LandingRedirect`.
- `.landing-layout` wrapper outside `LandingLayout`.
- `PASS with limitation`.

## 11. Removal Classification Rules

Classification must be deterministic:
- `canonical-active`: `LandingLayout` and `LandingPage`.
- `external-active`: product-visible `/` route shell or public UX dependency.
- `historical-facade`: local landing wrapper inside `LandingRedirect`.
- `dead`: wrapper helpers with zero consumers after reroute.
- `needs-user-decision`: only if product rejects navbar/footer.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `historical-facade` | `delete` | Must be deleted, not repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `LandingLayout` | TSX component | `canonical-active` | `/` route | none | `keep` | route after artifact | deleting would break canonical owner |
| `ScopedLandingPage` | local component | `historical-facade` | `/` route | `LandingLayout` | `delete` | before/after scan | public wrapper behavior |
| `LandingRedirect` consumer | route consumer | `canonical-active` | `/` route | `LandingLayout` ancestor | `replace-consumer` | route after artifact | redirect behavior |
| external landing shell | public UX | `external-active` | `/` route | `LandingLayout` | `keep` or `needs-user-decision` | visual smoke/decision | navbar/footer risk |
| stale local wrapper helper | local symbol | `dead` | zero after reroute | none | `delete` | scan | none |

Audit output path when applicable:
- `_condamad/stories/CS-104-monter-landing-via-layout-principal/landing-layout-before.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Landing layout wrapper | `frontend/src/layouts/LandingLayout.tsx` | `ScopedLandingPage` |
| Landing redirect decision | `frontend/src/app/guards/LandingRedirect.tsx` | layout component |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:
- preserving `ScopedLandingPage`;
- adding another wrapper component;
- importing `LandingLayout.css` from the guard;
- preserving old path through re-export;
- preserving old path through alias/fallback.

Route consumer note:
- `LandingRedirect` may remain as the canonical redirect/token decision component.
- The removable local landing wrapper remains delete-only.
- Any route consumer update must not preserve a wrapper, alias, or fallback.

## 15. External Usage Blocker

If an item is classified `external-active`, it must not be deleted.
If product decision says landing must not show navbar/footer, stop and record the user decision.
Do not keep the bypass as a silent compatibility route.

## 17. Generated Contract Check

- Generated contract check: frontend route table check required.
- Required generated-contract evidence:
  - route table inventory in `_condamad/stories/CS-104-monter-landing-via-layout-principal/landing-layout-after.md`;
  - `AST guard` proving the public `/` route is mounted under `LandingLayout`;
  - no generated API/OpenAPI change expected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-002`
- `frontend/src/app/routes.tsx`
- `frontend/src/app/guards/LandingRedirect.tsx`
- `frontend/src/layouts/LandingLayout.tsx`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/app/routes.tsx` - mount landing under `LandingLayout`.
- `frontend/src/app/guards/LandingRedirect.tsx` - remove local wrapper and CSS import.
- `frontend/src/tests/page-architecture-guards.test.ts` - add landing bypass guard if no dedicated layout guard exists.
- `frontend/src/tests/App.test.tsx` - update landing redirect expectations when assertions are missing.

Likely tests:
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/page-architecture-guards.test.ts`

Files not expected to change:
- `backend/**` - no backend contract.
- `frontend/src/pages/landing/sections/**` - no landing content redesign.
- `frontend/package.json` - no dependency/script change expected.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- App visual-smoke page-architecture layout
rg -n "LandingLayout.css|landing-layout|ScopedLandingPage" src/app/guards/LandingRedirect.tsx
rg -n "className=\"landing-layout\"|className='landing-layout'" src -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-104-monter-landing-via-layout-principal/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: navbar/footer appears where product did not expect it.
  - Guardrail: user decision blocker if canonical `LandingLayout` behavior is rejected.
- Risk: redirect logic moves into layout.
  - Guardrail: ownership routing forbids token logic in `LandingLayout`.
- Risk: bypass returns as another wrapper.
  - Guardrail: negative scan/guard on `.landing-layout` outside owner.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated edits.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-002` - source candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-002` - source finding.
- `frontend/src/app/guards/LandingRedirect.tsx` - current bypass.
- `frontend/src/layouts/LandingLayout.tsx` - canonical landing layout.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
