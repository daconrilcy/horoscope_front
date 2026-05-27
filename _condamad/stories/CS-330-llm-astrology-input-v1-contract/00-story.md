# Story CS-330 llm-astrology-input-v1-contract: Define llm_astrology_input_v1 Contract
Status: ready-to-review

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`.
- Related dependency: CS-254 defines `AINarrativeInputContract` as the internal narrative input owner.
- Related dependency: CS-256 defines `structured_facts_v1` as the stable fact projection.
- Related dependency: CS-258 defines `client_interpretation_projection_v1` as B2C shaping metadata.
- Related dependency: CS-259 defines `narrative_answer_audit_v1` anchors for hashes and evidence.
- Architecture source: `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md`.
- Transition source: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Existing owner found: `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`.
- Existing owner found: `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`.
- Existing owner found: `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: the natal LLM path still relies on broad chart payloads while richer internal contracts already exist.
- Source-alignment evidence: PASS; ACs preserve internal LLM contract creation, factual ownership, narrative ownership and no prompt wiring.

## Objective

Define the backend-domain contract `llm_astrology_input_v1` as the versioned internal input schema used by future LLM prompt composition.

The contract must wrap `AINarrativeInputContract`, consume `structured_facts_v1` as the canonical factual source, keep B2C projections as shaping
metadata only, expose limits and evidence explicitly, and keep raw runtime payloads out of the LLM input boundary.

## Target State

- `llm_astrology_input_v1` exists as a versioned internal backend contract.
- The contract separates `facts`, `signals`, `limits`, `evidence`, `shaping`, `provenance` and `exclusions`.
- `facts` is sourced from `structured_facts_v1`, not from raw chart or public payload carriers.
- `signals` is sourced from `AINarrativeInputContract` and keeps runtime-only or audit-only fields out of prompt-visible content.
- `shaping` can reference plan, module and editorial depth from `client_interpretation_projection_v1` metadata without becoming a factual source.
- `provenance` carries contract ids, source versions, `projection_hash`, `llm_input_hash` rules and compact prompt references.
- `evidence` uses `evidence_refs` or validation-ready references without embedding verbose audit payloads.
- No prompt template, provider integration, frontend source, API route, DB schema or migration is modified.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-330`.
- Evidence 3: `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md` - target contract read.
- Evidence 4: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md` - transition report read.
- Evidence 5: `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md` - narrative input source brief read.
- Evidence 6: `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md` - fact source brief read.
- Evidence 7: `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md` - shaping source brief read.
- Evidence 8: `_story_briefs/cs-259-define-narrative-answer-audit-v1.md` - audit source brief read.
- Evidence 9: targeted `rg` found no current `llm_astrology_input_v1` backend contract or test file.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup.
- Source-alignment evidence: PASS; the story keeps every named primitive in scope or explicitly out of scope.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend internal contract definition for `llm_astrology_input_v1`.
  - Contract source mapping for `facts`, `signals`, `limits`, `evidence`, `shaping`, `provenance` and `exclusions`.
  - Validation of prompt-visible, runtime-only, validation-only and audit-only boundaries.
  - Tests for minimal shape, deterministic hashes and forbidden source carriers.
  - Loaded app neutrality checks proving no API surface is introduced.
- Out of scope:
  - Frontend UI, public API route, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Prompt wording, prompt renderer wiring, provider calls, `NatalExecutionInput`, `ExecutionContext` and real LLM execution.
  - Removing `chart_json`, `natal_data`, public projections or existing runtime objects.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or generated API client for this contract.
  - No database table, migration, persistence write path or repository update.
  - No prompt template edit, provider integration, final prose renderer or LLM call.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend-domain LLM input contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the canonical internal contract and focused tests for `llm_astrology_input_v1`.
  - Reuse `structured_facts_v1`, `AINarrativeInputContract` and evidence validation owners before creating adjacent helpers.
  - Keep `client_interpretation_projection_v1` as shaping metadata, not as the factual source.
  - Keep API routes, frontend, DB, migrations, auth, i18n, style, prompt templates and build tooling unchanged.
  - Keep raw runtime payloads, public payload carriers, prompt text and provider responses outside the contract.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the final owner cannot live under `backend/app/domain/astrology/interpretation/**` without crossing service or prompt boundaries.
