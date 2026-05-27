# Story CS-333 aligner-hash-evidence-audit-entree-llm-astrologique: Align Hash Evidence And LLM Astrology Input Audit
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`.
- Upstream story: CS-330 defines the `llm_astrology_input_v1` internal contract.
- Upstream story: CS-331 defines the mapper that feeds `llm_astrology_input_v1`.
- Upstream story: CS-332 wires `llm_astrology_input_v1` into the natal runtime.
- Audit source: CS-259 defines `narrative_answer_audit_v1` and requires `projection_hash` plus `llm_input_hash`.
- Evidence source: CS-260 defines `evidence_refs` as validated, hashed source references.
- Projection source: CS-264 defines stable `projection_hash` semantics.
- Transition source: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: the current audit hash can prove runtime identity without proving every prompt-influencing astrology input block.
- Source-alignment evidence: PASS; ACs preserve hash stability, invalidation, evidence coherence and prompt/runtime/audit role separation.

## Objective

Align `projection_hash`, `llm_input_hash`, `evidence_refs` and narrative audit data around `llm_astrology_input_v1`.

The backend must prove which astrology facts, interpretive signals, limits, evidence and shaping data influenced the LLM prompt.

## Target State

- `llm_astrology_input_v1` has one stable canonical hash input used to compute `llm_input_hash`.
- `llm_input_hash` changes when a prompt-visible block changes.
- `llm_input_hash` stays unchanged when a runtime-only value outside the prompt input changes.
- `projection_hash` remains the stable hash of the persisted projection or factual payload, not the full LLM prompt input identity.
- `evidence_refs` in the LLM input reference authorized hashed sources that match exposed facts or signals.
- `narrative_answer_audit_v1` records both `projection_hash` and `llm_input_hash` with coherent `evidence_refs`.
- Tests distinguish validation-only, runtime-only, audit-only and prompt-visible data roles.
- No prompt wording, provider policy, frontend, public route, DB schema, migration, auth, i18n, style or build tooling is changed.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-333`.
- Evidence 3: `_condamad/stories/CS-330-llm-astrology-input-v1-contract/00-story.md` - upstream contract story read.
- Evidence 4: `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/00-story.md` - upstream mapper story read.
- Evidence 5: `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/00-story.md` - upstream runtime story read.
- Evidence 6: `backend/app/domain/astrology/projections/projection_hash.py` - canonical hash helper found.
- Evidence 7: `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` - canonical evidence validation owner found.
- Evidence 8: targeted `rg` found current `llm_input_hash`, `projection_hash` and `evidence_refs` use in natal persistence and audit tests.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Source-alignment evidence: PASS; every named brief primitive is in scope or listed as a non-goal.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend hash semantics for `llm_astrology_input_v1`.
  - Relationship between `projection_hash` and `llm_input_hash`.
  - Coherence checks between prompt-visible facts, signals and `evidence_refs`.
  - Narrative audit payload alignment for `projection_hash`, `llm_input_hash` and `evidence_refs`.
  - Tests for stable hash, prompt-visible invalidation and runtime-only non-invalidation.
  - Role classification for validation-only, runtime-only, audit-only and prompt-visible data.
- Out of scope:
  - Frontend UI, public API route, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Prompt prose changes, provider policy, retry policy, model selection and real LLM network calls.
  - Physical retirement of `chart_json`, `natal_data` or historical public projection fields.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI response model or generated API client.
  - No database table, migration, repository schema change or persistence backfill.
  - No prompt wording rewrite, provider integration or LLM call.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend-domain hash and audit alignment contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Update only hash identity, evidence validation linkage and audit alignment for `llm_astrology_input_v1`.
  - Reuse `compute_projection_hash`, evidence validation owners and CS-330 to CS-332 contract owners.
  - Keep `projection_hash` scoped to projection or factual payload identity.
  - Keep `llm_input_hash` scoped to prompt-visible LLM input blocks and their source references.
  - Keep runtime-only, validation-only and audit-only data outside the LLM input hash material.
  - Keep public routes, OpenAPI exposure, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: `llm_astrology_input_v1` cannot expose a canonical prompt-visible hash material without changing prompt ownership.
