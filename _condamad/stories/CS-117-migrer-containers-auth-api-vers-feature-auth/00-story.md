# Story CS-117 migrer-containers-auth-api-vers-feature-auth: Migrer les containers auth API vers le feature owner auth

Status: done

## 1. Objective

Migrer les containers auth exacts `SignInForm` et `SignUpForm` hors de
`frontend/src/components/**` vers un owner canonique `frontend/src/features/auth/**`.
Retirer leurs exceptions `COMPONENT_API_IMPORT_EXCEPTIONS` sans changer le
comportement visible des routes `/login` et `/register`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-components/2026-05-09-0031/02-finding-register.md#F-001`
- Reason for change: le remain "move exact API-owning containers to future
  feature/page owners" est une dette de convergence cross-domain. Cette story
  traite uniquement la tranche auth car `LoginPage.tsx`, `RegisterPage.tsx`,
  `SignInForm.tsx` et `SignUpForm.tsx` forment un domaine coherent.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/features/auth`
- In scope:
  - deplacer `frontend/src/components/SignInForm.tsx` vers un composant/container auth canonique sous `frontend/src/features/auth/**`;
  - deplacer `frontend/src/components/SignUpForm.tsx` et `frontend/src/components/SignUpForm.css` sous le meme owner auth;
  - mettre a jour `frontend/src/pages/LoginPage.tsx`, `frontend/src/pages/RegisterPage.tsx` et les tests auth pour consommer le nouvel owner;
  - retirer les deux lignes auth correspondantes de `COMPONENT_API_IMPORT_EXCEPTIONS`.
- Out of scope:
  - B2B/enterprise panels;
  - ops/support panels;
  - settings/privacy panels;
  - layout auth hook ownership;
  - natal interpretation ownership;
  - backend auth API, payloads, tokens et endpoints.
- Explicit non-goals:
  - ne pas changer les contrats `loginApi`, `registerApi`, `AuthApiError` ou `setAccessToken`;
  - ne pas modifier les routes `/login` et `/register`, leur layout owner ou leurs redirects;
  - ne pas affaiblir `RG-064`, `RG-068`, `RG-069` ou `RG-070`;
  - ne pas creer de barrel `frontend/src/components/SignInForm` ou `frontend/src/components/SignUpForm` de compatibilite.

## 4. Operation Contract

- Operation type: move
- Primary archetype: legacy-facade-removal
- Archetype reason: les anciens chemins `components/SignInForm` et
  `components/SignUpForm` doivent disparaitre apres migration canonique, sans
  wrapper, alias, fallback ou re-export de compatibilite.
- Behavior change allowed: no
- Behavior change constraints:
  - les formulaires, messages d'erreur, tracking, redirections et gestion `returnTo` doivent rester equivalentes;
  - les seules differences autorisees sont les chemins d'import et l'emplacement CSS du formulaire signup.
- Deletion allowed: yes
- Replacement allowed: no
- Replacement clarification:
  - consumer imports may be repointed to the canonical auth feature owner;
  - no replacement compatibility component, wrapper, alias or re-export is allowed
    under `frontend/src/components/**`.
- User decision required if: un consommateur runtime externe a `LoginPage.tsx`, `RegisterPage.tsx` ou aux tests locaux depend encore des anciens chemins apres inventaire.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les routes auth doivent rester observables via le routeur/app tests et les regles d'architecture via guard AST. |
| Baseline Snapshot | yes | la migration doit prouver avant/apres les imports auth et les exceptions auth. |
| Ownership Routing | yes | les containers auth doivent etre classes vers leur owner canonique. |
| Allowlist Exception | yes | la story retire deux exceptions exactes d'un registre existant sans wildcard. |
| Contract Shape | no | no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is changed. |
| Batch Migration | no | une seule tranche auth est migree; les autres domaines restent hors scope. |
| Reintroduction Guard | yes | le retour d'imports API auth sous `components` et des anciennes exceptions auth doit echouer. |
| Persistent Evidence | yes | les preuves avant/apres et la fermeture de tranche doivent etre conservees. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - Runtime artifact: React router/app behavior exercised by `npm run test -- App router`.
  - Runtime artifact: AST guard exercised by `npm run test -- component-architecture page-architecture`.
  - Runtime artifact: TypeScript module graph exercised by `npm run lint`.
- Secondary evidence:
  - targeted `rg` scans for removed component auth paths and stale allowlist entries.
- Why static scans alone are insufficient:
  - the move must preserve the mounted `/login` and `/register` behavior, not only remove old imports.
- Static scans alone are not sufficient:
  - the story must run route/form tests and AST guard tests because deleted path scans cannot prove login/register still work.
- Command:
  - `cd frontend && npm run test -- SignInForm SignUpForm App router component-architecture page-architecture`

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/auth-api-containers-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/auth-api-containers-after.md`
- Expected invariant:
  - `/login` et `/register` gardent les memes comportements auth; seules les
    suppressions des anciens fichiers auth sous `components` et de leurs
    exceptions sont autorisees.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Auth sign-in container | `frontend/src/features/auth/**` | `frontend/src/components/**` |
| Auth sign-up container | `frontend/src/features/auth/**` | `frontend/src/components/**` |
| Auth page route composition | `frontend/src/pages/LoginPage.tsx`, `frontend/src/pages/RegisterPage.tsx` | shared components as API owner |
| Auth API client contract | `frontend/src/api/auth.ts` and `@api` exports | duplicated feature-local API client |
| Access token persistence | `frontend/src/utils/authToken.ts` | duplicated feature-local token store |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `components/SignInForm.tsx` | `loginApi`, `AuthApiError` from `@api` | auth container currently under shared components | must be removed by this story |
| `components/SignUpForm.tsx` | `registerApi`, `AuthApiError` from `@api` | auth container currently under shared components | must be removed by this story |

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

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| baseline | `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/auth-api-containers-before.md` | imports auth avant |
| after | `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/auth-api-containers-after.md` | anciens chemins absents |
| final evidence | `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/generated/10-final-evidence.md` | consigne les commandes executees et leur resultat |

For audit-sourced stories, include at least one artifact or generated evidence entry that records source finding closure status and any remaining closure map.

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must prove an architecture guard fails if the removed or
forbidden surface is reintroduced. The existing `component-architecture` guard
may satisfy this requirement only if after-evidence proves it rejects stale auth
exceptions and old component imports; otherwise update the guard explicitly.

The guard must check at least one deterministic source:

- forbidden symbols or states

Required forbidden examples:

- `components/SignInForm.tsx` in `COMPONENT_API_IMPORT_EXCEPTIONS`
- `components/SignUpForm.tsx` in `COMPONENT_API_IMPORT_EXCEPTIONS`
- production import from `../components/SignInForm`
- production import from `../components/SignUpForm`

Guard evidence:

- Evidence profile: `reintroduction_guard`; run `npm run test -- component-architecture page-architecture`
  and `npm run test -- SignInForm SignUpForm App router`.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-components/2026-05-09-0031/02-finding-register.md#F-001`
- Closure proof required: before/after artifacts, diff
  `COMPONENT_API_IMPORT_EXCEPTIONS`, tests auth cibles, guard
  `component-architecture`, scans negatifs des anciens imports auth.
- Known residual in-domain work: none for `frontend/src/features/auth` after this story.
- Deferred non-domain concerns: enterprise/B2B, admin-ops/support,
  settings/privacy, layout auth provider ownership, dashboard summary,
  natal-chart, and `UpgradeCTA` type-only test remain outside this story.
- Remaining closure map:
  - enterprise/B2B: future `frontend-enterprise` story;
  - admin operations/support: future `frontend-admin-ops` story;
  - settings/privacy: future `frontend-settings` story;
  - layout auth state: future `frontend-layouts` story;
  - dashboard summary: future `frontend-dashboard` story;
  - natal interpretation: future `frontend-natal` story.
- Stop condition: both auth exceptions are removed, no production consumer imports
  auth forms from `frontend/src/components/**`, auth tests pass, and no unrelated
  component exception is modified.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/tests/component-architecture-allowlist.ts` -
  `components/SignInForm.tsx` and `components/SignUpForm.tsx` are exact API
  exceptions with owner `auth pages` and exit condition `Deplacer sous une feature auth`.
- Evidence 2: `frontend/src/pages/LoginPage.tsx` - the login route imports `SignInForm` from `../components/SignInForm`.
- Evidence 3: `frontend/src/pages/RegisterPage.tsx` - the register route imports `SignUpForm` from `../components/SignUpForm`.
- Evidence 4: `frontend/src/components/SignInForm.tsx` - the sign-in container imports `loginApi`, `AuthApiError`, `setAccessToken`, routing hooks, validation and UI primitives.
- Evidence 5: `frontend/src/components/SignUpForm.tsx` - the sign-up container
  imports `registerApi`, `AuthApiError`, analytics, pricing config, routing hooks,
  validation and `./SignUpForm.css`.
- Evidence 6: `frontend/src/tests/SignInForm.test.tsx` and `frontend/src/tests/SignUpForm.test.tsx` - tests import the forms from `../components/**`.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.
- Evidence 8: `_condamad/audits/frontend-components/2026-05-09-0031/01-evidence-log.md`
  - `E-001`, `E-003`, `E-011` and `E-013` prove current exceptions are exact,
  guarded and runtime-consumed.

## 6. Target State

After implementation:

- `SignInForm` and `SignUpForm` live under `frontend/src/features/auth/**` with their CSS colocated under the same auth owner.
- `LoginPage.tsx`, `RegisterPage.tsx` and auth tests import from the new auth feature owner.
- `COMPONENT_API_IMPORT_EXCEPTIONS` no longer contains `components/SignInForm.tsx` or `components/SignUpForm.tsx`.
- `frontend/src/components/SignInForm.tsx`, `frontend/src/components/SignUpForm.tsx`
  and `frontend/src/components/SignUpForm.css` no longer exist and are not replaced
  by re-export shims.
- The remaining non-auth component API exceptions are unchanged.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page architecture guards protect auth route placement under `AuthLayout`.
  - `RG-068` - layout hierarchy must keep login/register in the auth public family.
  - `RG-069` - component API/feature imports must not grow and retained hits must stay exact.
  - `RG-070` - component TypeScript suppressions must not be introduced while moving auth files.
- Non-applicable invariants:
  - `RG-071` - natal interpretation is outside the auth feature domain.
  - `RG-072` - unused component inventory is not the primary target, except for proving deleted auth component files are not retained as dead exports.
- Required regression evidence:
  - `npm run test -- component-architecture page-architecture SignInForm SignUpForm App router`
  - `npm run lint`
  - targeted `rg` scans listed in the validation plan.
- Allowed differences:
  - only auth form file paths/import paths and the removal of the two auth exceptions.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Auth forms move to `features/auth`; old component imports are gone. | Evidence profile: `repo_wide_negative_scan`; `rg -n "components/Sign(InForm|UpForm)" src`. |
| AC2 | Login/register behavior remains equivalent after the move. | Runtime evidence: `npm run test -- SignInForm SignUpForm App router`; `npm run lint`. |
| AC3 | Auth exceptions are removed. | Evidence profile: `allowlist_register_validated`; `npm run test -- component-architecture`; run A3 command in the Validation Plan. |
| AC4 | No old auth form remains under `components`. | Evidence profile: `no_legacy_contract`; `rg -n "Sign(In\|Up)Form" frontend/src/components`. |
| AC5 | Persistent evidence records auth closure. | Concrete validation command: run the `python` commands in the PERSISTENCE block of the Validation Plan. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture baseline evidence before edits (AC: AC1, AC3, AC5)
  - [ ] Record current imports, files and exceptions in `auth-api-containers-before.md`.
  - [ ] Include the exact `rg` commands used and classify only the auth tranche.

- [ ] Task 2 - Move auth containers to the feature owner (AC: AC1, AC2, AC4)
  - [ ] Create an auth feature structure under `frontend/src/features/auth/**`.
  - [ ] Move `SignInForm.tsx`, `SignUpForm.tsx` and `SignUpForm.css` into that owner.
  - [ ] Preserve existing imports to `@api`, `@i18n`, `@ui`, `@utils` or relative utilities according to existing aliases; do not duplicate API clients or token helpers.

- [ ] Task 3 - Repoint consumers and tests (AC: AC1, AC2)
  - [ ] Update `LoginPage.tsx` and `RegisterPage.tsx` to import from the auth feature owner.
  - [ ] Update `SignInForm.test.tsx` and `SignUpForm.test.tsx` imports.
  - [ ] Update any exact local imports discovered by the baseline scan.

- [ ] Task 4 - Retire auth exceptions and harden guard evidence (AC: AC3, AC4)
  - [ ] Remove only `components/SignInForm.tsx` and `components/SignUpForm.tsx` from `COMPONENT_API_IMPORT_EXCEPTIONS`.
  - [ ] Update `component-architecture-guards.test.ts` only if it needs a more explicit anti-return assertion for auth component paths.
  - [ ] Do not modify unrelated exception rows.

- [ ] Task 5 - Persist after evidence and validation (AC: AC1, AC2, AC3, AC4, AC5)
  - [ ] Record after scans in `auth-api-containers-after.md`.
  - [ ] Record final command results in `generated/10-final-evidence.md`.
  - [ ] If implementation establishes a durable auth invariant, add `RG-073` to `_condamad/stories/regression-guardrails.md` with an executable guard.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/api/auth.ts` and `@api` exports for auth HTTP calls;
  - `frontend/src/utils/authToken.ts` for token persistence;
  - `frontend/src/i18n/zod/auth.ts` for validation schemas;
  - `frontend/src/i18n/auth.ts` through `useTranslation("auth")`;
  - `frontend/src/components/ui/Field` and `frontend/src/components/ui/Button` for UI primitives.
- Do not recreate:
  - a feature-local `loginApi`, `registerApi`, `AuthApiError`, token store, pricing config or analytics hook.
- Shared abstraction allowed only if:
  - it removes duplicated logic between `SignInForm` and `SignUpForm` inside `frontend/src/features/auth/**`;
  - it has at least two concrete in-scope consumers;
  - it does not create a new shared `components` API owner.

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

- `frontend/src/components/SignInForm.tsx`
- `frontend/src/components/SignUpForm.tsx`
- `frontend/src/components/SignUpForm.css`
- `components/SignInForm.tsx` in `COMPONENT_API_IMPORT_EXCEPTIONS`
- `components/SignUpForm.tsx` in `COMPONENT_API_IMPORT_EXCEPTIONS`
- imports from `../components/SignInForm` or `../components/SignUpForm` in production code or tests

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

Auth removal classification for this story:

| Item | Required classification before deletion | Decision rule |
|---|---|---|
| `frontend/src/components/SignInForm.tsx` | `historical-facade` after consumers are repointed; otherwise `canonical-active` | delete after tests |
| `frontend/src/components/SignUpForm.tsx` | `historical-facade` after consumers are repointed; otherwise `canonical-active` | delete after tests |
| `frontend/src/components/SignUpForm.css` | `historical-facade` after CSS import is moved; otherwise `canonical-active` | delete after tests |

## 12. Removal Audit Format

Required audit table:

Allowed decisions in this audit: `keep`, `delete`, `replace-consumer`,
`needs-user-decision`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `SignInForm.tsx` | TSX | `canonical-active` before; `historical-facade` after | page/tests | `features/auth/SignInForm.tsx` | replace-consumer; delete | tests | login |
| `SignUpForm.tsx` | TSX | `canonical-active` before; `historical-facade` after | page/tests | `features/auth/SignUpForm.tsx` | replace-consumer; delete | tests | register |
| `SignUpForm.css` | CSS | `canonical-active` before; `historical-facade` after | form | `features/auth/SignUpForm.css` | replace-consumer; delete | lint | style |

Audit output path when applicable:

- `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/auth-api-containers-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Sign-in form API orchestration | `frontend/src/features/auth/**` | `frontend/src/components/SignInForm.tsx` |
| Sign-up form API orchestration | `frontend/src/features/auth/**` | `frontend/src/components/SignUpForm.tsx` |
| Auth route page composition | `frontend/src/pages/LoginPage.tsx`, `frontend/src/pages/RegisterPage.tsx` | shared component API ownership |

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

For this frontend app, blocker evidence is any first-party runtime import outside
`LoginPage.tsx`, `RegisterPage.tsx`, or local auth tests that still requires the
old component path.

## 17. Generated Contract Check

Generated contract check is required for this frontend removal story even though no backend OpenAPI or generated client should change.

Required generated-contract evidence:

- route manifest absence: `cd frontend && npm run test -- App router page-architecture`
  proves `/login` and `/register` remain registered canonically.
- generated client/schema absence: `cd frontend && npm run lint` proves the TypeScript module graph has no orphaned old auth imports.
- old path absence: `rg -n "components/Sign(In|Up)Form" frontend/src` returns no hits.
- OpenAPI path absence: no OpenAPI change is expected because no backend route,
  schema, or generated API client is modified; record this in final evidence.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/components/SignInForm.tsx`
- `frontend/src/components/SignUpForm.tsx`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/RegisterPage.tsx`
- `frontend/src/tests/SignInForm.test.tsx`
- `frontend/src/tests/SignUpForm.test.tsx`
- `frontend/vite.config.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/features/auth/SignInForm.tsx` - new canonical sign-in container path, or equivalent exact auth feature path.
- `frontend/src/features/auth/SignUpForm.tsx` - new canonical sign-up container path, or equivalent exact auth feature path.
- `frontend/src/features/auth/SignUpForm.css` - moved signup styles without inline style introduction.
- `frontend/src/pages/LoginPage.tsx` - import from auth feature owner.
- `frontend/src/pages/RegisterPage.tsx` - import from auth feature owner.
- `frontend/src/tests/component-architecture-allowlist.ts` - remove only the two auth exceptions.

Likely tests:

- `frontend/src/tests/SignInForm.test.tsx` - update import and preserve behavior assertions.
- `frontend/src/tests/SignUpForm.test.tsx` - update import and preserve behavior assertions.
- `frontend/src/tests/component-architecture-guards.test.ts` - update for an explicit auth anti-return guard when the current guard lacks that assertion.

Files not expected to change:

- `frontend/src/api/auth.ts` - API contract must not change.
- `frontend/src/utils/authToken.ts` - token persistence must not change.
- `frontend/src/app/routes.tsx` - auth route registration must not change unless a test proves an import-only adjustment is necessary.
- `backend/**` - backend auth behavior is outside scope.
- `frontend/src/components/ui/**` - UI primitives are reused, not changed.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- SignInForm SignUpForm App router
npm run test -- component-architecture page-architecture
npm run lint
# A3
rg -n "components/SignInForm.tsx" src/tests/component-architecture-allowlist.ts
rg -n "components/SignUpForm.tsx" src/tests/component-architecture-allowlist.ts
rg -n "components/SignInForm|components/SignUpForm|\\.\\./components/SignInForm|\\.\\./components/SignUpForm" src -g "*.ts" -g "*.tsx"
rg -n "export .*SignInForm|export .*SignUpForm" src/components -g "*.ts" -g "*.tsx"
```

All four `rg` commands in this block must return no hits after migration. If
`rg` exits with code `1` because there are zero matches, record that as PASS in
the after evidence.

PERSISTENCE block from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -c "from pathlib import Path; b=Path('_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth'); assert (b/'auth-api-containers-before.md').exists()"
python -c "from pathlib import Path; b=Path('_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth'); assert (b/'auth-api-containers-after.md').exists()"
python -c "from pathlib import Path; b=Path('_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth'); assert (b/'generated/10-final-evidence.md').exists()"
```

Story contract validation before implementation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py `
  --explain-contracts `
  _condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md
```

## 22. Regression Risks

- Risk: auth route behavior changes while only imports were intended to move.
  - Guardrail: `SignInForm`, `SignUpForm`, `App`, `router` tests plus lint.
- Risk: component API allowlist is weakened or unrelated exceptions are edited.
  - Guardrail: `component-architecture` test and exact diff review of `component-architecture-allowlist.ts`.
- Risk: a compatibility re-export hides the old component path.
  - Guardrail: `Test-Path` checks and targeted `rg` scans under `frontend/src/components`.
- Risk: auth route placement regresses outside `AuthLayout`.
  - Guardrail: `page-architecture` tests protecting `RG-064` and `RG-068`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work for the auth tranche.
- Keep all new or moved TSX/CSS files free of inline styles; use the moved CSS file or existing CSS variables/classes.
- Preserve French file-level comments and public/non-trivial docstrings/comments where the existing project convention requires them.

## 24. References

- `_condamad/audits/frontend-components/2026-05-09-0031/02-finding-register.md#F-001` - source remain and closure decision.
- `_condamad/audits/frontend-components/2026-05-09-0031/01-evidence-log.md` - current exact exception evidence.
- `_condamad/audits/frontend-components/2026-05-09-0031/03-story-candidates.md` - confirms this is deferred non-component feature/page work.
- `_condamad/stories/CS-113-classer-converger-composants-consommateurs-api/component-api-ownership.md` - prior owner decisions and exit conditions.
- `_condamad/stories/regression-guardrails.md` - applicable invariants `RG-064`, `RG-068`, `RG-069`, `RG-070`, `RG-071`, `RG-072`.
- `frontend/src/tests/component-architecture-allowlist.ts` - executable exception register to reduce.
