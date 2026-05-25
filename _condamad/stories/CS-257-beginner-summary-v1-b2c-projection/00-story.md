# Story CS-257 beginner-summary-v1-b2c-projection: Define beginner_summary_v1 Deterministic B2C Projection
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-257-define-beginner-summary-v1-deterministic-b2c-projection.md`.
- Related dependency: CS-255 documents public product primitives and separates raw runtime from public projections.
- Related dependency: CS-256 defines `structured_facts_v1` as the stable factual base for downstream projections.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` already lists `beginner_summary`.
- Existing runtime reference found: `backend/app/services/llm_generation/shared/natal_context.py` owns degraded natal context terms.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `beginner_summary_v1` lacks one deterministic B2C projection contract for free/basic client use.
- Source-alignment evidence: PASS; ACs preserve allowed fields, states, missing birth time behavior, source link and raw-surface exclusions.

## Objective

Define one canonical backend-domain contract document for `beginner_summary_v1` as a simple deterministic B2C projection for free/basic plans.

The implementation must formalize allowed client fields, user-facing states, no-time degraded behavior, `structured_facts_v1` linkage and controlled
error messages without implementing a route, frontend screen, LLM narration, database object or premium projection.

## Target State

- `beginner_summary_v1` is documented as the basic client projection for public-user, beginner, free and basic contexts.
- The projection exposes only signs principaux, ascendant when available, dominant house, dominant themes and controlled status/message fields.
- The projection defines the states `loading`, `empty`, `degraded` and `unavailable` with deterministic trigger rules.
- Missing birth time produces a documented degraded mode that withholds ascendant and house-dependent claims.
- `structured_facts_v1` is named as the upstream factual source, not as a direct public payload dump.
- Controlled error messages are documented with stable codes and no raw traceback, debug payload, audit detail or runtime trace.
- Differences from `structured_facts_v1` are explicit: limited readability projection, not full facts, not hash/audit projection, not expert technical data.
- No frontend implementation, API route, OpenAPI schema, runtime builder, service, model, DB table, migration or premium projection is created by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-257-define-beginner-summary-v1-deterministic-b2c-projection.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-257`.
- Evidence 3: `docs/architecture/official-product-primitives-public-projections.md` - existing `beginner_summary` primitive owner found.
- Evidence 4: `_condamad/stories/CS-255-product-architecture-current-state/00-story.md` - product architecture dependency read.
- Evidence 5: `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - `structured_facts_v1` dependency read.
- Evidence 6: `backend/app/services/llm_generation/shared/natal_context.py` - degraded natal context terminology found by targeted search.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Source-alignment evidence: PASS; the story answers every brief stake without turning the beginner projection into expert, frontend or API work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical contract documentation for `beginner_summary_v1`.
  - Allowed B2C fields, deterministic state rules, degraded no-time behavior and controlled error messages.
  - Relationship to `structured_facts_v1` as upstream factual source.
  - Negative checks for full technical data, raw runtime, audit details, API route and frontend drift.
  - Persistent evidence artifacts for contract validation scans.
- Out of scope:
  - Frontend UI, public API exposure, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Runtime projection builder, service orchestration, serializer, persistence, premium projection and long LLM narration.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or API contract for `beginner_summary_v1`.
  - No runtime projection builder, service orchestration, database table or migration.
  - No premium projection, expert technical projection, prompt template, final prose or LLM provider integration.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain projection contract documentation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `beginner_summary_v1` contract documentation, product registry alignment and story evidence artifacts.
  - Reuse existing `beginner_summary`, `structured_facts_v1`, B2C, free/basic and degraded natal context terminology.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep full technical data, raw runtime payloads, audit details and debug payloads outside the B2C projection.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose expert or premium technical fields inside `beginner_summary_v1`.
- Additional validation rules:
  - The contract must name `beginner_summary_v1` exactly.
  - The contract must list signs principaux, ascendant, maison dominante and thèmes dominants as allowed client fields.
  - The contract must define `loading`, `empty`, `degraded` and `unavailable` with deterministic trigger rules.
  - The contract must describe missing birth time behavior and the ascendant or house-dependent fields withheld in degraded mode.
  - The contract must state that `structured_facts_v1` is the upstream factual source and not the direct public payload.
  - The contract must define controlled error codes/messages with no raw runtime, debug or audit payload exposure.
  - The contract must state free/basic compatibility and exclude premium projection requirements.
  - `app.routes`, `app.openapi()`, `pytest` and scoped `git status` prove no public API or application surface drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing degraded context and loaded app checks prove the boundary before contract claims it. |