- Additional validation rules:
  - The canonical hash material must be deterministic and serializable through the existing stable hash helper.
  - The hash material must include every prompt-visible fact, signal, limit, evidence reference and shaping value.
  - The hash material must exclude runtime-only request metadata that does not influence the prompt.
  - The hash material must exclude audit-only provider response and persisted answer fields.
  - `projection_hash` and `llm_input_hash` must be documented as separate identities.
  - Each `evidence_ref` carried by the LLM input must match an authorized hashed source.
  - Tests must prove a prompt-visible signal change invalidates `llm_input_hash`.
  - Tests must prove a runtime-only value change preserves `llm_input_hash`.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` evidence must prove no public API exposure was added.
  - An AST guard or targeted `rg` scan must prove no parallel hash implementation bypasses the canonical owner.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Hash behavior, evidence validation, audit payloads, `app.routes`, `app.openapi()` and `TestClient` prove runtime boundary. |
| Baseline Snapshot | yes | Before and after artifacts prove hash identity, evidence coherence and public surface neutrality. |
| Ownership Routing | yes | Projection hash, LLM input hash, evidence refs and audit payloads need distinct canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this hash and audit alignment story. |
| Contract Shape | yes | `llm_astrology_input_v1` must define exact hash material, role classes and evidence reference rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Prompt-visible data must not bypass `llm_input_hash` or evidence refs. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `llm_input_hash` is stable. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`. |
| AC2 | Prompt-visible signals alter the hash. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`. |
| AC3 | Runtime-only changes preserve `llm_input_hash`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`. |
| AC4 | Hash identities stay distinct. | Evidence profile: ast_architecture_guard; `python` AST guard checks documented owners. |
| AC5 | `evidence_refs` match exposed sources. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`. |
| AC6 | Invalid evidence refs are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`. |
| AC7 | Audit payload stores both hashes coherently. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`. |
| AC8 | Data role classes are tested. | Evidence profile: json_contract_shape; `pytest` covers prompt-visible, runtime-only, validation-only and audit-only roles. |
| AC9 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `TestClient` smoke. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-333 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-330, CS-331, CS-332, CS-259, CS-260, CS-264 and the transition report before editing. (AC: AC4, AC8)
- [ ] Task 2: Define canonical hash material for `llm_astrology_input_v1`. (AC: AC1, AC2, AC3)
- [ ] Task 3: Compute or expose `llm_input_hash` through the canonical LLM input owner. (AC: AC1, AC2, AC3)
- [ ] Task 4: Document the boundary between `projection_hash` and `llm_input_hash` in code or existing technical docs. (AC: AC4)
- [ ] Task 5: Link `evidence_refs` to prompt-visible facts and signals through authorized hashed sources. (AC: AC5)
- [ ] Task 6: Reuse `evidence_refs_validation.py` for rejected or incoherent refs. (AC: AC6)
- [ ] Task 7: Align narrative audit construction so both hashes and validated evidence refs describe the same LLM input. (AC: AC7)
- [ ] Task 8: Add tests for prompt-visible, runtime-only, validation-only and audit-only data role classes. (AC: AC8)
- [ ] Task 9: Add loaded-app and targeted scan guards for public API neutrality. (AC: AC9)
- [ ] Task 10: Persist hash, evidence, audit and validation artifacts under the CS-333 evidence folder. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md` - source brief.
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - upstream contract brief.
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md` - upstream mapper brief.
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md` - upstream runtime brief.
- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md` - audit contract brief.
- `_story_briefs/cs-260-add-evidence-refs-contract-and-validation.md` - evidence refs contract brief.
- `_story_briefs/cs-264-implement-projection-persistence-and-projection-hash.md` - projection hash brief.
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md` - transition report.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - expected canonical contract or mapper owner from CS-330 and CS-331.
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` - evidence refs validation owner.
- `backend/app/domain/astrology/projections/projection_hash.py` - deterministic hash helper owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - current narrative audit hash construction.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - evidence-based rejection workflow.
- `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py` - audit persistence repository.
- `backend/app/infra/db/models/user_natal_interpretation.py` - persisted audit columns.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` for canonical LLM input and hash material.
  - `backend/app/domain/astrology/projections/projection_hash.py` for deterministic hash serialization.
  - `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` for evidence reference validation.
  - `backend/app/services/llm_generation/natal/interpretation_service.py` for narrative audit hash application.
  - `app.routes`, `app.openapi()`, `TestClient`, AST guard and targeted `rg` scans for public API neutrality.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`.
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`.
  - `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`.
  - Targeted scans over LLM input, evidence validation, projection hash and natal audit paths.
