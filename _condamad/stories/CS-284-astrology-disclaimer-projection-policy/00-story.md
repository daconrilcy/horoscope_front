# Story CS-284 astrology-disclaimer-projection-policy: Define Astrology Disclaimer Projection Policy
Status: ready-to-dev

## Trigger / Source

- Source type: audit-to-story with repository-informed boundary.
- Source reference: `_story_briefs/cs-284-audit-existing-astrology-disclaimers-and-projection-disclaimer-policy.md`.
- Related dependency: CS-257 defines `beginner_summary_v1` as the beginner B2C projection.
- Related dependency: CS-258 defines `client_interpretation_projection_v1` by free, basic and premium plan depth.
- Related dependency: CS-283 defines B2C projection entitlement policy for free, basic and premium plans.
- Existing owner found: `backend/app/services/resources/templates/disclaimer_registry.py` owns static natal disclaimers.
- Existing owner found: `backend/app/services/llm_generation/natal/interpretation_service.py` injects static disclaimers for natal output.
- Existing owner found: `backend/app/services/llm_generation/guidance/guidance_service.py` has guidance disclaimer behavior.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: B2C projection disclaimers lack one audited policy that maps existing texts to projection plans and removes LLM authorship.
- Source-alignment evidence: PASS; ACs preserve inventory, plan mapping, degraded/no-time coverage, LLM boundary and justified text delta.

## Objective

Define one canonical backend-domain audit and policy document for astrology disclaimers attached to B2C projections.

The implementation must inventory existing disclaimers, classify usage, decide which texts are application-injected, map them to free, basic and premium
projection plans, and forbid LLM-authored disclaimer variation without creating a new legal policy, UI, route, prompt rewrite or admin-only exposure.

## Target State

