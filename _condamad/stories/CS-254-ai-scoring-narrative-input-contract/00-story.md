# Story CS-254 ai-scoring-narrative-input-contract: Define AI Scoring And Narrative Input Contract
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md`.
- Remapped architecture item: `SC-ARCH-008`.
- Related dependency: CS-248 defines trace and provenance expectations for explainable scoring sources.
- Related dependency: CS-251 classifies raw `interpretation_input` as internal or LLM-only, not public API payload.
- Related dependency: CS-252 defines doctrine and school governance inputs that may feed pre-narrative signals.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: define one versioned internal facts contract for AI scoring and narration without making prompts a truth source.
- Source-alignment evidence: PASS; contract fields, prompt non-authority, public projection links and boundary tests are preserved.

## Objective

Create one internal backend-domain input contract for AI scoring, narrative preparation, LLM generation and controlled debug.

The implementation must keep canonical runtime facts upstream, pre-narrative signals separated, public projections linked but not embedded,
and prompt or LLM output data outside calculation ownership.

## Target State

- A versioned internal contract exposes `structural_facts`, `interpretive_signals`, `readiness_flags`, `source_versions`, `masking_policy`
  and `public_projection_links`.
- Structural facts remain derived from canonical calculation runtime and typed projection owners.
- Interpretive signals remain pre-narrative structured data, not final prose or prompt text.
- AI scoring and narrative preparation consume the same contract instead of reading prompt strings as astrology truth.
- Public projection links name controlled public owners without making this contract an API surface.
- Boundary guards prove calculation modules do not accept narrative, prompt, LLM output or final prose tokens.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to convert `CS-254` from `brief-ready` to `ready-to-dev`.
- Evidence 3: `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` - existing internal input contracts found.
- Evidence 4: `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` - current builder owner found.
- Evidence 5: `backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_contracts.py` - contract tests found.
- Evidence 6: `backend/tests/architecture/test_chart_interpretation_input_boundary.py` - prompt and narrative boundary guard found.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.
- Evidence 8: `resolve_guardrails.py` - scoped resolver run for backend-domain interpretation, runtime contract and no-public-api surfaces.
- Source-alignment evidence: PASS; ACs cover versioning, structural separation, prompt non-authority, tests, provider neutrality and public projection control.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Internal AI scoring and narrative input contract under backend astrology interpretation ownership.
  - Versioned sections for structural facts, interpretive signals, readiness flags, source versions, masking policy and public projection links.
  - Builder or adapter behavior that assembles the contract from canonical runtime and pre-narrative projection owners.
  - Tests proving calculation, interpretation and narration remain separated.
  - Architecture guards blocking narrative tokens in calculation modules.
  - Runtime-neutral proof through `app.openapi()`, `app.routes`, `pytest` and `TestClient`.
- Out of scope:
  - Frontend UI, public API exposure, DB schema, migrations, auth, i18n, styling, build tooling and provider integration.
  - Prompt authoring, commercial scoring policy, LLM provider calls, final narrative rendering and generated client changes.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint or OpenAPI schema for the AI input contract.
  - No prompt template creation or LLM gateway integration.
  - No scoring business policy decision.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the internal AI scoring and narrative input contract plus targeted builder or adapter wiring.
  - Keep canonical calculation runtime upstream of the contract.
  - Keep prompt text, LLM output and final prose outside calculation modules.
  - Keep public API, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: scoring policy requires product thresholds or paid-feature behavior beyond structural contract shape.
- Additional validation rules:
  - The contract exposes exactly one stable contract version field.
  - `structural_facts` and `interpretive_signals` are separate top-level sections.
  - `readiness_flags`, `source_versions`, `masking_policy` and `public_projection_links` are present in the contract shape.
  - Calculation modules do not import prompt, LLM gateway, narration service or final prose owners.
  - Prompt templates and LLM outputs are not accepted as source inputs for structural facts.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove no public API surface delta.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Canonical runtime, builder tests, `app.routes`, `app.openapi()` and `TestClient` prove source boundaries. |
| Baseline Snapshot | yes | Before and after evidence must show internal contract delta without public payload drift. |
| Ownership Routing | yes | Contract, builder, scoring adapters, narration prep, public projection links and guards need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this internal contract story. |
| Contract Shape | yes | The versioned input contract is the core implementation surface. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Prompt, narrative and final prose tokens must stay out of calculation ownership. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The AI input contract is versioned. | Evidence profile: json_contract_shape; `pytest` runs the AI contract test file. |
| AC2 | Structural facts are separated. | Evidence profile: json_contract_shape; `pytest` runs the AI contract test file. |
| AC3 | Interpretive signals are separated. | Evidence profile: json_contract_shape; `pytest` runs the AI contract test file. |
| AC4 | Prompt text is not a truth source. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_ai_narrative_input_boundary.py`. |
| AC5 | Provider integration is not added. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans OpenAI, AIEngineAdapter and chat completions in touched files. |
| AC6 | Public projection links stay controlled. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `TestClient` remains usable. |
| AC7 | Calculation modules reject narrative tokens. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_ai_narrative_input_boundary.py`. |
| AC8 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-254 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Add the internal versioned AI scoring and narrative input contract under astrology interpretation ownership. (AC: AC1)
- [ ] Task 2: Model `structural_facts` from canonical runtime facts without prompt, LLM output or final prose input. (AC: AC2, AC4)
- [ ] Task 3: Model `interpretive_signals` as pre-narrative structured signals distinct from structural facts. (AC: AC3)
- [ ] Task 4: Add `readiness_flags`, `source_versions`, `masking_policy` and `public_projection_links` to the contract. (AC: AC1, AC6)
- [ ] Task 5: Add or extend the builder that adapts existing interpretation input into the AI input contract. (AC: AC2, AC3)
- [ ] Task 6: Add contract unit tests for version, sections, source versions, masking policy and public projection links. (AC: AC1, AC2, AC3)
- [ ] Task 7: Add architecture guards for calculation-to-interpretation-to-narration direction. (AC: AC4, AC7)
- [ ] Task 8: Add targeted scans proving no provider integration or new public API surface. (AC: AC5, AC6)
- [ ] Task 9: Persist validation, shape and runtime-neutrality evidence under the CS-254 evidence folder. (AC: AC8)

## Files to Inspect First

- `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md` - source contract.
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/00-story.md` - provenance dependency.
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/00-story.md` - public projection dependency.
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/00-story.md` - doctrine governance dependency.
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` - existing internal input contracts.
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` - existing builder owner.
- `backend/app/domain/astrology/interpretation/chart_object_interpretation_projector.py` - structured object projector.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - canonical chart object runtime source.
- `backend/app/domain/llm/runtime/contracts.py` - LLM runtime boundary source for non-authority checks.
- `backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_contracts.py` - existing contract tests.
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py` - existing calculation and prompt boundary guard.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/**` canonical calculation outputs.
  - `backend/app/domain/astrology/interpretation/**` pre-narrative projection owners.
  - `backend/app/domain/llm/runtime/contracts.py` only as downstream LLM runtime boundary, not as astrology truth.
  - `AST guard`, `app.routes`, `app.openapi()` and `TestClient`.
