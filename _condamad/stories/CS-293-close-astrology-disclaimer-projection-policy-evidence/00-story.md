# Story CS-293 close-astrology-disclaimer-projection-policy-evidence: Close Astrology Disclaimer Projection Policy Evidence
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-293-close-astrology-disclaimer-projection-policy-evidence.md`.
- Related capsule: `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/00-story.md`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: CS-284 is still not evidenced because its canonical policy, evidence folder and final evidence artifact are absent.
- Source-alignment evidence: PASS; this story preserves the brief stakes: policy, inventory, plan mapping, LLM boundary and CS-284 closure proof.

## Objective

Close the missing CS-284 evidence by creating the canonical disclaimer projection policy and the persistent CONDAMAD artifacts that prove it.

The implementation must show that B2C astrology disclaimers are owned by application-controlled sources and attached to projection plans by policy.
It must not create a route, UI, migration, model, prompt rewrite or new legal policy.

## Target State

- `docs/architecture/astrology-disclaimer-projection-policy.md` exists as the canonical policy for B2C projection disclaimers.
- The CS-284 capsule contains an `evidence/` folder with a bounded disclaimer inventory.
- `generated/10-final-evidence.md` exists under CS-284 and proves closure of the missing policy and evidence gap.
- `beginner_summary_v1` and `client_interpretation_projection_v1` are mapped to applicable disclaimers by `free`, `basic` and `premium` plans.
- The policy states that the LLM never owns, creates, rewrites or mutates disclaimer text.
- Degraded mode and missing birth time are covered, or a product gap is documented with owner and next action.
- Runtime API neutrality is proven through `app.openapi()`, `app.routes` and `pytest` evidence.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-293-close-astrology-disclaimer-projection-policy-evidence.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-293`.
- Evidence 3: `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/00-story.md` - target closure contract read.
- Evidence 4: `docs/architecture/astrology-disclaimer-projection-policy.md` - absent before this story.
- Evidence 5: `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/` - absent before this story.
- Evidence 6: `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/10-final-evidence.md` - absent before this story.
- Evidence 7: `backend/app/services/resources/templates/disclaimer_registry.py` - static application disclaimer registry found.
- Evidence 8: `docs/architecture/official-product-primitives-public-projections.md` - public projection governance owner found.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - consulted through scoped resolver output only.
- Evidence 10: `resolve_guardrails.py` selected RG-002 and no exact disclaimer-projection guardrail.
- Source-alignment evidence: PASS; no source concern was softened into generic cleanup or moved outside the CS-284 closure boundary.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - CS-284 closure evidence and final evidence artifact.
  - Canonical architecture policy for B2C projection disclaimers.
  - Inventory across backend, frontend, docs and story briefs using bounded scans.
  - Classification of natal, prediction, AI, degraded mode and missing birth time usage.
  - Plan mapping for `beginner_summary_v1` and `client_interpretation_projection_v1`.
  - Proof that no API route or runtime public surface is introduced.
- Out of scope:
  - Frontend UI, API route creation, database schema, migrations, auth, i18n, styling, build tooling and prompt rewrite.
  - New legal policy drafting beyond documenting existing text ownership and product gaps.
  - Admin-only technical warning exposure to B2C clients.
  - Guardrail registry enrichment in `_condamad/stories/regression-guardrails.md`.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or runtime projection builder.
  - No database table, migration, prompt rewrite, provider change or new model.
  - No duplicate disclaimer source outside the existing static registry and canonical policy.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a backend-domain documentation and evidence closure story.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the policy document, CS-284 evidence artifacts and final closure evidence.
  - Reuse existing disclaimer registry, existing projection contracts and existing entitlement terminology.
  - Keep backend runtime code, API routes, frontend source, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep LLM output and prompt text outside disclaimer authorship.
  - Keep admin technical warnings outside B2C projection disclaimer payloads.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to create new legal wording beyond a documented inventory gap.
- Additional validation rules:
  - The policy must name `astrology_disclaimer_projection_policy` exactly.
  - The policy must inventory existing disclaimer references from backend, frontend, docs and story briefs.
  - The policy must classify usage as natal, prediction, AI, degraded mode or missing birth time.
  - The policy must map disclaimer applicability to `free`, `basic` and `premium` B2C projection plans.
  - The policy must state that disclaimers are controlled by application code and not authored by the LLM.
  - The policy must cover degraded mode and missing birth time, or document a product gap with owner and next action.
  - CS-284 `evidence/` and `generated/10-final-evidence.md` must exist after implementation.
  - `app.routes`, `app.openapi()`, `pytest` and scoped status prove no public API or application source drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing registry, projection docs, `app.routes`, `app.openapi()` and `pytest` prove the boundary. |