- Additional validation rules:
  - The contract must emit contract id `llm_astrology_input_v1`.
  - The contract must define the seven top-level blocks named in the source brief.
  - `facts` must use `structured_facts_v1` as its canonical source.
  - `signals` must use `AINarrativeInputContract` as its internal narrative owner.
  - B2C projection data must remain shaping metadata only.
  - `ChartObjectRuntimeData`, `CalculationGraph`, `chart_json` and `natal_data` must not be canonical sources.
  - `llm_input_hash` rules must cover every prompt-influencing block.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` evidence must prove no public API exposure was added.
  - The implementation must include an AST guard or targeted `rg` scan proving no parallel contract owner bypasses the selected module.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing builders, tests, `app.routes`, `app.openapi()` and `TestClient` prove the internal boundary. |
| Baseline Snapshot | yes | Before and after evidence must prove contract shape and no prompt or public surface drift. |
| Ownership Routing | yes | Facts, signals, shaping, evidence and audit anchors need separate canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this internal contract story. |
| Contract Shape | yes | `llm_astrology_input_v1` has exact blocks, source rules, hash rules and exclusions. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw chart carriers, runtime dumps, prompt text and B2C facts must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The internal contract exists. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`. |
| AC2 | The seven top-level blocks exist. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`. |
| AC3 | `facts` uses `structured_facts_v1`. | Evidence profile: ast_architecture_guard; `python` AST guard checks source mapping. |
| AC4 | `signals` uses `AINarrativeInputContract`. | Evidence profile: ast_architecture_guard; `python` AST guard checks imports and mapping. |
| AC5 | B2C projections are shaping only. | Evidence profile: targeted_forbidden_symbol_scan; `pytest` asserts source role; `rg` scans the contract. |
| AC6 | Raw chart carriers are not canonical. | Evidence profile: no_legacy_contract; `pytest` negative assertions; targeted `rg` scan. |
| AC7 | Hash provenance is deterministic. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`. |
| AC8 | Prompt wiring stays unchanged. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans prompt and provider paths. |
| AC9 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `TestClient` smoke stays unchanged. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-330 evidence paths. |

## Implementation Tasks

- [x] Task 1: Inspect target contract, transition report and existing builders before choosing the owner. (AC: AC3, AC4)
- [x] Task 2: Add or extend one canonical internal contract module for `llm_astrology_input_v1`. (AC: AC1)
- [x] Task 3: Define `facts`, `signals`, `limits`, `evidence`, `shaping`, `provenance` and `exclusions`. (AC: AC2)
- [x] Task 4: Map `facts` from `structured_facts_v1` without raw chart carrier ownership. (AC: AC3, AC6)
- [x] Task 5: Map `signals` from `AINarrativeInputContract` with prompt-visible role flags. (AC: AC4)
- [x] Task 6: Keep `client_interpretation_projection_v1` limited to shaping metadata. (AC: AC5)
- [x] Task 7: Define limits for missing data, unavailable sections and excluded calculation surfaces. (AC: AC2, AC6)
- [x] Task 8: Define evidence references and provenance including `projection_hash` and `llm_input_hash`. (AC: AC7)
- [x] Task 9: Add contract shape, hash and negative-source tests. (AC: AC1, AC2, AC6, AC7)
- [x] Task 10: Add loaded-app and targeted scan guards for public API, prompt and provider neutrality. (AC: AC8, AC9)
- [x] Task 11: Persist sample payload, validation and architecture evidence under the CS-330 evidence folder. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - source brief.
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md` - transition report.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md` - target contract.
- `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md` - narrative input contract source.
- `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md` - factual source contract.
- `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md` - shaping source contract.
- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md` - audit source contract.
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` - factual source owner.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - narrative input builder owner.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - narrative input contract owner.
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - B2C shaping owner.
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` - evidence reference validation owner.
- `backend/app/domain/astrology/projections/projection_hash.py` - hash helper owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - prompt-adjacent neutrality scan target.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` for factual input.
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` for narrative signals and readiness.
  - `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` for evidence reference validation.
  - `backend/app/domain/astrology/projections/projection_hash.py` for deterministic hash semantics.
  - `app.routes`, `app.openapi()`, `TestClient`, AST guard and targeted `rg` scans for public API and prompt neutrality.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`.
  - Targeted scans over the final contract, tests and prompt-adjacent service.