- One policy document records the existing disclaimer inventory across backend, frontend and documentation.
- Existing disclaimer usage is classified as natal, prediction, AI, degraded mode and missing birth time.
- Each B2C projection plan states which static application-controlled disclaimers apply.
- The LLM is documented as never owning, inventing or modifying disclaimer text.
- Degraded mode and missing birth time have explicit disclaimer coverage or a documented product gap.
- Any created or changed disclaimer text is justified by an identified inventory gap.
- Technical admin disclaimers and internal debug warnings are not exposed to B2C clients by this policy.
- No API route, frontend screen, DB migration, prompt rewrite, provider change or admin surface is created by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-284-audit-existing-astrology-disclaimers-and-projection-disclaimer-policy.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-284`.
- Evidence 3: `backend/app/services/resources/templates/disclaimer_registry.py` - static application disclaimer registry found.
- Evidence 4: `backend/app/services/llm_generation/natal/interpretation_service.py` - natal service injects registry disclaimers.
- Evidence 5: `backend/app/services/llm_generation/guidance/guidance_service.py` - guidance output includes disclaimer behavior.
- Evidence 6: `docs/architecture/official-product-primitives-public-projections.md` - public projection governance owner found.
- Evidence 7: CS-257, CS-258 and CS-283 stories read as B2C projection and entitlement dependencies.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 9: `resolve_guardrails.py` - scoped resolver run for backend-domain disclaimer policy and B2C projection scope.
- Source-alignment evidence: PASS; the story answers every brief stake without turning audit policy into implementation or legal drafting.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit and canonical policy documentation for astrology disclaimers.
  - Inventory across backend, frontend and docs using targeted scans.
  - Usage classification for natal, prediction, AI, degraded mode and missing birth time.
  - Static application injection policy for B2C projections by free, basic and premium plan.
  - LLM boundary forbidding disclaimer invention or text mutation.
  - Justification rule for any created or changed disclaimer text.
  - Persistent evidence artifacts for inventory, policy validation and app-surface status.
- Out of scope:
  - New complete legal policy, frontend UI, public route, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Prompt rewrite, provider integration, admin-only disclaimer exposure, payment behavior and runtime projection builder implementation.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or API contract for disclaimer delivery.
  - No database table, migration, prompt rewrite, provider change or admin technical disclaimer exposure.
  - No new legal doctrine beyond documented gaps and application-controlled product policy.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain disclaimer audit and policy contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only disclaimer audit/policy documentation, product projection registry alignment and story evidence artifacts.
  - Reuse existing static disclaimer registry, natal disclaimer injection and B2C projection terminology.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep LLM output, prompt text and provider responses outside disclaimer authorship.
  - Keep technical admin disclaimers and debug warnings outside B2C client projection payloads.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to create new legal wording beyond a documented inventory gap.
- Additional validation rules:
  - The policy must name `astrology_disclaimer_projection_policy` exactly.
  - The policy must inventory existing disclaimers from backend, frontend and docs.
  - The policy must classify usages as natal, prediction, AI, degraded mode and missing birth time.
  - The policy must map disclaimer applicability to free, basic and premium B2C projection plans.
  - The policy must state that disclaimers are injected by application code, not authored by the LLM.
  - The policy must cover degraded mode and missing birth time, or record a product gap with owner and next action.
  - The policy must justify each created or changed disclaimer text by an identified gap.
  - `app.routes`, `app.openapi()`, `pytest` and scoped `git status` prove no public API or application surface drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing registry, service injection points, `app.routes`, `app.openapi()` and `pytest` prove the boundary. |
| Baseline Snapshot | yes | Before and after evidence must prove inventory, policy document, registry alignment and no app-surface drift. |
| Ownership Routing | yes | Disclaimer registry, policy document, projection registry and future runtime injection need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this disclaimer policy story. |
| Contract Shape | yes | The policy has exact inventory, usage classes, plan mapping, LLM boundary and gap justification fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | LLM-authored disclaimers and undocumented plan attachment must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Existing disclaimers are inventoried. | Evidence profile: baseline_before_after_diff; `rg` scans backend, frontend, docs and briefs. |
| AC2 | Usage classes are explicit. | Evidence profile: json_contract_shape; `rg` checks natal, prediction, AI, degraded mode and missing birth time. |
| AC3 | B2C plan attachment is explicit. | Evidence profile: json_contract_shape; `rg` checks free, basic, premium and projection mapping. |
| AC4 | LLM disclaimer authorship is forbidden. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks LLM boundary and application injection wording. |
| AC5 | Degraded states are covered. | Evidence profile: json_contract_shape; `rg` checks degraded mode and missing birth time policy rows. |
| AC6 | Text deltas are justified. | Evidence profile: external_usage_blocker; `rg` checks identified gap, owner and next action wording. |
| AC7 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC8 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |
| AC9 | Regression tests stay green. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-284 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing disclaimer registry, natal injection and guidance disclaimer behavior before writing the policy. (AC: AC1, AC4)
- [ ] Task 2: Create `docs/architecture/astrology-disclaimer-projection-policy.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Persist a bounded inventory of backend, frontend, docs and brief disclaimer references. (AC: AC1, AC10)
- [ ] Task 4: Classify each disclaimer usage as natal, prediction, AI, degraded mode or missing birth time. (AC: AC2, AC5)
- [ ] Task 5: Map static disclaimer applicability to free, basic and premium B2C projections. (AC: AC3)
- [ ] Task 6: Document that application code injects disclaimers and the LLM never authors or mutates them. (AC: AC4)
- [ ] Task 7: Document gap handling for degraded mode and missing birth time coverage. (AC: AC5, AC6)
- [ ] Task 8: Justify each created or changed disclaimer text from an inventory gap. (AC: AC6)
- [ ] Task 9: Align `docs/architecture/official-product-primitives-public-projections.md` to reference CS-284 disclaimer ownership. (AC: AC3)
- [ ] Task 10: Persist validation, scoped status and source checklist evidence under the CS-284 evidence folder. (AC: AC7, AC8, AC10)

## Files to Inspect First

- `_story_briefs/cs-284-audit-existing-astrology-disclaimers-and-projection-disclaimer-policy.md` - source brief.
- `backend/app/services/resources/templates/disclaimer_registry.py` - existing static disclaimer registry.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - existing natal disclaimer injection.
- `backend/app/services/llm_generation/guidance/guidance_service.py` - existing guidance disclaimer behavior.
- `backend/app/services/llm_generation/shared/natal_context.py` - existing degraded natal context terminology.
- `docs/architecture/official-product-primitives-public-projections.md` - public projection governance owner.
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md` - beginner projection dependency.
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md` - plan projection dependency.
- `_condamad/stories/CS-283-b2c-projection-entitlement-policy/00-story.md` - entitlement policy dependency.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/services/resources/templates/disclaimer_registry.py` for existing static disclaimer texts.
  - `backend/app/services/llm_generation/natal/interpretation_service.py` for existing natal disclaimer injection.
  - `backend/app/services/llm_generation/guidance/guidance_service.py` for existing guidance disclaimer behavior.
  - `docs/architecture/official-product-primitives-public-projections.md` for B2C projection governance.
  - CS-257, CS-258 and CS-283 stories for B2C projection and entitlement boundaries.
  - `app.routes`, `app.openapi()`, scoped `git status`, `pytest` and targeted `rg` scans for no API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/astrology-disclaimer-projection-policy.md`.