| Baseline Snapshot | yes | Before and after evidence must prove one contract document, registry alignment and no app-surface drift. |
| Ownership Routing | yes | Product primitive docs, projection contract, source facts and future runtime builder need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this single projection contract story. |
| Contract Shape | yes | `beginner_summary_v1` has exact fields, states, no-time behavior, source link and error shape. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Full facts, raw runtime, audit details, premium fields and long LLM narration must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `beginner_summary_v1` is documented. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Authorized client fields are explicit. | Evidence profile: json_contract_shape; `rg` checks signs principaux, ascendant, maison dominante and thèmes dominants. |
| AC3 | Client states are deterministic. | Evidence profile: json_contract_shape; `rg` checks loading, empty, degraded and unavailable trigger rules. |
| AC4 | Missing birth time behavior is explicit. | Evidence profile: json_contract_shape; `rg` checks heure de naissance, ascendant and house-dependent withholding. |
| AC5 | `structured_facts_v1` source linkage is explicit. | Evidence profile: json_contract_shape; `rg` checks upstream factual source and direct payload wording. |
| AC6 | Technical payload exposure is forbidden. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks raw runtime, debug, audit and full facts exclusions. |
| AC7 | Free/basic compatibility is explicit. | Evidence profile: external_usage_blocker; `rg` checks B2C, free, basic and premium exclusion wording. |
| AC8 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC9 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output for app roots. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-257 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing `beginner_summary`, `structured_facts_v1` and degraded natal context owners before writing the contract. (AC: AC1, AC4, AC5)
- [ ] Task 2: Create `docs/architecture/beginner-summary-v1-contract.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define the B2C free/basic role of `beginner_summary_v1`. (AC: AC1, AC7)
- [ ] Task 4: Document authorized fields for signs principaux, ascendant, maison dominante and thèmes dominants. (AC: AC2)
- [ ] Task 5: Document `loading`, `empty`, `degraded` and `unavailable` as deterministic states. (AC: AC3)
- [ ] Task 6: Document missing birth time behavior and withheld ascendant or house-dependent fields. (AC: AC4)
- [ ] Task 7: Link `beginner_summary_v1` to `structured_facts_v1` as upstream source without direct public dump semantics. (AC: AC5)
- [ ] Task 8: Document controlled error codes/messages and excluded technical payloads. (AC: AC6)
- [ ] Task 9: Align `docs/architecture/official-product-primitives-public-projections.md` to name CS-257 and `beginner_summary_v1`. (AC: AC1, AC7)
- [ ] Task 10: Persist validation, scoped status and source checklist evidence under the CS-257 evidence folder. (AC: AC8, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-257-define-beginner-summary-v1-deterministic-b2c-projection.md` - source contract.
- `docs/architecture/official-product-primitives-public-projections.md` - existing `beginner_summary` product primitive owner.
- `_condamad/stories/CS-255-product-architecture-current-state/00-story.md` - product architecture dependency.
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - upstream factual projection dependency.
- `docs/architecture/structured-facts-v1-contract.md` - expected upstream contract after CS-256 implementation.
- `backend/app/services/llm_generation/shared/natal_context.py` - existing degraded natal context terminology.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - existing free short and degraded mode reference surface.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `docs/architecture/official-product-primitives-public-projections.md` for product primitive ownership.
  - `docs/architecture/structured-facts-v1-contract.md` for upstream factual projection after CS-256.
  - `backend/app/services/llm_generation/shared/natal_context.py` for current degraded natal context terminology.
  - `app.routes`, `app.openapi()`, scoped `git status`, and targeted `rg` scans for no public API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/beginner-summary-v1-contract.md`.
- Static scans alone are not sufficient because:
  - public API neutrality and application-source non-change must be proven from the loaded app and scoped status.

## Contract Shape

- Contract type:
  - Markdown backend-domain contract for a future controlled B2C projection.
- Fields:
  - `projection_id`: exact value `beginner_summary_v1`.
  - `audience`: public-user, beginner, free and basic.
  - `source_projection`: exact value `structured_facts_v1`.
  - `allowed_fields`: signs principaux, ascendant when available, maison dominante and thèmes dominants.
  - `state`: one of `loading`, `empty`, `degraded` or `unavailable`.
  - `degraded_reason`: controlled reason such as missing birth time.
  - `display_messages`: stable user-facing messages with controlled codes.
  - `excluded_surfaces`: full technical data, raw runtime payloads, debug details, audit details and premium projection fields.
- Required fields:
  - `projection_id`
  - `audience`
  - `source_projection`
  - `allowed_fields`
  - `state`
  - `display_messages`
  - `excluded_surfaces`
- Optional fields:
  - `ascendant` only when birth time supports it.
  - `maison_dominante` only when birth time supports house-dependent calculation.
  - `degraded_reason` only when `state` is `degraded`.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `beginner_summary_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-257-define-beginner-summary-v1-deterministic-b2c-projection.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-255-product-architecture-current-state/00-story.md`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- Comparison after implementation:
  - `docs/architecture/beginner-summary-v1-contract.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/validation.txt`
  - `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document, one registry alignment and CONDAMAD story/evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `beginner_summary_v1` contract | `docs/architecture/beginner-summary-v1-contract.md` | API routers, frontend, DB models |