- Static scans alone are not sufficient because:
  - hash determinism, invalidation behavior and audit persistence must be proven from runtime tests.

## Contract Shape

- Contract type:
  - Backend-domain hash, evidence and narrative audit alignment for `llm_astrology_input_v1`.
- Fields:
  - `llm_input_version`: exact version identifier for the LLM input hash contract.
  - `llm_input_hash`: stable SHA-256 of canonical prompt-visible `llm_astrology_input_v1` hash material.
  - `projection_hash`: stable SHA-256 of projection or factual payload identity.
  - `evidence_refs`: compact references to authorized hashed sources for prompt-visible facts and signals.
  - `data_role`: classification value for prompt-visible, runtime-only, validation-only or audit-only material.
  - `hash_material`: canonical serialized subset that affects `llm_input_hash`.
  - `excluded_hash_material`: named values excluded from `llm_input_hash` with a role reason.
  - `audit_link`: narrative audit payload fields connecting answer, projection, LLM input and evidence refs.
- Required fields:
  - `llm_input_version`
  - `llm_input_hash`
  - `projection_hash`
  - `evidence_refs`
  - `hash_material`
  - `excluded_hash_material`
  - `audit_link`
- Optional fields:
  - none for the hash contract; empty collections encode unavailable source data.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - emitted names must stay `llm_input_hash`, `projection_hash`, `evidence_refs` and `llm_astrology_input_v1`.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose this internal audit alignment from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
  - `_condamad/stories/CS-330-llm-astrology-input-v1-contract/00-story.md`
  - `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/00-story.md`
  - `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/00-story.md`
  - targeted search output showing current `llm_input_hash`, `projection_hash` and `evidence_refs` wiring.
- Comparison after implementation:
  - `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/hash-cases.json`
  - `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/evidence-coherence.txt`
  - `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/audit-payload.json`
  - `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/validation.txt`
- Expected invariant:
  - The only intended application delta is canonical LLM input hash identity, evidence coherence and narrative audit alignment.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| LLM input hash material | `llm_astrology_input_v1` domain owner | prompt template or provider code |
| Projection hash identity | `backend/app/domain/astrology/projections/projection_hash.py` | ad hoc local hashing |
| Evidence ref validation | `evidence_refs_validation.py` | client payload or decorative string list |
| Narrative audit assignment | natal interpretation audit workflow | provider response construction |
| Data role classification | LLM input domain contract | hidden request metadata |
| Public API neutrality evidence | loaded app checks and targeted tests | new API route or generated client |
| Evidence artifacts | `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-330 `llm_astrology_input_v1` contract shape.
- Reuse the CS-331 mapper output for prompt-visible facts, signals, limits, evidence and shaping.
- Reuse the CS-332 natal runtime key for prompt-visible transport.
- Reuse `compute_projection_hash` and canonical JSON behavior from `projection_hash.py`.
- Reuse `evidence_refs_validation.py` and existing audit workflow helpers for evidence coherence.
- Keep one canonical `llm_input_hash` material builder; do not create a parallel prompt input hash helper.
- Do not add external packages, public routes, frontend helpers, DB models, migrations, LLM providers or generated clients.

## No Legacy / Forbidden Paths

- No legacy prompt input path may own `llm_input_hash`.
- No compatibility route path may expose this internal audit alignment.
- No fallback branch may compute `llm_input_hash` from request id, provider output or persisted answer only.
- Do not create aliases, shims, wrappers or parallel schemas for the same hash material.
- Do not use `evidence_catalog` alone as proof that prompt grounding is covered.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**` schema and migration surfaces
  - `backend/migrations/**`
  - generated OpenAPI clients
  - provider implementations as hash owners

## Reintroduction Guard

- Guard target:
  - prompt-visible facts, signals, limits, evidence and shaping cannot bypass `llm_input_hash`;
  - runtime-only request metadata cannot invalidate `llm_input_hash`;
  - audit-only provider output cannot become LLM input hash material;
  - `projection_hash` cannot be treated as a substitute for full LLM input identity;
  - `evidence_refs` cannot remain decorative or unbound to hashed authorized sources;
  - public API routes and OpenAPI schemas cannot expose this internal alignment.