- Static scans alone are not sufficient because:
  - public API neutrality and application-source non-change must be proven from the loaded app and scoped status.

## Contract Shape

- Contract type:
  - Markdown backend-domain audit and policy for B2C astrology disclaimer attachment.
- Fields:
  - `policy_id`: exact value `astrology_disclaimer_projection_policy`.
  - `inventory_scope`: backend, frontend, docs and story briefs searched for existing disclaimer references.
  - `usage_class`: one of natal, prediction, AI, degraded mode or missing birth time.
  - `source_owner`: canonical file, service or document owning the existing disclaimer behavior.
  - `injection_owner`: application component responsible for attaching the disclaimer.
  - `projection_plan`: one of free, basic or premium.
  - `applicability`: projection IDs or plan contexts that receive the disclaimer.
  - `llm_boundary`: the LLM does not author, invent, rewrite or mutate disclaimer text.
  - `gap_status`: covered, product gap or text delta justified by identified gap.
  - `admin_exposure_policy`: technical admin-only warnings stay outside B2C client payloads.
- Required fields:
  - `policy_id`
  - `inventory_scope`
  - `usage_class`
  - `source_owner`
  - `injection_owner`
  - `projection_plan`
  - `applicability`
  - `llm_boundary`
  - `gap_status`
  - `admin_exposure_policy`
- Optional fields:
  - `next_action` only for a product gap.
  - `text_delta_justification` only for created or changed disclaimer text.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose a new disclaimer endpoint from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-284-audit-existing-astrology-disclaimers-and-projection-disclaimer-policy.md`
  - `backend/app/services/resources/templates/disclaimer_registry.py`
  - `backend/app/services/llm_generation/natal/interpretation_service.py`
  - `backend/app/services/llm_generation/guidance/guidance_service.py`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - CS-257, CS-258 and CS-283 story contracts.
- Comparison after implementation:
  - `docs/architecture/astrology-disclaimer-projection-policy.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md`
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt`
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one policy document, one projection registry alignment and CONDAMAD story/evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Static disclaimer registry | `backend/app/services/resources/templates/disclaimer_registry.py` | prompt templates or provider output |
| Disclaimer projection policy | `docs/architecture/astrology-disclaimer-projection-policy.md` | API routers, frontend, DB models |
| Public projection registry | `docs/architecture/official-product-primitives-public-projections.md` | duplicated projection registry |
| Degraded natal terminology | `backend/app/services/llm_generation/shared/natal_context.py` | new duplicate state vocabulary |
| Future runtime injection tests | `backend/tests/services/llm_generation/` | route-local ad hoc checks |
| Evidence artifacts | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse `backend/app/services/resources/templates/disclaimer_registry.py` as the existing static disclaimer owner.
- Reuse existing natal and guidance disclaimer behavior instead of creating parallel disclaimer text sources.
- Reuse CS-257, CS-258 and CS-283 free, basic and premium B2C projection terminology.
- Reuse existing degraded natal context terminology for missing birth time coverage.
- Keep one canonical `astrology_disclaimer_projection_policy` document and one inventory evidence artifact.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts, migrations or generated clients.

## No Legacy / Forbidden Paths

- No legacy disclaimer source may bypass the static registry or the policy document.
- No compatibility disclaimer path may allow LLM-authored legal or product wording.
- No fallback branch may expose unclassified technical admin warnings to B2C clients.
- Do not create aliases, shims, wrappers or parallel documents for the same disclaimer policy.
- Do not place disclaimer ownership in prompt templates, provider responses, frontend-only copy or route handlers.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as disclaimer owners

## Reintroduction Guard