- Static scans alone are not sufficient because:
  - contract serialization, hash determinism and loaded-app public-surface neutrality must be proven at runtime.

## Contract Shape

- Contract type:
  - Backend-domain internal LLM input contract for astrology prompt composition.
- Fields:
  - `contract_id`: exact value `llm_astrology_input_v1`.
  - `contract_version`: stable version for this schema.
  - `facts`: prompt-eligible factual subset from `structured_facts_v1`.
  - `signals`: prompt-eligible interpretive signals and readiness flags from `AINarrativeInputContract`.
  - `limits`: missing data, unavailable sections, uncertainty markers and excluded calculations.
  - `evidence`: compact `evidence_refs` or validation references for grounding.
  - `shaping`: plan, module, depth profile and editorial angle metadata.
  - `provenance`: source versions, `projection_hash`, `llm_input_hash`, prompt ref and source ids.
  - `exclusions`: raw runtime carriers, public payload carriers, prompt text, provider output and audit payloads.
- Required fields:
  - `contract_id`
  - `contract_version`
  - `facts`
  - `signals`
  - `limits`
  - `evidence`
  - `shaping`
  - `provenance`
  - `exclusions`
- Optional fields:
  - none for the top-level contract; empty collections or explicit nulls encode unavailable optional source data.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - emitted JSON keys must use stable snake_case names from this contract.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `llm_astrology_input_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
  - `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md`
  - `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
  - targeted search output proving no current `llm_astrology_input_v1` backend contract or test file.
- Comparison after implementation:
  - `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/sample-payload.json`
  - `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/validation.txt`
  - `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/public-surface-guard.txt`
  - `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/architecture-guard.txt`
- Expected invariant:
  - The only intended application delta is the canonical internal LLM input contract, adjacent helpers and focused backend tests.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `llm_astrology_input_v1` contract | `backend/app/domain/astrology/interpretation/**` | API routers, frontend or provider code |
