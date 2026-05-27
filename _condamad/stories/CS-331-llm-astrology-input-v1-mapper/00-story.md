# Story CS-331 llm-astrology-input-v1-mapper: Map Astrological Richness To llm_astrology_input_v1
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`.
- Upstream story: CS-330 defines the target `llm_astrology_input_v1` internal contract.
- Architecture source: `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md`.
- Target contract source: `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md`.
- Transition source: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Existing owner found: `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`.
- Existing owner found: `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`.
- Existing owner found: `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`.
- Existing evidence owner found: `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: rich calculated facts and pre-narrative signals exist, but no deterministic mapper feeds `llm_astrology_input_v1`.
- Source-alignment evidence: PASS; ACs preserve facts, signals, limits, evidence, shaping and raw-runtime exclusion stakes.

## Objective

Create the backend-domain builder or adapter that maps existing astrology interpretation surfaces into `llm_astrology_input_v1`.

The mapper must give the future prompt a rich, deterministic, prompt-readable input without using `chart_json` as the canonical source.

## Target State

- A canonical `llm_astrology_input_v1` mapper exists under the astrology interpretation domain.
- `facts` is populated from `structured_facts_v1` structural facts, positions, signs, houses, aspects, axes and missing-data facts.
- Synthetic calculated facts include elements, modalities, polarities, dominants, dignities, forces, weights or scores when already available.
- `signals` is populated from `AINarrativeInputContract` interpretive signals, readiness flags and masking policy.
- `limits` exposes missing, uncertain or intentionally excluded data in a prompt-usable shape.
- `evidence` contains compact `evidence_refs` or validation-ready references tied to allowed sources.
- `shaping` carries plan, module, section and depth metadata without becoming a factual source.
- Tests cover one complete natal profile, one missing-data profile and fact-signal non-duplication.
- Raw runtime objects and public chart carriers are not serialized by the LLM input contract.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-331`.
- Evidence 3: `_condamad/stories/CS-330-llm-astrology-input-v1-contract/00-story.md` - upstream target contract story read.
- Evidence 4: `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md` - target matrix read.
- Evidence 5: targeted search found `structured_facts_v1_builder.py`, `ai_narrative_input_builder.py` and B2C shaping builder.
- Evidence 6: targeted search found `evidence_refs_validation.py` and related evidence tests instead of a file named `evidence_refs.py`.
- Evidence 7: targeted search found no current `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup.
- Repository structure alert: `backend/app/domain/astrology/interpretation/evidence_refs.py` is absent in this workspace.
- Source-alignment evidence: PASS; the story maps every named brief primitive or states it out of scope.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend internal mapper or builder for `llm_astrology_input_v1`.
  - Mapping from `structured_facts_v1` into `facts`, including positions, signs, elements, modalities, polarities, houses and aspects.
  - Mapping from `AINarrativeInputContract` into `signals` and readiness-related `limits`.
  - Mapping from evidence validation surfaces into compact `evidence`.
  - Mapping from plan/module/depth metadata into `shaping`.
  - Unit and architecture tests for mapping, missing data, non-duplication and forbidden sources.
- Out of scope:
  - Frontend UI, public API route, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Prompt wording, prompt renderer wiring, provider calls, `NatalExecutionInput`, `ExecutionContext` and real LLM execution.
  - Removing `chart_json`, `natal_data`, public projections or existing runtime objects.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI response model or generated API client for this mapper.
  - No database table, migration, repository write path or persistence backfill.
  - No prompt template edit, provider integration, final prose renderer or LLM call.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend-domain LLM input mapping contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the canonical mapper, adjacent domain helpers and focused tests for `llm_astrology_input_v1`.
  - Reuse `structured_facts_v1`, `AINarrativeInputContract`, B2C shaping metadata and evidence validation owners.
  - Keep `chart_json`, `natal_data`, `CalculationGraph` and `ChartObjectRuntimeData` out of the serialized LLM input.
  - Keep prompt templates, providers, public API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the final mapper cannot use CS-330 contract fields without changing prompt runtime ownership.