- Guard target:
  - LLM output cannot become the source of disclaimer text;
  - disclaimer attachment cannot be undocumented per B2C projection plan;
  - degraded mode and missing birth time cannot lose client-visible coverage;
  - technical admin warnings cannot become B2C disclaimer payloads;
  - public API routes, database migrations and frontend files cannot be introduced by this story.
- Guard mechanism:
  - targeted `rg` checks for required inventory, usage classes, plan mapping, LLM boundary and gap justification;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-284 evidence folder.
- Guard owner:
  - `docs/architecture/astrology-disclaimer-projection-policy.md`;
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md`;
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt`.
- Guard evidence:
  - `rg -n "astrology_disclaimer_projection_policy|free|basic|premium|LLM" docs/architecture`;
  - `python -c "from app.main import app; assert 'astrology_disclaimer_projection_policy' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('disclaimer-policy' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src backend/tests backend/migrations`.

## Regression Guardrails

Scope vector:

- backend-domain policy documentation: yes;
- docs architecture contract: yes;
- disclaimer registry source reference: yes;
- LLM generation source reference: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths are referenced as source owners, not modified. | `git status`; `python` loaded app checks. |
| Registry gap | No exact disclaimer-projection guardrail exists in resolver output. | Story-local scans and loaded app checks. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story references plan mapping, not access rights.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Policy document | `docs/architecture/astrology-disclaimer-projection-policy.md` | Keep the canonical disclaimer projection policy. |
| Disclaimer inventory | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md` | Keep the bounded audit inventory. |
| Validation output | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt` | Keep content scans and validation output. |
| Application surface status | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/source-checklist.md` | Record source coverage. |
| Review output | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this disclaimer policy story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/astrology-disclaimer-projection-policy.md` - new canonical audit and policy document.
- `docs/architecture/official-product-primitives-public-projections.md` - align public projection registry with CS-284 disclaimer ownership.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md` - bounded inventory artifact.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/astrology-disclaimer-projection-policy.md` - checked by `rg` and `python` validation commands.
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
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/astrology-disclaimer-projection-policy.md').exists()"`
- VC3: `rg -n "disclaimer|avertissement|IA|prediction|heure de naissance|mode degrade" .\backend .\frontend .\docs .\_story_briefs`
- VC4: `rg -n "astrology_disclaimer_projection_policy|disclaimer_registry|get_disclaimers" docs/architecture/astrology-disclaimer-projection-policy.md`
- VC5: `rg -n "natal|prediction|AI|degraded mode|missing birth time" docs/architecture/astrology-disclaimer-projection-policy.md`
- VC6: `rg -n "free|basic|premium|projection plan|B2C" docs/architecture/astrology-disclaimer-projection-policy.md`
- VC7: `rg -n "LLM|application-injected|does not author|does not mutate" docs/architecture/astrology-disclaimer-projection-policy.md`
- VC8: `rg -n "identified gap|gap_status|next_action|text_delta_justification" docs/architecture/astrology-disclaimer-projection-policy.md`
- VC9: `python -c "from app.main import app; assert 'astrology_disclaimer_projection_policy' not in str(app.openapi())"`
- VC10: `python -c "from app.main import app; assert all('disclaimer-policy' not in getattr(r, 'path', '') for r in app.routes)"`
- VC11: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC12: `git status --short -- backend/app frontend/src backend/tests backend/migrations`
- VC13: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md').exists()"`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `pytest -q`
- VC17: `git status --short -- backend/app frontend/src`

Before VC2, VC9, VC10 and VC13, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Disclaimer wording could drift into LLM output instead of remaining application-controlled.
- A new disclaimer could be created without an inventory gap, creating parallel product or legal wording.
- Free, basic and premium projection plans could attach different disclaimers without a documented policy.
- Missing birth time or degraded mode could produce client output without a visible limitation disclaimer.
- A documentation story could drift into frontend, API, DB, prompt, provider or admin implementation.

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

- `_story_briefs/cs-284-audit-existing-astrology-disclaimers-and-projection-disclaimer-policy.md`
- `backend/app/services/resources/templates/disclaimer_registry.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/guidance/guidance_service.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md`
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md`
- `_condamad/stories/CS-283-b2c-projection-entitlement-policy/00-story.md`
- `_condamad/stories/regression-guardrails.md`