| Baseline Snapshot | yes | Before and after artifacts prove CS-284 moved from missing evidence to evidenced closure. |
| Ownership Routing | yes | Disclaimer registry, architecture policy and CS-284 evidence need separate canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this CS-284 closure story. |
| Contract Shape | yes | The policy has exact inventory, usage classes, plan mapping, LLM boundary and gap fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | LLM-authored disclaimers and undocumented projection attachment must stay out. |
| Persistent Evidence | yes | CS-284 evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | CS-284 policy document exists. | Evidence profile: baseline_before_after_diff; `python` checks `docs/architecture/astrology-disclaimer-projection-policy.md`. |
| AC2 | Existing disclaimers are inventoried. | Evidence profile: baseline_before_after_diff; `rg` scans backend, frontend, docs and `_story_briefs`. |
| AC3 | Usage classes are explicit. | Evidence profile: json_contract_shape; `rg` checks natal, prediction, AI, degraded mode and missing birth time. |
| AC4 | B2C plan mapping is explicit. | Evidence profile: json_contract_shape; `rg` checks `beginner_summary_v1`, `client_interpretation_projection_v1`, free, basic and premium. |
| AC5 | LLM disclaimer authorship is blocked. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks application-controlled and LLM boundary wording. |
| AC6 | Degraded states are resolved. | Evidence profile: json_contract_shape; `rg` checks degraded mode and missing birth time coverage or product gap. |
| AC7 | CS-284 final evidence exists. | Evidence profile: baseline_before_after_diff; `python` checks CS-284 evidence and `generated/10-final-evidence.md`. |
| AC8 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC9 | Regression tests stay green. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`. |
| AC10 | App source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-284 story, existing disclaimer registry, projection docs and relevant tests before creating artifacts. (AC: AC1, AC2)
- [ ] Task 2: Create `docs/architecture/astrology-disclaimer-projection-policy.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Persist a bounded inventory under CS-284 `evidence/disclaimer-inventory.md`. (AC: AC2, AC7)
- [ ] Task 4: Classify disclaimer usage as natal, prediction, AI, degraded mode and missing birth time. (AC: AC3, AC6)
- [ ] Task 5: Map disclaimer applicability to `beginner_summary_v1` and `client_interpretation_projection_v1` by plan. (AC: AC4)
- [ ] Task 6: Document that application code controls disclaimers and the LLM does not create or mutate them. (AC: AC5)
- [ ] Task 7: Record degraded mode and missing birth time coverage or product gap rows. (AC: AC6)
- [ ] Task 8: Persist validation output and scoped app-surface status under CS-284 evidence. (AC: AC7, AC8, AC10)
- [ ] Task 9: Create CS-284 `generated/10-final-evidence.md` with links to policy, inventory and validation proof. (AC: AC7)
- [ ] Task 10: Run targeted architecture checks and full backend validation from the activated venv. (AC: AC8, AC9)

## Files to Inspect First

- `_story_briefs/cs-293-close-astrology-disclaimer-projection-policy-evidence.md` - source brief.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/00-story.md` - target closure contract.
- `backend/app/services/resources/templates/disclaimer_registry.py` - existing static disclaimer registry.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - existing natal disclaimer injection.
- `backend/app/services/llm_generation/guidance/guidance_service.py` - existing guidance disclaimer behavior.
- `backend/app/services/llm_generation/shared/natal_context.py` - degraded natal context terminology.
- `docs/architecture/official-product-primitives-public-projections.md` - public projection governance owner.
- `docs/architecture/beginner-summary-v1-contract.md` - `beginner_summary_v1` contract.
- `docs/architecture/client-interpretation-projection-v1-contract.md` - `client_interpretation_projection_v1` contract.
- `docs/architecture/b2c-projection-entitlement-policy.md` - free, basic and premium entitlement policy.
- `backend/tests/architecture/test_api_contract_neutrality.py` - API-neutrality regression tests.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/services/resources/templates/disclaimer_registry.py` for static disclaimer texts.
  - `backend/app/services/llm_generation/natal/interpretation_service.py` for existing natal disclaimer injection.
  - `backend/app/services/llm_generation/guidance/guidance_service.py` for guidance disclaimer behavior.
  - CS-257, CS-258, CS-283 and CS-284 story contracts for projection, plan and closure boundaries.
  - `app.routes`, `app.openapi()`, scoped `git status`, `pytest` and targeted `rg` scans for no app-surface drift.