| Factual source | `structured_facts_v1` builder output | `chart_json`, `natal_data` or raw runtime |
| Narrative signals | `AINarrativeInputContract` | prompt templates or provider output |
| Shaping metadata | `client_interpretation_projection_v1` metadata | factual source ownership |
| Evidence references | `evidence_refs_validation.py` | verbose audit payload injection |
| Hash identity | `projection_hash.py` and provenance block | ad hoc local hashing |
| Evidence artifacts | `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse `structured_facts_v1_builder.py` as the factual source boundary.
- Reuse `AINarrativeInputContract` fields for signals, readiness and source versions before adding adjacent fields.
- Reuse `client_interpretation_projection_v1_builder.py` only for plan and editorial shaping metadata.
- Reuse `evidence_refs_validation.py` and `projection_hash.py` for evidence and deterministic hash semantics.
- Keep one canonical contract owner for `llm_astrology_input_v1`; do not create a parallel prompt input schema.
- Do not add external packages, public routes, frontend helpers, DB models, migrations, LLM providers or generated clients.

## No Legacy / Forbidden Paths

- No legacy prompt input path may become the owner for `llm_astrology_input_v1`.
- No compatibility route path may expose this internal contract.
- No fallback branch may promote raw chart carriers as canonical LLM input.
- Do not create aliases, shims, wrappers or parallel schemas for the same contract.
- Do not place prompt text, provider responses, final prose, raw debug traces or verbose audit internals inside the contract.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as contract owners

## Reintroduction Guard

- Guard target:
  - duplicate LLM input schemas cannot appear outside the canonical owner;
  - facts cannot bypass `structured_facts_v1`;
  - signals cannot bypass `AINarrativeInputContract`;
  - B2C projection data cannot become a factual source;
  - raw runtime carriers and broad chart payloads cannot become canonical input;
  - public API routes and OpenAPI schemas cannot expose this internal contract.
- Guard mechanism:
  - focused unit tests for shape, source mapping, hash determinism and forbidden source carriers;
  - AST guard or targeted `rg` scan for duplicate owner and forbidden field names;
  - `app.routes`, `app.openapi()` and `TestClient` neutrality checks;
  - persisted sample payload and validation transcript under the CS-330 evidence folder.
- Guard owner:
  - final `llm_astrology_input_v1` contract module;
  - `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`;
  - `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/validation.txt`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`;
  - `python -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('llm_astrology' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `rg -n "llm_astrology_input_v1|ChartObjectRuntimeData|CalculationGraph|chart_json|natal_data" app tests`.

## Regression Guardrails

Scope vector:

- backend-domain contract: yes;
- backend interpretation owners: yes;
- backend unit tests: yes;
- prompt-generation validation paths: yes;
- public API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend ownership stays inside canonical app paths. | AST guard; targeted `pytest`; loaded app checks. |
| RG-022 | Backend prompt-generation validation paths must stay collected. | `pytest`; validation transcript. |
| Registry gap | No exact `llm_astrology_input_v1` guardrail exists in scoped resolver output. | Story-local `rg` and loaded app guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story defines an internal LLM input contract.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Sample payload | `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/sample-payload.json` | Keep representative contract output. |
| Validation output | `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/validation.txt` | Keep lint and test transcript. |
| Public surface guard | `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/public-surface-guard.txt` | Prove API neutrality. |
| Architecture guard | `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/architecture-guard.txt` | Prove owner reuse. |
| Review output | `_condamad/stories/CS-330-llm-astrology-input-v1-contract/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this backend contract story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - canonical internal contract.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - possible typed source role support.
- `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/sample-payload.json` - sample output.
- `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/public-surface-guard.txt` - route and OpenAPI proof.
- `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/architecture-guard.txt` - owner and scan proof.

Likely tests:

- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - contract shape, hash and forbidden-source tests.
- `backend/tests/architecture/test_llm_astrology_input_boundary.py` - public exposure and owner guard when the existing pattern fits.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public or internal API route is touched.
- `backend/app/infra/db/**` - out of scope; no persistence adapter is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `backend/app/services/llm_generation/**` - out of scope; no prompt runtime wiring is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- VC6: `pytest -q tests --tb=short`
- VC7: `python -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"`
- VC8: `python -c "from app.main import app; assert all('llm_astrology' not in getattr(r, 'path', '') for r in app.routes)"`
- VC9: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/validation.txt').exists()"`
- VC10: `rg -n "llm_astrology_input_v1|structured_facts_v1|AINarrativeInputContract|ChartObjectRuntimeData|chart_json|natal_data" app tests`
- VC11: `rg -n "llm_astrology_input_v1|prompt_template|provider_response|NatalExecutionInput|ExecutionContext" app/services/llm_generation tests`

Before VC3 through VC11, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The contract could copy `structured_facts_v1` instead of referencing it as the factual source boundary.
- B2C projection metadata could drift into factual ownership.
- Runtime-only or audit-only fields could become prompt-visible without an explicit role.
- Hash identity could ignore a prompt-influencing block.
- A contract story could drift into prompt wiring, API exposure, persistence, provider work or frontend work.
- Negative scans could be too broad and confuse existing transition carriers with newly authorized source ownership.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Reuse the closest existing interpretation, evidence and hash owners before creating adjacent helpers.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md`
- `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md`
- `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md`
- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`
- `backend/app/domain/astrology/projections/projection_hash.py`
- `_condamad/stories/regression-guardrails.md`