- Secondary evidence:
  - Targeted `rg` scans for prompt, LLM, provider, final prose and public schema symbols in touched backend files.
- Static scans alone are not sufficient because:
  - contract assembly, runtime-neutrality and boundary direction must be proven by deterministic tests and loaded app checks.

## Contract Shape

- Contract type:
  - internal typed backend contract for AI scoring, narrative preparation, LLM generation input and controlled debug.
- Fields:
  - `contract_version`: stable version string.
  - `structural_facts`: canonical calculation facts and typed runtime identifiers.
  - `interpretive_signals`: pre-narrative structured signals derived from interpretation owners.
  - `readiness_flags`: booleans or enum values describing contract completeness for scoring and narration.
  - `source_versions`: runtime, doctrine, graph, projection and reference versions used to build the contract.
  - `masking_policy`: structured privacy and redaction policy for downstream LLM input.
  - `public_projection_links`: references to controlled public projection owners or identifiers.
  - `debug_context`: bounded debug metadata for traceability without final prose.
- Required fields:
  - `contract_version`
  - `structural_facts`
  - `interpretive_signals`
  - `readiness_flags`
  - `source_versions`
  - `masking_policy`
  - `public_projection_links`
- Optional fields:
  - `debug_context`
- Forbidden fields:
  - `prompt`
  - `llm_output`
  - `final_narrative`
  - `rendered_text`
  - `provider_response`
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - no public JSON key is added by this story.
- Frontend type impact:
  - none; no frontend contract changes are authorized.
