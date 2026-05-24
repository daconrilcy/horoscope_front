# Story CS-270 internal-role-model: Define Internal Role Model
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-270-define-internal-role-model-admin-marketer-techno-astro-expert.md`.
- Related dependency: CS-255 for current product surfaces.
- Related dependency: CS-267 for the first admin audit surface.
- Future dependency: CS-271 must define the permission matrix after this role vocabulary is stable.
- Existing owner found: `backend/app/core/rbac.py` currently exposes active roles as lowercase runtime values.
- Existing owner found: `docs/admin-implementation-overview.md` states that `/admin` is currently admin-only.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: internal admin surfaces need a target role vocabulary without granting access to future roles.
- Source-alignment evidence: PASS; the story preserves role definitions, B2C/B2B separation, current admin-only state and future RBAC dependency.

## Objective

Define one canonical internal role model document for `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT`.

The implementation must document the target vocabulary and future permission implications without activating new roles, modifying authentication,
creating accounts, changing migrations, or opening access to non-admin actors.

## Target State

- `docs/architecture/internal-role-model.md` exists and starts with a French global file comment.
- The document defines `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT` with their business intent.
- `ADMIN` is documented as the only currently active operational internal role with full admin access.
- `MARKETER`, `TECHNO` and `ASTRO_EXPERT` are documented as target roles with no current access grant.
- Internal roles are explicitly separated from B2C customers and B2B accounts.
- Admin-related surfaces are identified from current product and admin documentation without changing routes.
- Future permission matrix implications are listed as an input to CS-271.
- No RBAC implementation, auth change, account creation, migration, frontend UI or API exposure is introduced by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-270-define-internal-role-model-admin-marketer-techno-astro-expert.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-270`.
- Evidence 3: `backend/app/core/rbac.py` - current active backend roles inspected.
- Evidence 4: `docs/admin-implementation-overview.md` - current admin-only access and admin surfaces inspected.
- Evidence 5: `docs/architecture/product-architecture-current-state-2026-05-24.md` - current product architecture surface was discoverable.
- Evidence 6: `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md` - future matrix dependency found.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 8: `resolve_guardrails.py` - scoped resolver run for backend-domain, documentation contract and role-model scope.
- Repository structure alert: backend, frontend, docs and expected story roots exist in this workspace.
- Source-alignment evidence: PASS; no brief stake was narrowed into implementation or generic cleanup work.

## Domain Boundary

- Domain: documentation-architecture
- In scope:
  - Canonical internal role model documentation under `docs/architecture`.
  - Business intent for `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT`.
  - Separation between internal roles, B2C customers and B2B accounts.
  - Current active state documenting `ADMIN` as the only operational internal role.
  - Future permission implications and CS-271 dependency.
  - Static and targeted backend checks proving no access activation is introduced.
- Out of scope:
  - Frontend UI, DB schema, auth redesign, i18n, styling, build tooling, migrations, seeds, generated clients and public API changes.
  - Full RBAC implementation, account creation, route protection changes and real access grants for future roles.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No endpoint, serializer, route, model, repository, migration, user seed, token claim redesign or UI permission screen.
  - No activation of `MARKETER`, `TECHNO` or `ASTRO_EXPERT`.
  - No client B2C or B2B role conversion into internal staff roles.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a documentation-only internal role governance contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `docs/architecture/internal-role-model.md`, targeted contract tests and story evidence artifacts.
  - Keep runtime authorization behavior unchanged.
  - Keep `MARKETER`, `TECHNO` and `ASTRO_EXPERT` as target-only role vocabulary.
  - Keep B2C and B2B subject models distinct from internal staff roles.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to activate future roles before CS-271 defines the permission matrix.
- Additional validation rules:
  - The document must name all four internal roles exactly.
  - The document must state that only `ADMIN` is currently operational.
  - The document must state that future roles grant no access until RBAC is implemented.
  - The document must separate internal roles from B2C customers and B2B accounts.
  - The document must list dependencies toward the future permission matrix.
  - `pytest` and `python` checks must prove current backend active roles do not include future target roles.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `backend/app/core/rbac.py`, `AST guard`, `python` and `pytest` prove active backend role state. |