| Product primitive registry | `docs/architecture/official-product-primitives-public-projections.md` | duplicated projection registry |
| Upstream factual source | `docs/architecture/structured-facts-v1-contract.md` | B2C contract as full facts owner |
| Degraded natal terminology | `backend/app/services/llm_generation/shared/natal_context.py` | new duplicate state vocabulary |
| Evidence artifacts | `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the existing `beginner_summary` product primitive wording instead of creating a parallel primitive name.
- Reuse CS-256 `structured_facts_v1` terminology for the upstream factual source.
- Reuse existing degraded natal context terms for missing birth time behavior.
- Keep one canonical `beginner_summary_v1` document and one projection identifier.
- Keep state names stable: `loading`, `empty`, `degraded` and `unavailable`.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services or generated clients.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for this projection.
- No compatibility projection path may bypass `beginner_summary_v1`.
- No fallback branch may expose raw runtime objects as the B2C projection.
- Do not create aliases, shims, wrappers or parallel documents for the same projection contract.
- Do not place full technical data, long LLM narration, prompt text, raw debug traces, audit details or premium fields inside the projection.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as projection contract owners

## Reintroduction Guard

- Guard target:
  - full technical data cannot enter `beginner_summary_v1`;
  - raw runtime payloads cannot become B2C projection payloads;
  - audit and debug details cannot be exposed to free/basic users;
  - premium projection fields cannot be required by this beginner contract;
  - public API routes and OpenAPI schemas cannot be introduced by this story.
- Guard mechanism:
  - targeted `rg` checks for required contract terms and forbidden raw-surface terms;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-257 evidence folder.
- Guard owner:
  - `docs/architecture/beginner-summary-v1-contract.md`;
  - `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/validation.txt`;
  - `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/app-surface-status.txt`.
- Guard evidence:
  - `rg -n "beginner_summary_v1|structured_facts_v1|free|basic|degraded" docs/architecture`;
  - `python -c "from app.main import app; assert 'beginner_summary_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('beginner_summary' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src backend/tests backend/migrations`.

## Regression Guardrails

Scope vector:

- backend-domain contract documentation: yes;
- docs architecture contract: yes;
- backend runtime source reference: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths are referenced only as source owners, not modified. | `git status`; `python` loaded app checks. |
| RG-022 | Backend validation paths must point to collected pytest targets. | `pytest -q`; targeted evidence paths. |
| Registry gap | No exact `beginner_summary_v1` guardrail exists in scoped resolver output. | Story-local `rg`, `app.routes` and `app.openapi()` guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this contract concerns astrology B2C projections.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/beginner-summary-v1-contract.md` | Keep the canonical `beginner_summary_v1` contract. |
| Validation output | `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/validation.txt` | Keep content scans and validation output. |
| Application surface status | `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this contract documentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/beginner-summary-v1-contract.md` - new canonical contract document.
- `docs/architecture/official-product-primitives-public-projections.md` - align the existing primitive row and roadmap story number.
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/beginner-summary-v1-contract.md` - checked by `rg` and `python` validation commands; no test file is expected to change.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/tests/**` - out of scope; no backend test is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/beginner-summary-v1-contract.md').exists()"`
- VC3: `rg -n "beginner_summary_v1|B2C|free|basic" docs/architecture/beginner-summary-v1-contract.md`
- VC4: `rg -n "signes principaux|ascendant|maison dominante|thèmes dominants" docs/architecture/beginner-summary-v1-contract.md`
- VC5: `rg -n "loading|empty|degraded|unavailable|trigger" docs/architecture/beginner-summary-v1-contract.md`
- VC6: `rg -n "heure de naissance|ascendant|house-dependent|degraded_reason" docs/architecture/beginner-summary-v1-contract.md`
- VC7: `rg -n "structured_facts_v1|upstream factual source|direct public payload" docs/architecture/beginner-summary-v1-contract.md`
- VC8: `rg -n "controlled error|raw runtime|debug|audit|premium" docs/architecture/beginner-summary-v1-contract.md`
- VC9: `python -c "from app.main import app; assert 'beginner_summary_v1' not in str(app.openapi())"`
- VC10: `python -c "from app.main import app; assert all('beginner_summary' not in getattr(r, 'path', '') for r in app.routes)"`
- VC11: `git status --short -- backend/app frontend/src backend/tests backend/migrations`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/evidence/validation.txt').exists()"`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q`

Before VC2, VC9, VC10 and VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The contract may drift into a mini expert projection instead of a beginner B2C summary.
- The projection may expose full technical facts instead of a limited client-readable subset.
- Missing birth time may produce unsupported ascendant or house-dependent claims.
- `structured_facts_v1` may be reframed as a direct public payload instead of an upstream source.
- A documentation story may drift into API, frontend, builder, service or migration implementation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep the implementation documentation-only unless a separate user decision authorizes code or API work.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-257-define-beginner-summary-v1-deterministic-b2c-projection.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-255-product-architecture-current-state/00-story.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `docs/architecture/structured-facts-v1-contract.md`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `_condamad/stories/regression-guardrails.md`