- Generated contract impact:
  - `app.openapi()` must not expose the internal AI scoring and narrative input contract.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/contract-before.md`
  - `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/contract-after.md`
  - `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/openapi-after.json`
- Expected invariant:
  - The only intended behavior delta is an internal versioned backend input contract plus targeted tests and guards.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| AI input contract | `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` | API routers, DB models, frontend |
| Contract builder | `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` | prompt templates or LLM gateway |
| Structural facts | `backend/app/domain/astrology/runtime/**` and interpretation projectors | prompt, narration or provider modules |
| Pre-narrative signals | `backend/app/domain/astrology/interpretation/**` | calculation modules |
| Public projection links | documented references to public projection owners | raw public payload expansion |
| Boundary guards | `backend/tests/architecture/test_ai_narrative_input_boundary.py` | manual-only review |
| Contract tests | `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py` | broad integration tests only |

## Mandatory Reuse / DRY Constraints

- Reuse existing `chart_interpretation_input_contracts.py` primitives before introducing parallel object, aspect or dignity vocabularies.
- Reuse `ChartInterpretationInputBuilder` outputs or a thin adapter from that builder for AI contract assembly.
- Reuse canonical runtime fields from `ChartObjectRuntimeData`, `NatalResult` and existing interpretation projectors.
- Keep one version field and one contract owner for AI scoring and narrative input.
- Do not duplicate public projection schemas inside the internal contract.
- Do not add external packages or custom serialization tooling.

## No Legacy / Forbidden Paths

- No legacy prompt-owned astrology facts may be added.
- No compatibility path may allow LLM output to populate structural facts.
- No fallback path may read final prose as calculation input.
- No shim, alias or wrapper may expose this contract as public API.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - prompt template files as canonical astrology facts
  - provider gateway modules as structural fact owners

## Reintroduction Guard

- Guard target:
  - prompt strings cannot become structural fact inputs;
  - LLM outputs cannot become calculation truth;
  - final narrative tokens cannot enter calculation modules;
  - public API schemas cannot expose the internal contract;
  - provider integration cannot be introduced by this story.
- Guard mechanism:
  - unit tests for contract shape and builder assembly;
  - AST guard for calculation, interpretation and narration dependency direction;
  - targeted `rg` scans for prompt, LLM, provider and final prose tokens in touched files;
  - `TestClient`, `app.routes` and `app.openapi()` neutrality checks.
- Guard owner:
  - `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`;
  - `backend/tests/architecture/test_ai_narrative_input_boundary.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`;
  - `pytest -q backend/tests/architecture/test_ai_narrative_input_boundary.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()` and `TestClient`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-100 `CS-165-construire-builder-interpretation-aspects` | Domain astrology must not call LLM or produce silent text fallbacks. | `pytest`; targeted `rg`. |
| RG-102 `CS-167-separer-semantique-et-editorial-aspects` | Semantic facts stay between runtime and editorial renderer. | `pytest`; AST guard. |
| RG-143 `CS-216-advanced-planetary-conditions-interpretation-profiles` | Pre-narrative profiles stay structured and non-public. | `pytest`; targeted `rg`. |
| RG-144 `CS-217-unified-chart-object-runtime-contract` | Chart object runtime remains the canonical structural source. | `pytest`; AST guard. |
| Needs-investigation | No exact CS-254 route-specific guardrail exists for this internal contract. | Registry gap recorded; no registry edit. |

Non-applicable examples:

- RG-047 frontend inline styles is out of scope because this story does not touch `frontend/src/**`.
- RG-003 API route architecture is out of scope because this story adds no route.
- RG-007 admin LLM observability is out of scope because this story adds no admin endpoint.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/validation.md` | Keep lint, tests and scans. |
| Contract before | `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/contract-before.md` | Capture prior input shape. |
| Contract after | `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/contract-after.md` | Capture final input shape. |
| OpenAPI before | `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/openapi-before.json` | Prove public API baseline. |
| OpenAPI after | `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/openapi-after.json` | Prove no public API exposure. |
| Boundary scans | `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/boundary-scans.md` | Record prompt and provider scans. |
| Review output | `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this internal contract story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - define the versioned internal contract.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - assemble the contract from runtime and interpretation input.
- `backend/app/domain/astrology/interpretation/__init__.py` - expose canonical internal symbols only.
- `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py` - cover contract shape.
- `backend/tests/architecture/test_ai_narrative_input_boundary.py` - guard calculation, interpretation and narration boundaries.
- `backend/tests/architecture/test_api_contract_neutrality.py` - prove internal contract is not public OpenAPI.
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/validation.md` - persist validation evidence.
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/contract-before.md` - persist baseline shape.
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/evidence/contract-after.md` - persist final shape.

Likely tests:

- `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`
- `backend/tests/architecture/test_ai_narrative_input_boundary.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public route or serializer is added.
- `backend/app/infra/db/**` - out of scope; no persistence model is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`
- VC2: `pytest -q backend/tests/architecture/test_ai_narrative_input_boundary.py`
- VC3: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC4: `python -c "from app.main import app; assert 'AI' not in str(app.openapi().get('components', {}).get('schemas', {}))"`
- VC5: `python -c "from app.main import app; assert all('ai_narrative' not in getattr(r, 'path', '') for r in app.routes)"`
- VC6: `rg -n "prompt|llm_output|final_narrative|rendered_text|provider_response" backend/app/domain/astrology/runtime backend/app/domain/astrology/interpretation`
- VC7: `rg -n "OpenAI|AIEngineAdapter|chat\\.completions|LLMGateway" backend/app/domain/astrology/interpretation`
- VC8: `ruff format .`
- VC9: `ruff check .`
- VC10: `pytest -q`

## Regression Risks

- Prompt text could regain authority over astrology facts if the builder accepts prompt-owned fields as source inputs.
- Structural facts and interpretive signals could merge into one untyped payload, making scoring and narration boundaries hard to review.
- The internal contract could drift into public API schemas without a product projection decision.
- Debug fields could leak final prose or provider responses instead of bounded trace metadata.
- Scoring policy could be embedded in the contract instead of staying as a future product decision.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep all new tests deterministic and bounded to the backend-domain surfaces listed in this story.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md`
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/00-story.md`
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/00-story.md`
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/00-story.md`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
- `backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_contracts.py`
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`
