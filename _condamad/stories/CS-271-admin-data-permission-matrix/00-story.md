# Story CS-271 admin-data-permission-matrix: Define Permission Matrix For Admin Data Domains
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md`.
- Required dependency: CS-270 internal role model.
- Existing owner found: `docs/admin-implementation-overview.md` describes current admin-only access and admin surface families.
- Existing owner found: `backend/app/core/rbac.py` exposes active runtime roles and does not activate future target staff roles.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: future admin API stories need a restrictive target permission matrix before marketer, technical and astrology expert roles exist.
- Source-alignment evidence: PASS; the story preserves role/domain/action/masking/open-decision stakes without activating RBAC.

## Objective

Define one canonical target permission matrix for admin data domains: business, technical, astrology and debug data.

The implementation must document domains, actions, masking rules and open decisions while keeping `ADMIN` as the only operational role until RBAC
is implemented.

## Target State

- `docs/architecture/admin-permission-matrix.md` exists and starts with a French global file comment.
- The document defines a role x domain matrix for `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT`.
- The data domains include business, technical, astrology and debug families.
- Birth data is documented as sensitive and masked outside explicitly approved admin contexts.
- Traces, prompts and replay data are classified as separate debug/technical surfaces.
- Matrix actions cover read, search, export, replay and correct.
- `MARKETER`, `TECHNO` and `ASTRO_EXPERT` are target roles with no current access grant.
- Open permission decisions are listed in a dedicated section.
- B2C client access is explicitly excluded from this admin permission matrix.
- No RBAC implementation, auth change, route change, frontend UI, database migration or public client behavior change is introduced.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-271`.
- Evidence 3: `_condamad/stories/CS-270-internal-role-model/00-story.md` - dependency story read for role vocabulary and inactive target roles.
- Evidence 4: `backend/app/core/rbac.py` - current active backend role registry inspected.
- Evidence 5: `docs/admin-implementation-overview.md` - admin-only access and admin surface families inspected.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 7: `resolve_guardrails.py` - scoped resolver run for backend-domain, permission-matrix and documentation contracts.
- Repository structure alert: backend, backend/app, backend/tests, frontend, frontend/src and docs exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was dropped or replaced by generic cleanup work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical admin permission matrix documentation under `docs/architecture`.
  - Role x domain rules for `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT`.
  - Data classification for business, technical, astrology and debug data.
  - Masking rules for birth data, technical traces, prompts and replay payloads.
  - Action coverage for read, search, export, replay and correct.
  - Open permission decisions and future RBAC dependency.
  - Static and targeted backend checks proving no access activation is introduced.
- Out of scope:
  - Frontend UI, DB schema, auth redesign, i18n, styling, build tooling, migrations, seeds, generated clients and public API changes.
  - Full RBAC implementation, account creation, route protection changes and real access grants for future roles.
  - Client B2C permission behavior and B2B account-role modeling.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No endpoint, serializer, route, model, repository, migration, user seed, token claim redesign or UI permission screen.
  - No activation of `MARKETER`, `TECHNO` or `ASTRO_EXPERT`.
  - No final RGPD retention decision.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a documentation-only permission matrix governance contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `docs/architecture/admin-permission-matrix.md`, targeted contract tests and story evidence artifacts.
  - Keep runtime authorization behavior unchanged.
  - Keep `MARKETER`, `TECHNO` and `ASTRO_EXPERT` as target-only role vocabulary.
  - Keep B2C client access outside the admin permission matrix.
  - Keep uncertain permissions visible as open decisions.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to grant access to future roles before RBAC is implemented.
- Additional validation rules:
  - The document must define a matrix crossing roles with business, technical, astrology and debug data domains.
  - The document must state that only `ADMIN` currently has operational admin access.
  - The document must state that future roles grant no access until RBAC is implemented.
  - The document must classify birth data as sensitive.
  - The document must classify traces, prompts and replay separately.
  - The document must cover read, search, export, replay and correct actions.
  - The document must list open permission decisions.
  - `pytest`, `python` and `rg` checks must prove the matrix exists without activating future roles.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `backend/app/core/rbac.py`, `AST guard`, `python` and `pytest` prove active backend role state. |
| Baseline Snapshot | yes | Before and after evidence prove documentation and tests do not activate target roles. |
| Ownership Routing | yes | Permission matrix documentation, RBAC code and admin surfaces need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this permission matrix story. |
| Contract Shape | yes | The matrix has exact roles, domains, actions, masking rules and open decisions. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Future role activation, auth changes and B2C exposure must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The permission matrix document exists. | Evidence profile: baseline_before_after_diff; `python` checks `docs/architecture/admin-permission-matrix.md`. |
| AC2 | The four internal roles appear in the matrix. | Evidence profile: json_contract_shape; `rg` checks `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT`. |
| AC3 | The four data domains are classified. | Evidence profile: json_contract_shape; `rg` checks business, technical, astrology and debug domain headings. |
| AC4 | Birth data is marked sensitive. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_admin_permission_matrix_contract.py`. |
| AC5 | Debug data categories are separated. | Evidence profile: json_contract_shape; `rg` checks trace, prompt and replay rows. |
| AC6 | Matrix actions are complete. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_admin_permission_matrix_contract.py`. |
| AC7 | Future roles grant no current access. | Evidence profile: external_usage_blocker; `pytest -q backend/tests/unit/test_admin_permission_matrix_contract.py`. |
| AC8 | B2C client access is excluded. | Evidence profile: json_contract_shape; `rg` checks B2C exclusion wording in the document. |
| AC9 | Open permission decisions are listed. | Evidence profile: baseline_before_after_diff; `rg` checks open decision markers in the document. |
| AC10 | Runtime role state remains unchanged. | Evidence profile: ast_architecture_guard; `AST guard`; `python` checks `backend/app/core/rbac.py`. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-271 evidence paths. |