- Guard mechanism:
  - focused unit tests for hash stability, prompt-visible invalidation and runtime-only non-invalidation;
  - evidence refs tests for authorized source matching and rejected mismatches;
  - integration test for narrative audit payload coherence;
  - `app.routes`, `app.openapi()` and `TestClient` neutrality checks;
  - AST guard or targeted `rg` scan for duplicate hash helpers and prompt-provider bypasses.
- Guard owner:
  - final `llm_astrology_input_v1` hash material owner;
  - `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`;
  - `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`;
  - `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`;
  - `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/validation.txt`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`;
  - `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`;
  - `python -c "from app.main import app; assert 'llm_input_hash' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('llm-input' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `rg -n "llm_input_hash|projection_hash|evidence_refs|llm_astrology_input_v1|prompt-visible|runtime-only|validation-only|audit-only" app tests docs`.

## Regression Guardrails

Scope vector:

- backend-domain hash and audit update: yes;
- backend interpretation owners: yes;
- backend LLM natal service: yes;
- backend unit and integration tests: yes;
- prompt-generation validation paths: yes;
- public API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend ownership stays inside canonical app paths. | AST guard; targeted `pytest`; loaded app checks. |
| RG-022 | Backend prompt-generation validation paths must stay collected. | `pytest`; validation transcript. |
| Registry gap | No exact `llm_input_hash` guardrail exists in scoped resolver output. | Story-local `rg` and audit tests. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story aligns backend LLM input auditability.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Hash cases | `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/hash-cases.json` | Keep stability and invalidation examples. |
| Evidence coherence | `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/evidence-coherence.txt` | Prove source matching. |
| Audit payload | `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/audit-payload.json` | Keep narrative audit proof. |
| Validation output | `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/validation.txt` | Keep lint and test transcript. |
| Review output | `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this backend hash and audit story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - canonical hash material and evidence linkage.
- `backend/app/domain/astrology/projections/projection_hash.py` - reuse or document canonical serialization boundary.
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` - reuse validation for LLM input refs.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - align narrative audit hash inputs.
- `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/hash-cases.json` - hash proof.
- `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/evidence-coherence.txt` - evidence proof.
- `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/audit-payload.json` - audit proof.
- `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/validation.txt` - validation transcript.

Likely tests:

- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` - hash stability and invalidation.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` - evidence refs coherence.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - narrative audit payload coherence.
- `backend/tests/architecture/test_llm_astrology_input_audit_boundary.py` - owner and public exposure guard.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public or internal API route is touched.
- `backend/app/infra/db/**` schema and migration surfaces - out of scope; no persistence schema change is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- provider implementation files - out of scope; no provider policy or network call behavior is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_hash.py`
- VC6: `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`
- VC7: `pytest -q tests/integration/llm/test_natal_llm_astrology_input_audit.py`
- VC8: `pytest -q tests/architecture/test_llm_astrology_input_audit_boundary.py`
- VC9: `pytest -q tests --tb=short`
- VC10: `python -c "from app.main import app; assert 'llm_input_hash' not in str(app.openapi())"`
- VC11: `python -c "from app.main import app; assert all('llm-input' not in getattr(r, 'path', '') for r in app.routes)"`
- VC12: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/evidence/validation.txt').exists()"`
- VC13: `rg -n "llm_input_hash|projection_hash|evidence_refs|llm_astrology_input_v1|prompt-visible|runtime-only|validation-only|audit-only" app tests docs`

Before VC3 through VC13, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- `llm_input_hash` could remain tied to request identity instead of prompt-influencing astrology input.
- Prompt-visible evidence refs could point to decorative strings rather than hashed authorized sources.
- Runtime-only metadata could cause noisy hash churn.
- Audit-only provider output could be folded into the input hash after generation.
- `projection_hash` could be mistaken for full prompt input identity.
- Validation tests could miss the difference between validation-only, runtime-only, audit-only and prompt-visible data.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Reuse CS-330, CS-331 and CS-332 owners before creating adjacent helpers.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`
- `_story_briefs/cs-260-add-evidence-refs-contract-and-validation.md`
- `_story_briefs/cs-264-implement-projection-persistence-and-projection-hash.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`
- `backend/app/domain/astrology/projections/projection_hash.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
- `_condamad/stories/regression-guardrails.md`
