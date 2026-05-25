# Story CS-283 b2c-projection-entitlement-policy: Define B2C Projection Entitlement Policy
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-283-define-b2c-projection-entitlement-policy.md`.
- Related dependency: CS-256 defines `structured_facts_v1` as the stable factual projection.
- Related dependency: CS-257 defines `beginner_summary_v1` as the deterministic B2C beginner projection.
- Related dependency: CS-258 defines `client_interpretation_projection_v1` by B2C plan depth.
- Related dependency: CS-259 defines `narrative_answer_audit_v1` for narrative answer audit triggers.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` owns public projection governance.
- Existing owner found: `backend/app/services/entitlement/**` owns current entitlement service vocabulary.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: B2C projection access lacks one readable policy matrix for free, basic and premium plans.
- Source-alignment evidence: PASS; ACs preserve plan mapping, internal projection denial, plan error control and AI audit triggers.

## Objective

Define one canonical backend-domain policy document for B2C projection entitlements across free, basic and premium plans.

The implementation must formalize the authorized projection matrix, denied internal projections, plan-insufficient error shape, AI audit triggers and
existing quota linkage without implementing payment, B2B API, frontend behavior, new runtime exposure or persistence.

## Target State

- One policy document maps each authorized B2C projection to free, basic and premium access.
- `structured_facts_v1`, `beginner_summary_v1` and `client_interpretation_projection_v1` are classified by plan access and content depth.
- Internal projections remain denied to B2C clients, including expert, admin, debug, raw runtime, prompt and audit payload surfaces.
- The policy defines a controlled `plan_insufficient` error with required fields and no technical payload exposure.
- Basic, premium, long and sensitive narrative answers trigger `narrative_answer_audit_v1` audit policy.
- Existing quota or limit decisions are referenced only when an existing product decision is found.
- No route, serializer, frontend, payment, B2B API, DB table, migration, prompt or provider integration is created by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-283-define-b2c-projection-entitlement-policy.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-283`.
- Evidence 3: `docs/architecture/official-product-primitives-public-projections.md` - public projection owner found.
- Evidence 4: `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - factual projection dependency read.
- Evidence 5: `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md` - beginner projection dependency read.
- Evidence 6: `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md` - plan depth dependency read.
- Evidence 7: `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - audit contract dependency read.
- Evidence 8: `backend/app/services/entitlement/**` - targeted search found existing entitlement service ownership.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Evidence 10: `resolve_guardrails.py` - scoped resolver run for backend-domain entitlement policy and projection matrix scope.
- Source-alignment evidence: PASS; the story answers every brief stake without turning access policy into route, payment or frontend work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical B2C projection entitlement policy documentation.
  - Matrix for free, basic and premium access to authorized client projections.
  - Denial policy for internal projections and technical runtime surfaces.
  - Controlled plan-insufficient error contract for future API authorization tests.
  - AI audit trigger rules for basic, premium, long and sensitive narrative answers.
  - Existing quota and limit decision linkage when a prior product contract exists.
  - Persistent evidence artifacts for policy validation scans.
- Out of scope:
  - Frontend UI, payment implementation, B2B API, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Runtime projection builder, route, serializer, entitlement middleware, provider call, prompt template and persistence implementation.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or API contract for a new entitlement route.
  - No payment system, Stripe plan mutation, B2B entitlement API, database table or migration.
  - No exposure of expert, admin, debug, raw runtime, prompt or audit payload projections to B2C clients.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain entitlement policy contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the B2C projection entitlement policy documentation, product registry alignment and story evidence artifacts.
  - Reuse CS-256, CS-257, CS-258 and CS-259 projection and audit terminology.
  - Reuse existing entitlement service and billing plan vocabulary for free, basic and premium.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep internal projections and technical runtime payloads outside B2C entitlement surfaces.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose internal projections to B2C clients or to create quotas without an existing product decision.
- Additional validation rules:
  - The policy must name `free`, `basic` and `premium` exactly.
  - The policy must map `structured_facts_v1`, `beginner_summary_v1` and `client_interpretation_projection_v1`.
  - The policy must list internal projections denied to B2C clients.
  - The policy must define `plan_insufficient` with stable fields for future API authorization tests.
  - The policy must require `narrative_answer_audit_v1` for basic, premium, long and sensitive answers.
  - The policy must reference existing quotas or state that quota creation requires a separate product decision.
  - `app.routes`, `app.openapi()`, `pytest` and scoped `git status` prove no public API or application surface drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing projection docs, entitlement owners, `app.routes`, `app.openapi()` and `pytest` prove source boundaries. |
| Baseline Snapshot | yes | Before and after evidence must prove one policy document, registry alignment and no app-surface drift. |
| Ownership Routing | yes | Projection contracts, entitlement policy, future route checks and audit triggers need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this policy documentation story. |
| Contract Shape | yes | The policy has exact plans, projection matrix, denial set, error shape and audit triggers. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Internal projection exposure and route-level plan logic must stay out of this story. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The B2C entitlement policy is documented. | Evidence profile: baseline_before_after_diff; `python` checks the policy document path. |
| AC2 | Plan access is mapped per projection. | Evidence profile: json_contract_shape; `rg` checks free, basic, premium and projection matrix wording. |
| AC3 | Client projection coverage is explicit. | Evidence profile: json_contract_shape; `rg` checks the three B2C projection IDs. |
| AC4 | Internal projections are denied to B2C. | Evidence profile: external_usage_blocker; `rg` checks expert, admin, debug, raw runtime and prompt denial wording. |
| AC5 | Plan-insufficient errors are controlled. | Evidence profile: api_error_shape_contract; `rg` checks `plan_insufficient` and required error fields. |
| AC6 | AI audit triggers are defined. | Evidence profile: json_contract_shape; `rg` checks `narrative_answer_audit_v1`, basic, premium, long and sensitive. |
| AC7 | Quota linkage follows existing decisions. | Evidence profile: external_usage_blocker; `rg` checks quota decision and separate product decision wording. |
| AC8 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC9 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-283 evidence paths. |

## Implementation Tasks

- [x] Task 1: Inspect existing projection, audit and entitlement owners before writing the policy. (AC: AC1, AC2, AC3, AC6)
- [x] Task 2: Create `docs/architecture/b2c-projection-entitlement-policy.md` with a French global file comment. (AC: AC1)
- [x] Task 3: Define the B2C role of the policy for free, basic and premium access. (AC: AC1, AC2)
- [x] Task 4: Document the projection-by-plan matrix for `structured_facts_v1`, `beginner_summary_v1` and client interpretation. (AC: AC2, AC3)
- [x] Task 5: Document denied internal projections and forbidden technical surfaces for B2C clients. (AC: AC4)
- [x] Task 6: Document the controlled `plan_insufficient` error shape for future authorization tests. (AC: AC5)
- [x] Task 7: Document AI audit triggers for basic, premium, long and sensitive narrative outputs. (AC: AC6)
- [x] Task 8: Document quota linkage only from existing product decisions and defer new quota creation. (AC: AC7)
- [x] Task 9: Align `docs/architecture/official-product-primitives-public-projections.md` to reference CS-283 policy ownership. (AC: AC1, AC2)
- [x] Task 10: Persist validation, scoped status and source checklist evidence under the CS-283 evidence folder. (AC: AC8, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-283-define-b2c-projection-entitlement-policy.md` - source contract.
- `docs/architecture/official-product-primitives-public-projections.md` - existing public projection governance owner.
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - upstream factual projection dependency.
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md` - beginner B2C projection dependency.
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md` - plan-depth projection dependency.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - audit trigger dependency.
- `backend/app/services/entitlement/**` - existing entitlement service ownership.
- `backend/app/services/billing/**` - existing free/basic/premium billing plan vocabulary.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `docs/architecture/official-product-primitives-public-projections.md` for public projection governance.
  - CS-256, CS-257, CS-258 and CS-259 stories for projection and audit contract boundaries.
  - `backend/app/services/entitlement/**` and `backend/app/services/billing/**` for existing plan and entitlement vocabulary.
  - `app.routes`, `app.openapi()`, scoped `git status`, `pytest` and targeted `rg` scans for no public API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/b2c-projection-entitlement-policy.md`.
- Static scans alone are not sufficient because:
  - public API neutrality and application-source non-change must be proven from the loaded app and scoped status.

## Contract Shape

- Contract type:
  - Markdown backend-domain policy for B2C projection entitlements.
- Fields:
  - `policy_id`: exact value `b2c_projection_entitlement_policy`.
  - `plans`: exact values `free`, `basic` and `premium`.
  - `projection_matrix`: mapping of projection ID to minimum plan and allowed content depth.
  - `authorized_projections`: `structured_facts_v1`, `beginner_summary_v1` and `client_interpretation_projection_v1`.
  - `denied_internal_projections`: expert, admin, debug, raw runtime, prompt, provider and audit payload surfaces.
  - `plan_insufficient_error`: code, message, current_plan, required_plan, projection_id and upgrade_hint policy.
  - `audit_trigger_policy`: `narrative_answer_audit_v1` trigger rules for basic, premium, long and sensitive narrative answers.
  - `quota_policy`: existing quota references or explicit separate product decision requirement.
- Required fields:
  - `policy_id`
  - `plans`
  - `projection_matrix`
  - `authorized_projections`
  - `denied_internal_projections`
  - `plan_insufficient_error`
  - `audit_trigger_policy`
  - `quota_policy`
- Optional fields:
  - `upgrade_hint` only when the message remains client-readable and non-technical.
- Status codes:
  - Documentation only; future API stories must map `plan_insufficient` to a controlled HTTP response.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose a new B2C entitlement policy route from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-283-define-b2c-projection-entitlement-policy.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
  - `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md`
  - `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md`
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- Comparison after implementation:
  - `docs/architecture/b2c-projection-entitlement-policy.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/validation.txt`
  - `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one policy document, one registry alignment and CONDAMAD story/evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| B2C entitlement policy | `docs/architecture/b2c-projection-entitlement-policy.md` | API routers, frontend, DB models |
| Public projection registry | `docs/architecture/official-product-primitives-public-projections.md` | duplicated projection registry |
| Projection contracts | CS-256, CS-257 and CS-258 story contracts | entitlement policy as payload owner |
| Narrative audit trigger | `docs/architecture/narrative-answer-audit-v1-contract.md` | client projection payloads |
| Future authorization tests | `backend/tests/authorization/` | route-local ad hoc checks |
| Evidence artifacts | `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the existing public projection governance document instead of creating a parallel projection registry.
- Reuse CS-256 `structured_facts_v1`, CS-257 `beginner_summary_v1` and CS-258 `client_interpretation_projection_v1` identifiers.
- Reuse CS-259 `narrative_answer_audit_v1` for audit trigger wording instead of creating a second audit contract.
- Reuse existing free, basic and premium plan vocabulary from entitlement and billing services.
- Keep one canonical `b2c_projection_entitlement_policy` document and one plan matrix.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts, migrations or generated clients.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for this entitlement policy.
- No compatibility projection path may bypass the B2C projection entitlement matrix.
- No fallback branch may expose internal projections to B2C clients.
- Do not create aliases, shims, wrappers or parallel documents for the same policy contract.
- Do not place expert, admin, debug, raw runtime, prompt, provider or audit payload fields inside B2C projections.
- Do not implement plan checks directly inside route handlers as the only product source of truth.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as entitlement policy owners

## Reintroduction Guard

- Guard target:
  - B2C clients cannot access denied internal projections;
  - plan access cannot be redefined inside routes without the canonical policy matrix;
  - `plan_insufficient` cannot expose technical payloads or raw runtime details;
  - basic, premium, long and sensitive narrative outputs cannot bypass `narrative_answer_audit_v1`;
  - public API routes, database migrations and frontend files cannot be introduced by this story.
- Guard mechanism:
  - targeted `rg` checks for required matrix, denial, error and audit terms;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-283 evidence folder.
- Guard owner:
  - `docs/architecture/b2c-projection-entitlement-policy.md`;
  - `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/validation.txt`;
  - `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/app-surface-status.txt`.
- Guard evidence:
  - `rg -n "b2c_projection_entitlement_policy|free|basic|premium|plan_insufficient" docs _story_briefs`;
  - `python -c "from app.main import app; assert 'b2c_projection_entitlement_policy' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('b2c-projection-entitlement' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src backend/tests backend/migrations`.

## Regression Guardrails

Scope vector:

- backend-domain policy documentation: yes;
- docs architecture contract: yes;
- entitlement and billing source reference: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths are referenced only as source owners, not modified. | `git status`; `python` loaded app checks. |
| RG-003 | Route architecture stays unchanged because this policy adds no route. | `app.routes`; `app.openapi()`. |
| RG-022 | Validation paths must point to collected pytest targets. | `pytest -q`; targeted evidence paths. |
| RG-041 | Entitlement documentation must stay aligned with runtime and API evidence. | targeted `rg`; loaded app checks. |
| Registry gap | No exact `b2c_projection_entitlement_policy` guardrail exists in resolver output. | Story-local scans and loaded app checks. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-007 admin LLM observability is not a changed route owner; only audit trigger wording is referenced.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Policy document | `docs/architecture/b2c-projection-entitlement-policy.md` | Keep the canonical B2C projection entitlement policy. |
| Validation output | `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/validation.txt` | Keep content scans and validation. |
| Application surface status | `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-283-b2c-projection-entitlement-policy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this policy documentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/b2c-projection-entitlement-policy.md` - new canonical policy document.
- `docs/architecture/official-product-primitives-public-projections.md` - align the public projection registry with CS-283.
- `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/b2c-projection-entitlement-policy.md` - checked by `rg` and `python` validation commands.
- `backend/tests/architecture/test_api_contract_neutrality.py` - targeted architecture regression check for no public route drift.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/tests/**` - out of scope except existing architecture tests executed as evidence.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/b2c-projection-entitlement-policy.md').exists()"`
- VC3: `rg -n "b2c_projection_entitlement_policy|free|basic|premium" docs/architecture/b2c-projection-entitlement-policy.md`
- VC4: `rg -n "structured_facts_v1|beginner_summary_v1|client_interpretation_projection_v1" docs/architecture/b2c-projection-entitlement-policy.md`
- VC5: `rg -n "expert|admin|debug|raw runtime|prompt|denied_internal_projections" docs/architecture/b2c-projection-entitlement-policy.md`
- VC6: `rg -n "plan_insufficient|current_plan|required_plan|projection_id|upgrade_hint" docs/architecture/b2c-projection-entitlement-policy.md`
- VC7: `rg -n "narrative_answer_audit_v1|basic|premium|long|sensitive" docs/architecture/b2c-projection-entitlement-policy.md`
- VC8: `rg -n "quota|limit|separate product decision" docs/architecture/b2c-projection-entitlement-policy.md`
- VC9: `python -c "from app.main import app; assert 'b2c_projection_entitlement_policy' not in str(app.openapi())"`
- VC10: `python -c "from app.main import app; assert all('b2c-projection-entitlement' not in getattr(r, 'path', '') for r in app.routes)"`
- VC11: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC12: `git status --short -- backend/app frontend/src backend/tests backend/migrations`
- VC13: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-283-b2c-projection-entitlement-policy/evidence/validation.txt').exists()"`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `pytest -q`
- VC17: `rg -n "entitlement|free|basic|premium|plan insuffisant|projection interne" .\docs .\_story_briefs`
- VC18: `git status --short -- backend/app frontend/src`

Before VC2, VC9, VC10 and VC13, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Plan differentiation could be implemented inside routes without a readable product matrix.
- Premium access could drift into expert or admin projection exposure instead of B2C narrative depth.
- `plan_insufficient` could leak technical payloads, raw runtime fields or audit internals.
- Basic, premium, long or sensitive narrative outputs could bypass required audit linkage.
- A documentation story could drift into payment, API, frontend, DB, prompt, provider or migration implementation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep the implementation documentation-only unless a separate user decision authorizes code, DB, route, prompt or frontend work.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-283-define-b2c-projection-entitlement-policy.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md`
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md`
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- `backend/app/services/entitlement/**`
- `backend/app/services/billing/**`
- `_condamad/stories/regression-guardrails.md`