| Baseline Snapshot | yes | Before and after evidence prove documentation and tests do not activate target roles. |
| Ownership Routing | yes | Role model documentation, RBAC code and future permission matrix need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation contract story. |
| Contract Shape | yes | The role model has exact roles, active-state rules, subject separation and future implications. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Future role activation, auth changes and client-role confusion must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The internal role model document exists. | Evidence profile: baseline_before_after_diff; `python` checks `docs/architecture/internal-role-model.md`. |
| AC2 | The four internal roles are defined. | Evidence profile: json_contract_shape; `rg` checks `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT`. |
| AC3 | `ADMIN` is the only active internal role. | Evidence profile: ast_architecture_guard; `python` checks `backend/app/core/rbac.py` role constants. |
| AC4 | Future roles grant no current access. | Evidence profile: external_usage_blocker; `pytest -q backend/tests/unit/test_internal_role_model_contract.py`. |
| AC5 | B2C subjects are separate from internal roles. | Evidence profile: json_contract_shape; `rg` checks B2C separation wording in the document. |
| AC6 | B2B subjects are separate from internal roles. | Evidence profile: json_contract_shape; `rg` checks B2B separation wording in the document. |
| AC7 | Admin surfaces are identified. | Evidence profile: json_contract_shape; `rg` checks admin dashboard, audit, content, logs and support surfaces. |
| AC8 | Permission matrix dependency is listed. | Evidence profile: external_usage_blocker; `rg` checks CS-271 and permission matrix wording. |
| AC9 | Route surfaces remain unchanged. | Evidence profile: ast_architecture_guard; `AST guard`; `python` records scoped status output. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-270 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, current RBAC role set and admin implementation overview before writing the document. (AC: AC1, AC3, AC7)
- [ ] Task 2: Create `docs/architecture/internal-role-model.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT` with distinct business intent. (AC: AC2)
- [ ] Task 4: State that `ADMIN` is the only currently active operational internal role. (AC: AC3)
- [ ] Task 5: State that future roles grant no access until RBAC is implemented. (AC: AC4)
- [ ] Task 6: Separate B2C customers and B2B accounts from internal staff roles. (AC: AC5, AC6)
- [ ] Task 7: List the current admin surfaces concerned by future permission slicing. (AC: AC7)
- [ ] Task 8: Link the future permission matrix dependency to CS-271. (AC: AC8)
- [ ] Task 9: Add a targeted contract test for the document and inactive future roles. (AC: AC3, AC4, AC9)
- [ ] Task 10: Persist validation and scoped status evidence under the CS-270 evidence folder. (AC: AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-270-define-internal-role-model-admin-marketer-techno-astro-expert.md` - source brief.
- `backend/app/core/rbac.py` - current active backend role registry.
- `docs/admin-implementation-overview.md` - current admin route, guard and surface overview.
- `docs/architecture/product-architecture-current-state-2026-05-24.md` - product surface context.
- `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md` - future matrix dependency.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/core/rbac.py` for current active backend role values.
  - `docs/admin-implementation-overview.md` for the current `/admin` surface and admin-only behavior.
  - `AST guard`, `pytest`, `python`, scoped `git status` and targeted `rg` scans for inactive future-role proof.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/internal-role-model.md`.
- Static scans alone are not sufficient because:
  - The current active role set must be checked from backend source with deterministic Python and test evidence.

## Contract Shape

- Contract type:
  - Markdown architecture governance document for internal staff roles.
- Fields:
  - `role_code`: one of `ADMIN`, `MARKETER`, `TECHNO` or `ASTRO_EXPERT`.
  - `business_intent`: concise purpose of the internal role.
  - `current_state`: `active` only for `ADMIN`, `target-only` for the three future roles.
  - `access_grant`: current access rule, with no grant for target-only roles.
  - `subject_boundary`: separation from B2C customers and B2B accounts.
  - `surface_family`: admin dashboard, audit, content, logs, support, technical diagnostics or astrology expertise.
  - `future_permission_dependency`: dependency on CS-271 permission matrix.
- Required fields:
  - `role_code`
  - `business_intent`
  - `current_state`
  - `access_grant`
  - `subject_boundary`
  - `surface_family`
  - `future_permission_dependency`
- Optional fields:
  - none.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - none; this story writes documentation and contract tests only.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - none; `app.openapi()` is unchanged because no API route is added.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-270-define-internal-role-model-admin-marketer-techno-astro-expert.md`
  - `backend/app/core/rbac.py`
  - `docs/admin-implementation-overview.md`
  - `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md`
- Comparison after implementation:
  - `docs/architecture/internal-role-model.md`
  - `backend/tests/unit/test_internal_role_model_contract.py`
  - `_condamad/stories/CS-270-internal-role-model/evidence/validation.txt`
  - `_condamad/stories/CS-270-internal-role-model/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture document, one targeted contract test and CONDAMAD evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Internal role vocabulary | `docs/architecture/internal-role-model.md` | route code or frontend guards |
| Current active backend roles | `backend/app/core/rbac.py` | documentation-only invented runtime list |
| Admin surface inventory | `docs/admin-implementation-overview.md` | duplicated UI route registry |
| Future permission matrix | CS-271 story and its contract artifact | this role vocabulary story |
| Story evidence artifacts | `_condamad/stories/CS-270-internal-role-model/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the current backend active role registry instead of inventing a second operational role list.
- Reuse `docs/admin-implementation-overview.md` for admin surfaces instead of duplicating the complete admin implementation overview.
- Reuse CS-255 and CS-267 context only as surface inputs, not as new product decisions.
- Keep one canonical internal role model document.
- Do not add external packages, duplicate permission matrices, generated clients or parallel admin access registries.

## No Legacy / Forbidden Paths

- No legacy role path may be added.
- No compatibility role path may be added.
- No fallback branch may grant access to target-only roles.
- Do not create aliases, shims, compatibility wrappers or parallel role documents.
- Do not add `MARKETER`, `TECHNO` or `ASTRO_EXPERT` to active backend role constants in this story.
- Do not modify auth dependencies, route guards, migrations, seeds, frontend admin guards or account creation flows.

## Reintroduction Guard

- Forbidden role activation:
  - `MARKETER`
  - `TECHNO`
  - `ASTRO_EXPERT`
- Forbidden surface changes:
  - auth dependency changes
  - route guard changes
  - migration or seed changes
  - frontend admin guard changes
- Required guards:
  - `python` checks current backend role constants for absent target-only roles.
  - `pytest -q backend/tests/unit/test_internal_role_model_contract.py` proves the document and inactive target-role contract.
  - `rg` checks the role model document for B2C/B2B separation and CS-271 dependency.
  - `git status --short -- backend/app frontend/src backend/migrations` proves scoped application surface neutrality.

## Regression Guardrails

Scope vector:

- documentation-architecture: yes;
- internal role model: yes;
- backend active role registry: read-only;
- frontend implementation: no;
- DB/migration/auth/i18n/style/build: no;
- future target role activation: forbidden.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Backend API ownership remains untouched by the documentation story. | scoped `git status`; `python`. |
| Registry gap | No exact internal role model guardrail exists in resolver output. | Story-local role and auth guards. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story documents internal staff roles, not product entitlements.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-270-internal-role-model/evidence/validation.txt` | Keep validation transcript. |
| Application surface status | `_condamad/stories/CS-270-internal-role-model/evidence/app-surface-status.txt` | Prove scoped app changes. |
| Source checklist | `_condamad/stories/CS-270-internal-role-model/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-270-internal-role-model/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this documentation contract story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/internal-role-model.md` - define the canonical internal role model.
- `backend/tests/unit/test_internal_role_model_contract.py` - cover document content and inactive future role checks.
- `_condamad/stories/CS-270-internal-role-model/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-270-internal-role-model/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-270-internal-role-model/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/tests/unit/test_internal_role_model_contract.py` - document, backend role registry and target-only role contract checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence schema is created.
- `backend/app/api/**` - out of scope; no route or auth dependency is touched.
- `backend/app/core/security.py` - out of scope; no token or auth behavior is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "ADMIN|MARKETER|TECHNO|ASTRO_EXPERT|rôle interne|B2C|B2B" .\docs .\_story_briefs`
- VC2: `rg -n "ADMIN|MARKETER|TECHNO|ASTRO_EXPERT|target-only|seul rôle actif" docs/architecture/internal-role-model.md`
- VC3: `rg -n "B2C|B2B|clients|comptes entreprise|rôles internes" docs/architecture/internal-role-model.md`
- VC4: `rg -n "dashboard|audit|content|logs|support|diagnostics|expertise astrologique" docs/architecture/internal-role-model.md`
- VC5: `rg -n "CS-271|matrice de permissions|permission matrix" docs/architecture/internal-role-model.md`
- VC6: `pytest -q backend/tests/unit/test_internal_role_model_contract.py`
- VC7: `python -c "from pathlib import Path; p=Path('backend/app/core/rbac.py'); t=p.read_text(); assert 'MARKETER' not in t and 'TECHNO' not in t"`
- VC8: `python -c "from pathlib import Path; p=Path('backend/app/core/rbac.py'); assert 'ASTRO_EXPERT' not in p.read_text()"`
- VC9: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-270-internal-role-model/evidence/validation.txt').exists()"`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-270-internal-role-model/evidence/app-surface-status.txt').exists()"`
- VC11: `git status --short -- backend/app frontend/src`
- VC12: `ruff format .`
- VC13: `ruff check .`
- VC14: `pytest -q`

Before VC6 through VC10, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The target role vocabulary may be interpreted as active authorization behavior.
- B2C customers or B2B accounts may be confused with internal staff roles.
- Future permission implications may become a hidden RBAC implementation inside this story.
- Admin surfaces may remain indistinct because the role model does not name the affected families.
- Application files may change while trying to prove the documentation contract.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before every Python command.
- Keep backend runtime behavior unchanged.
- Keep `MARKETER`, `TECHNO` and `ASTRO_EXPERT` out of active backend role constants.
- Keep B2C and B2B subject models separate from internal staff roles.
- Persist validation output under the CS-270 evidence folder before requesting review.

## References

- `_story_briefs/cs-270-define-internal-role-model-admin-marketer-techno-astro-expert.md`
- `backend/app/core/rbac.py`
- `docs/admin-implementation-overview.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md`
- `_condamad/stories/regression-guardrails.md`