- Secondary evidence:
  - `docs/architecture/astrology-disclaimer-projection-policy.md`.
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md`.
- Static scans alone are not sufficient because:
  - public API neutrality must be proven from the loaded app.

## Contract Shape

- Contract type:
  - Markdown backend-domain policy and CONDAMAD evidence closure for CS-284.
- Fields:
  - `policy_id`: exact value `astrology_disclaimer_projection_policy`.
  - `inventory_scope`: backend, frontend, docs and story briefs searched for disclaimer references.
  - `source_owner`: canonical file, service or document owning each existing disclaimer behavior.
  - `usage_class`: one of natal, prediction, AI, degraded mode or missing birth time.
  - `projection_id`: `beginner_summary_v1` or `client_interpretation_projection_v1`.
  - `projection_plan`: one of free, basic or premium.
  - `injection_owner`: application component responsible for attaching the disclaimer.
  - `llm_boundary`: the LLM does not own, create, rewrite or mutate disclaimer text.
  - `gap_status`: covered, product gap or text delta justified by identified gap.
  - `closure_evidence`: paths proving CS-284 final evidence and validation output.
- Required fields:
  - `policy_id`
  - `inventory_scope`
  - `source_owner`
  - `usage_class`
  - `projection_id`
  - `projection_plan`
  - `injection_owner`
  - `llm_boundary`
  - `gap_status`
  - `closure_evidence`
- Optional fields:
  - `next_action` only for a product gap.
  - `text_delta_justification` only for a created or changed disclaimer text.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `astrology_disclaimer_projection_policy`.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/00-story.md`
  - `backend/app/services/resources/templates/disclaimer_registry.py`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - missing `docs/architecture/astrology-disclaimer-projection-policy.md`
  - missing `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/`
  - missing `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/10-final-evidence.md`
- Comparison after implementation:
  - `docs/architecture/astrology-disclaimer-projection-policy.md`
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md`
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt`
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/app-surface-status.txt`
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/10-final-evidence.md`
- Expected invariant:
  - The only intended repository delta is policy documentation plus CS-284 evidence and generated closure artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Static disclaimer registry | `backend/app/services/resources/templates/disclaimer_registry.py` | prompt templates or provider output |
| Projection disclaimer policy | `docs/architecture/astrology-disclaimer-projection-policy.md` | API routers, frontend, DB models |
| Public projection registry | `docs/architecture/official-product-primitives-public-projections.md` | duplicate projection registry |
| B2C plan entitlement terms | `docs/architecture/b2c-projection-entitlement-policy.md` | route-local plan copy |
| CS-284 closure evidence | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/` | application source folders |
| CS-284 final evidence | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/10-final-evidence.md` | informal notes |

## Mandatory Reuse / DRY Constraints

- Reuse `backend/app/services/resources/templates/disclaimer_registry.py` as the existing static disclaimer owner.
- Reuse existing natal and guidance disclaimer behavior instead of creating parallel disclaimer text sources.
- Reuse CS-257, CS-258 and CS-283 free, basic and premium B2C projection terminology.
- Reuse CS-284 evidence expectations instead of creating a separate closure capsule.
- Keep one canonical `astrology_disclaimer_projection_policy` document and one CS-284 inventory artifact.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts, migrations or generated clients.

## No Legacy / Forbidden Paths

- No legacy disclaimer source may bypass the static registry or the policy document.
- No compatibility disclaimer path may allow LLM-authored product or legal wording.
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
  - CS-284 cannot remain without `evidence/` and `generated/10-final-evidence.md`;
  - degraded mode and missing birth time cannot lose client-visible coverage;
  - public API routes, database migrations and frontend files cannot be introduced by this story.
- Guard mechanism:
  - targeted `rg` checks for required inventory, usage classes, plan mapping, LLM boundary and gap handling;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-284 evidence folder.