- Additional validation rules:
  - The mapper must emit contract id `llm_astrology_input_v1`.
  - `facts` must use `structured_facts_v1` as its canonical source.
  - `signals` must use `AINarrativeInputContract` as its internal narrative source.
  - `limits` must include missing data and excluded surfaces from existing owners.
  - `evidence` must use compact refs tied to allowed sources, not verbose audit payloads.
  - `shaping` must stay separated from `facts`.
  - `chart_json`, `natal_data`, `CalculationGraph` and `ChartObjectRuntimeData` must not be serialized.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` evidence must prove no public API exposure was added.
  - An AST guard or targeted `rg` scan must prove no parallel mapper bypasses the selected module.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing builders, mapper tests, `app.routes`, `app.openapi()` and `TestClient` prove runtime boundary. |
| Baseline Snapshot | yes | Before and after evidence must prove mapper shape and no public or prompt surface drift. |
| Ownership Routing | yes | Facts, signals, limits, evidence and shaping need separate canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this internal mapper story. |
| Contract Shape | yes | `llm_astrology_input_v1` has exact blocks, source rules and serialized exclusions. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw runtime carriers and public chart payloads must stay absent from LLM input. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The canonical mapper exists. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`. |
| AC2 | `facts` maps from `structured_facts_v1`. | Evidence profile: ast_architecture_guard; `python` AST guard checks source mapping. |
| AC3 | `signals` maps from `AINarrativeInputContract`. | Evidence profile: ast_architecture_guard; `python` AST guard checks imports and mapping. |
| AC4 | `limits` exposes missing data. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`. |
| AC5 | `evidence` uses compact refs. | Evidence profile: json_contract_shape; `pytest` checks allowed evidence source refs. |
| AC6 | `shaping` stays separate from facts. | Evidence profile: targeted_forbidden_symbol_scan; `pytest` asserts source role; `rg` scans the mapper. |
| AC7 | Complete natal mapping is covered. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`. |
| AC8 | Missing-data mapping is covered. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`. |
| AC9 | Field ownership is disjoint. | Evidence profile: json_contract_shape; `pytest` asserts disjoint field ownership. |
| AC10 | Raw carriers are not serialized. | Evidence profile: no_legacy_contract; `pytest` negative assertions; targeted `rg` scan. |
| AC11 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `TestClient` smoke. |
| AC12 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-331 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-330, target architecture and current interpretation builders before editing. (AC: AC1, AC2, AC3)
- [ ] Task 2: Add or complete one canonical mapper for `llm_astrology_input_v1`. (AC: AC1)
- [ ] Task 3: Map structural positions, signs, elements, modalities, polarities, houses, aspects, axes and missing facts from `structured_facts_v1`. (AC: AC2)
- [ ] Task 4: Map dignity, force, weight, score, dominance, house, rulership and readiness signals from `AINarrativeInputContract` when available. (AC: AC3)
- [ ] Task 5: Add explicit `limits` for missing data, uncertain inputs and excluded surfaces. (AC: AC4, AC8)
- [ ] Task 6: Add compact evidence refs from the existing evidence validation owner. (AC: AC5)
- [ ] Task 7: Add plan/module/depth shaping metadata without factual ownership. (AC: AC6)
- [ ] Task 8: Add complete natal and missing-data tests. (AC: AC7, AC8)
- [ ] Task 9: Add non-duplication tests between facts and signals. (AC: AC9)
- [ ] Task 10: Add guards against raw runtime and chart carrier serialization. (AC: AC10)
- [ ] Task 11: Add loaded-app and targeted scan guards for public API neutrality. (AC: AC11)
- [ ] Task 12: Persist sample payload, validation and architecture evidence under the CS-331 evidence folder. (AC: AC12)

## Files to Inspect First

- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md` - source brief.
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - upstream contract brief.
- `_condamad/stories/CS-330-llm-astrology-input-v1-contract/00-story.md` - upstream story.
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md` - transition report.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md` - target flow.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md` - target block matrix.
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` - factual source owner.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - narrative input builder owner.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - narrative input contract owner.
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - B2C shaping owner.
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` - evidence reference validation owner.
- `backend/app/domain/astrology/interpretation/evidence_refs.py` - expected implementation-created path only if the mapper needs it.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` for factual input.
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` for narrative signals and readiness.
  - `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` for evidence reference validation.
  - `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` for shaping metadata.
  - `app.routes`, `app.openapi()`, `TestClient`, AST guard and targeted `rg` scans for public API and prompt neutrality.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`.
  - Targeted scans over the final mapper, tests and prompt-adjacent service.
- Static scans alone are not sufficient because:
  - contract serialization, mapping behavior and loaded-app public-surface neutrality must be proven at runtime.

## Contract Shape