## Implementation Tasks

- [x] Task 1: Inspect the brief, CS-270, current RBAC role set and admin implementation overview before writing the matrix. (AC: AC1, AC7, AC10)
- [x] Task 2: Create `docs/architecture/admin-permission-matrix.md` with a French global file comment. (AC: AC1)
- [x] Task 3: Define matrix rows for `ADMIN`, `MARKETER`, `TECHNO` and `ASTRO_EXPERT`. (AC: AC2, AC7)
- [x] Task 4: Classify business, technical, astrology and debug data domains. (AC: AC3)
- [x] Task 5: Mark birth data as sensitive with explicit masking rules. (AC: AC4)
- [x] Task 6: Classify traces, prompts and replay as separate surfaces. (AC: AC5)
- [x] Task 7: Cover read, search, export, replay and correct action semantics. (AC: AC6)
- [x] Task 8: Exclude B2C client access from the admin permission matrix. (AC: AC8)
- [x] Task 9: Add a dedicated open-decisions section for uncertain permissions. (AC: AC9)
- [x] Task 10: Add a targeted contract test for the matrix and inactive future roles. (AC: AC2, AC6, AC7, AC10)
- [x] Task 11: Persist validation and scoped status evidence under the CS-271 evidence folder. (AC: AC10, AC11)

## Files to Inspect First

- `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md` - source brief.
- `_condamad/stories/CS-270-internal-role-model/00-story.md` - role vocabulary dependency.
- `backend/app/core/rbac.py` - current active backend role registry.
- `docs/admin-implementation-overview.md` - current admin-only access and surface overview.
- `docs/architecture/internal-role-model.md` - expected role model document from CS-270 after implementation.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/core/rbac.py` for current active backend role values.
  - `docs/admin-implementation-overview.md` for the current `/admin` surface and admin-only behavior.
  - `AST guard`, `pytest`, `python`, scoped `git status` and targeted `rg` scans for inactive future-role proof.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/admin-permission-matrix.md`.
  - `pytest -q backend/tests/unit/test_admin_permission_matrix_contract.py` for matrix content and runtime neutrality.
- Static scans alone are not sufficient because:
  - The current active role set must be checked from backend source with deterministic Python and test evidence.

## Contract Shape

- Contract type:
  - Markdown architecture governance document for admin data permissions.
- Fields:
  - `role_code`: one of `ADMIN`, `MARKETER`, `TECHNO` or `ASTRO_EXPERT`.
  - `data_domain`: business, technical, astrology or debug.
  - `data_category`: concrete family such as birth data, billing, traces, prompts or replay.
  - `action`: read, search, export, replay or correct.
  - `current_access`: current operational grant, with access only for `ADMIN`.
  - `target_access`: future target permission state.
  - `masking_rule`: visible, masked, aggregated, denied or open decision.
  - `decision_status`: decided or open.
  - `rbac_activation_state`: inactive for future roles until RBAC exists.
- Required fields:
  - `role_code`
  - `data_domain`
  - `data_category`
  - `action`
  - `current_access`
  - `target_access`
  - `masking_rule`
  - `decision_status`
  - `rbac_activation_state`
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
  - `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md`
  - `_condamad/stories/CS-270-internal-role-model/00-story.md`
  - `backend/app/core/rbac.py`
  - `docs/admin-implementation-overview.md`
- Comparison after implementation:
  - `docs/architecture/admin-permission-matrix.md`
  - `backend/tests/unit/test_admin_permission_matrix_contract.py`
  - `_condamad/stories/CS-271-admin-data-permission-matrix/evidence/validation.txt`
  - `_condamad/stories/CS-271-admin-data-permission-matrix/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture document, one targeted contract test and CONDAMAD evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin permission matrix | `docs/architecture/admin-permission-matrix.md` | route code or frontend guards |
| Current active backend roles | `backend/app/core/rbac.py` | documentation-only invented runtime list |
| Admin surface inventory | `docs/admin-implementation-overview.md` | duplicated UI route registry |
| Internal role vocabulary | `docs/architecture/internal-role-model.md` | permission matrix rows |
| Story evidence artifacts | `_condamad/stories/CS-271-admin-data-permission-matrix/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-270 role vocabulary instead of defining a parallel internal role model.
- Reuse the current backend active role registry instead of inventing a second operational role list.
- Reuse `docs/admin-implementation-overview.md` for admin surface families instead of duplicating the complete overview.
- Keep one canonical admin permission matrix document.
- Do not add external packages, duplicate permission matrices, generated clients or parallel admin access registries.