- Guard owner:
  - `docs/architecture/astrology-disclaimer-projection-policy.md`;
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md`;
  - `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/10-final-evidence.md`.
- Guard evidence:
  - `rg -n "astrology_disclaimer_projection_policy|beginner_summary_v1|client_interpretation_projection_v1" docs/architecture`;
  - `python -c "from app.main import app; assert 'astrology_disclaimer_projection_policy' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('disclaimer-policy' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src backend/tests backend/migrations`.

## Regression Guardrails

Scope vector:

- backend-domain policy documentation: yes;
- CS-284 evidence closure: yes;
- disclaimer registry source reference: yes;
- LLM generation source reference: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths are referenced as source owners, not modified. | `git status`; `python` loaded app checks. |
| Registry gap | No exact disclaimer-projection guardrail exists in resolver output. | Story-local `rg`, `pytest` and loaded app checks. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story references plan terms but does not change access rights.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Policy document | `docs/architecture/astrology-disclaimer-projection-policy.md` | Keep the canonical disclaimer projection policy. |
| Disclaimer inventory | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md` | Keep the bounded inventory. |
| Validation output | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt` | Keep command output for CS-284 closure. |
| Application surface status | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/source-checklist.md` | Record source coverage. |
| Final evidence | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/10-final-evidence.md` | Close CS-284 evidence handoff. |
| Review output | `_condamad/stories/CS-293-close-astrology-disclaimer-projection-policy-evidence/generated/11-code-review.md` | Keep review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this CS-284 closure story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/astrology-disclaimer-projection-policy.md` - new canonical policy document.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md` - bounded inventory artifact.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/app-surface-status.txt` - scoped non-change proof.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/source-checklist.md` - source coverage evidence.
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/10-final-evidence.md` - final CS-284 closure proof.

Likely tests:

- `backend/tests/architecture/test_api_contract_neutrality.py` - targeted architecture check for no public route drift.
- `docs/architecture/astrology-disclaimer-projection-policy.md` - checked by `rg` and `python` validation commands.

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
- VC2: `cd backend`
- VC3: `python -B -c "from app.main import app; assert 'astrology_disclaimer_projection_policy' not in str(app.openapi())"`
- VC4: `python -B -c "from app.main import app; assert all('disclaimer-policy' not in getattr(r, 'path', '') for r in app.routes)"`
- VC5: `ruff check .`
- VC6: `python -B -m pytest -q --tb=short`
- VC7: `pytest -q tests/architecture/test_api_contract_neutrality.py`
- VC8: `python -c "from pathlib import Path; assert Path('../docs/architecture/astrology-disclaimer-projection-policy.md').exists()"`
- VC9: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence').exists()"`
- VC10: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/10-final-evidence.md').exists()"`
- VC11: `rg -n "disclaimer|avertissement|IA|prediction|heure de naissance|mode degrade" . ../frontend ../docs ../_story_briefs`
- VC12: `rg -n "beginner_summary_v1|client_interpretation_projection_v1|free|basic|premium" ../docs/architecture/astrology-disclaimer-projection-policy.md`
- VC13: `rg -n "LLM|application-controlled|application code|does not create|does not mutate" ../docs/architecture/astrology-disclaimer-projection-policy.md`
- VC14: `git status --short -- app ../frontend/src tests migrations`
- VC15: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt').exists()"`

Before every `python`, `pytest` and `ruff` command, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- CS-284 could appear closed while its evidence folder or final evidence remains absent.
- Disclaimer wording could drift into LLM output instead of remaining application-controlled.
- Free, basic and premium projection plans could attach different disclaimers without documented policy.
- Missing birth time or degraded mode could produce client output without a visible limitation disclaimer.
- A documentation closure story could drift into frontend, API, DB, prompt, provider or admin implementation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep the implementation documentation and evidence focused unless a separate user decision authorizes code, DB, route, prompt or frontend work.
- Persist the required CS-284 evidence artifacts before requesting review.

## References

- `_story_briefs/cs-293-close-astrology-disclaimer-projection-policy-evidence.md`
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/00-story.md`
- `backend/app/services/resources/templates/disclaimer_registry.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/guidance/guidance_service.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `docs/architecture/official-product-primitives-public-projections.md`
- `docs/architecture/beginner-summary-v1-contract.md`
- `docs/architecture/client-interpretation-projection-v1-contract.md`
- `docs/architecture/b2c-projection-entitlement-policy.md`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/regression-guardrails.md`