- Contract type:
  - Backend-domain internal mapper from astrology interpretation owners to `llm_astrology_input_v1`.
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
  - `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
  - `_condamad/stories/CS-330-llm-astrology-input-v1-contract/00-story.md`
  - `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md`
  - targeted search output proving no current `llm_astrology_input_v1` mapper module.
- Comparison after implementation:
  - `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/sample-payload.json`
  - `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/validation.txt`
  - `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/public-surface-guard.txt`
  - `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/architecture-guard.txt`
- Expected invariant:
  - The only intended application delta is the canonical internal mapper, adjacent domain helpers and focused backend tests.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `llm_astrology_input_v1` mapper | `backend/app/domain/astrology/interpretation/**` | API routers, frontend or provider code |
| Factual source | `structured_facts_v1` builder output | `chart_json`, `natal_data` or raw runtime |
| Narrative signals | `AINarrativeInputContract` | prompt templates or provider output |
| Limits source | structured facts plus narrative readiness | prompt disclaimers as source of truth |
| Shaping metadata | `client_interpretation_projection_v1` metadata | factual source ownership |
| Evidence references | `evidence_refs_validation.py` or adjacent domain ref helper | verbose audit payload injection |
| Evidence artifacts | `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse `structured_facts_v1_builder.py` as the factual source boundary.
- Reuse `AINarrativeInputContract` fields for signals, readiness and source versions.
- Reuse `client_interpretation_projection_v1_builder.py` only for plan, module and editorial shaping metadata.
- Reuse `evidence_refs_validation.py` or an adjacent interpretation-domain helper for compact evidence references.
- Keep one canonical mapper owner for `llm_astrology_input_v1`; do not create a parallel prompt input schema.
- Do not add external packages, public routes, frontend helpers, DB models, migrations, LLM providers or generated clients.

## No Legacy / Forbidden Paths

- No legacy prompt input path may become the owner for `llm_astrology_input_v1`.
- No compatibility route path may expose this internal mapper.
- No fallback branch may promote raw chart carriers as canonical LLM input.
- Do not create aliases, shims, wrappers or parallel schemas for the same mapper.
- Do not serialize prompt text, provider responses, final prose, raw debug traces or verbose audit internals.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as mapper owners

## Reintroduction Guard

- Guard target:
  - duplicate LLM input mappers cannot appear outside the canonical owner;
  - facts cannot bypass `structured_facts_v1`;
  - signals cannot bypass `AINarrativeInputContract`;
  - shaping cannot become factual source ownership;
  - raw runtime carriers and broad chart payloads cannot be serialized;
  - public API routes and OpenAPI schemas cannot expose this internal mapper.
- Guard mechanism:
  - focused unit tests for mapping, missing data, non-duplication and forbidden source carriers;
  - AST guard or targeted `rg` scan for duplicate owner and forbidden field names;
  - `app.routes`, `app.openapi()` and `TestClient` neutrality checks;
  - persisted sample payload and validation transcript under the CS-331 evidence folder.
- Guard owner:
  - final `llm_astrology_input_v1` mapper module;
  - `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`;
  - `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/validation.txt`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`;
  - `python -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('llm_astrology' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `rg -n "llm_astrology_input_v1|ChartObjectRuntimeData|CalculationGraph|chart_json|natal_data" app tests`.

## Regression Guardrails

Scope vector:

- backend-domain mapper: yes;
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
| Registry gap | No exact `llm_astrology_input_v1` mapper guardrail exists in scoped resolver output. | Story-local `rg` and loaded app guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story defines an internal LLM input mapper.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Sample payload | `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/sample-payload.json` | Keep representative contract output. |
| Validation output | `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/validation.txt` | Keep lint and test transcript. |
| Public surface guard | `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/public-surface-guard.txt` | Prove API neutrality. |
| Architecture guard | `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/architecture-guard.txt` | Prove owner reuse. |
| Review output | `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this backend mapper story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - canonical internal mapper.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - possible typed source role support.
- `backend/app/domain/astrology/interpretation/evidence_refs.py` - implementation-created path only for compact evidence helpers.
- `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/sample-payload.json` - sample output.
- `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/public-surface-guard.txt` - route and OpenAPI proof.
- `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/architecture-guard.txt` - owner and scan proof.

Likely tests:

- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - mapper shape, missing data and forbidden-source tests.
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
- VC6: `pytest -q tests/architecture/test_llm_astrology_input_boundary.py`
- VC7: `pytest -q tests --tb=short`
- VC8: `python -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"`
- VC9: `python -c "from app.main import app; assert all('llm_astrology' not in getattr(r, 'path', '') for r in app.routes)"`
- VC10: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/validation.txt').exists()"`
- VC11: `rg -n "llm_astrology_input_v1|structured_facts_v1|AINarrativeInputContract|signals|limits|evidence_refs|chart_json|natal_data" app tests`
- VC12: `rg -n "ChartObjectRuntimeData|CalculationGraph|provider_response|prompt_template|NatalExecutionInput|ExecutionContext" app tests`

Before VC3 through VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The mapper could copy flat facts without preserving pre-narrative nuance.
- Facts and signals could duplicate the same concept instead of keeping owner boundaries.
- Missing data could stay hidden from the future prompt and increase LLM invention risk.
- B2C shaping metadata could drift into factual ownership.
- Runtime-only or audit-only fields could become prompt-visible without a role.
- A mapper story could drift into prompt wiring, API exposure, persistence, provider work or frontend work.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Reuse the closest existing interpretation, evidence and shaping owners before creating adjacent helpers.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_condamad/stories/CS-330-llm-astrology-input-v1-contract/00-story.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`
- `_condamad/stories/regression-guardrails.md`