## No Legacy / Forbidden Paths

- No legacy permission path may be added.
- No compatibility permission path may be added.
- No fallback branch may grant access to target-only roles.
- Do not create aliases, shims, compatibility wrappers or parallel permission documents.
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
  - B2C client permission changes
- Required guards:
  - `python` checks current backend role constants for absent target-only roles.
  - `pytest -q backend/tests/unit/test_admin_permission_matrix_contract.py` proves the matrix and inactive target-role contract.
  - `rg` checks the matrix document for domains, actions, masking, B2C exclusion and open decisions.
  - `git status --short -- backend/app frontend/src backend/migrations` proves scoped application surface neutrality.

## Regression Guardrails

Scope vector:

- backend-domain: yes;
- documentation architecture: yes;
- admin permission matrix: yes;
- backend active role registry: read-only;
- frontend implementation: no;
- DB/migration/auth/i18n/style/build: no;
- future target role activation: forbidden.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Backend API ownership remains untouched by the documentation story. | scoped `git status`; `python`. |
| RG-020 `Taxonomie LLM consultation specifique` | Protected/admin data access must not change without explicit route work. | `rg`; targeted `pytest`. |
| RG-022 `Plans de validation des stories prompt-generation` | Prompt and replay data classification needs targeted validation evidence. | `rg`; targeted `pytest`. |
| Registry gap | No exact admin permission matrix guardrail exists in resolver output. | Story-local matrix guards. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story documents admin data permissions, not product entitlements.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-271-admin-data-permission-matrix/evidence/validation.txt` | Keep validation transcript. |
| Application surface status | `_condamad/stories/CS-271-admin-data-permission-matrix/evidence/app-surface-status.txt` | Prove scoped app changes. |
| Source checklist | `_condamad/stories/CS-271-admin-data-permission-matrix/evidence/source-checklist.md` | Record source coverage. |
| Review output | `_condamad/stories/CS-271-admin-data-permission-matrix/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this permission matrix story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/admin-permission-matrix.md` - define the canonical admin data permission matrix.
- `backend/tests/unit/test_admin_permission_matrix_contract.py` - cover document content and inactive future role checks.
- `_condamad/stories/CS-271-admin-data-permission-matrix/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-271-admin-data-permission-matrix/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-271-admin-data-permission-matrix/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/tests/unit/test_admin_permission_matrix_contract.py` - matrix, backend role registry and target-only role contract checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence schema is created.
- `backend/app/api/**` - out of scope; no route or auth dependency is touched.
- `backend/app/core/security.py` - out of scope; no token or auth behavior is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "matrice|permission|business|technical|astrology|debug|données de naissance|replay" .\docs .\_story_briefs`
- VC2: `rg -n "ADMIN|MARKETER|TECHNO|ASTRO_EXPERT|RBAC|non actif" docs/architecture/admin-permission-matrix.md`
- VC3: `rg -n "business|technical|astrology|debug" docs/architecture/admin-permission-matrix.md`
- VC4: `rg -n "données de naissance|birth data|sensible|masqu" docs/architecture/admin-permission-matrix.md`
- VC5: `rg -n "trace|prompt|replay|rejouer" docs/architecture/admin-permission-matrix.md`
- VC6: `rg -n "lire|rechercher|exporter|rejouer|corriger|open decision|décision ouverte" docs/architecture/admin-permission-matrix.md`
- VC7: `pytest -q backend/tests/unit/test_admin_permission_matrix_contract.py`
- VC8: `python -c "from pathlib import Path; p=Path('backend/app/core/rbac.py'); t=p.read_text(); assert 'MARKETER' not in t and 'TECHNO' not in t"`
- VC9: `python -c "from pathlib import Path; p=Path('backend/app/core/rbac.py'); assert 'ASTRO_EXPERT' not in p.read_text()"`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-271-admin-data-permission-matrix/evidence/validation.txt').exists()"`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-271-admin-data-permission-matrix/evidence/app-surface-status.txt').exists()"`
- VC12: `git status --short -- backend/app frontend/src`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q`

Before VC7 through VC11, VC13, VC14 and VC15, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The target permission matrix may be interpreted as active authorization behavior.
- Future roles may receive broader default access than intended.
- Birth data, prompts, traces or replay payloads may be exposed without masking rules.
- B2C client access may be confused with internal admin permissioning.
- Open decisions may be hidden inside prose instead of being explicit blockers for future API stories.
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
- Keep B2C client access outside the admin permission matrix.
- Persist validation output under the CS-271 evidence folder before requesting review.

## References

- `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md`
- `_condamad/stories/CS-270-internal-role-model/00-story.md`
- `backend/app/core/rbac.py`
- `docs/admin-implementation-overview.md`
- `_condamad/stories/regression-guardrails.md`
