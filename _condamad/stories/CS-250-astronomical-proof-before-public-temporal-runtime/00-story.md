# Story CS-250 astronomical-proof-before-public-temporal-runtime: Harden Astronomical Proof Before Public Temporal Runtime
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-250-astronomical-proof-before-public-temporal-runtime.md`.
- Related context: CS-241 found incomplete astronomical proof and a callable simplified path.
- Related gate: CS-245 requires this proof before CS-253 opens a public temporal technique.
- Problem statement: production astronomy must be proven before any public temporal runtime surface is authorized.
- Source-alignment evidence: PASS; the story preserves production mode proof, golden cases, tolerance policy, ephemeris trace, and CS-253 gating.

## Objective

Harden the backend astrology calculation proof so public temporal runtime work cannot rely on an unqualified simplified mode.

The implementation must prove the production `swisseph` path, persist golden-case evidence for sensitive charts, document tolerances, and keep CS-253 blocked
until the proof is closed or a documented product risk acceptance limits the surface to non-public experimentation.

## Target State

- Production astrology calculation proof is anchored to the runtime `swisseph` path or an explicitly authorized equivalent.
- A minimal golden suite covers sensitive temporal and house-system cases from CS-241 or this story.
- Ephemeris version, path hash, or equivalent configuration trace is captured in test evidence.
- Tolerances are explicit, justified, and reused by tests.
- Public temporal work cannot be carried by the simplified engine.
- CS-253 remains blocked unless the proof artifacts pass or risk acceptance records a bounded non-public scope.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-250-astronomical-proof-before-public-temporal-runtime.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to convert `CS-250` from brief-ready to ready-to-dev.
- Evidence 3: `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md` - audit story documents required sensitive golden charts.
- Evidence 4: `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md` - architecture gate confirms astronomy proof before temporal rollout.
- Evidence 5: `backend/app/domain/astrology/natal_calculation.py` - scoped read found `engine="simplified"` and `engine == "swisseph"` branches.
- Evidence 6: `backend/app/domain/astrology/ephemeris_provider.py` - scoped read found SwissEph calculation, ayanamsa, topocentric, and reset behavior.
- Evidence 7: `backend/pyproject.toml` - scoped scan found `pyswisseph>=2.10.0` as an existing dependency.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for backend runtime proof scope.

## Domain Boundary

- Domain: backend-astrology-runtime-proof
- In scope:
  - Backend astronomy proof for natal calculation runtime and temporal-technique readiness gate.
  - Identification of simplified calculation paths still reachable from backend astrology runtime.
  - Production-mode guards around `swisseph` or an authorized equivalent.
  - Golden tests for sensitive Paris, DST, high-latitude, Lahiri, topocentric, whole sign, and Placidus edge cases.
  - Ephemeris version, hash, path, or loaded configuration trace in deterministic evidence.
  - Tolerance policy for longitude, houses, ayanamsa, and sensitive temporal cases.
  - CS-253 blocker evidence or bounded non-public risk acceptance evidence.
- Out of scope:
  - Frontend UI, public API creation, database schema, auth, i18n, styling, build tooling, migrations, and business narration.
  - Implementing transits, synastry, returns, progressions, profections, or another public temporal technique.
  - Correcting astrology doctrine outside astronomical precision and runtime qualification.
- Explicit non-goals:
  - No frontend route, screen, generated client, CSS, or browser validation.
  - No new public endpoint or payload shape.
  - No hidden public use of a simplified calculation mode.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend astronomical runtime proof contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add proof, tests, guards, and documentation only for backend astronomy runtime qualification.
  - Keep current product behavior unchanged outside the qualification gate.
  - Block public temporal runtime work until proof closure or bounded non-public risk acceptance.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product wants CS-253 opened without completed astronomical proof.
- Additional validation rules:
  - Tests must prove the loaded production astronomy mode, not only imported modules.
  - Golden cases must include the sensitive cases named by CS-241 or justified replacements.
  - Test evidence must capture ephemeris version, path hash, loaded config, or an explicit reproducibility blocker.
  - Tolerances must be stored in one canonical test or docs surface and referenced by all new golden tests.
  - Public temporal surfaces must fail validation while the simplified mode remains the only qualifying proof.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, loaded config, test fixtures, and `pytest` must prove actual backend astronomy behavior. |
| Baseline Snapshot | yes | Before and after proof artifacts must show the qualification delta without broad runtime drift. |
| Ownership Routing | yes | Runtime guards, golden tests, and evidence docs need canonical backend ownership. |
| Allowlist Exception | no | No broad allowlist handling is authorized for public temporal runtime qualification. |
| Contract Shape | yes | The proof has exact required cases, metadata fields, tolerance fields, and gate states. |
| Batch Migration | no | No batch migration or cross-domain conversion is in scope. |
| Reintroduction Guard | yes | Simplified public temporal use and unqualified aliases must stay blocked. |
| Persistent Evidence | yes | Review must retain proof artifacts, validation transcript, and risk-gate evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Production astronomy mode is proven. | Evidence profile: ast_architecture_guard; targeted proof pytest in VC5. |
| AC2 | Simplified public temporal use is blocked. | Evidence profile: no_legacy_contract; `AST guard`; targeted `pytest`. |
| AC3 | Sensitive golden cases pass. | Evidence profile: json_contract_shape; targeted golden pytest in VC6. |
| AC4 | Tolerance policy is canonical. | Evidence profile: baseline_before_after_diff; `rg` checks tolerance owner; targeted `pytest`. |
| AC5 | Ephemeris trace is persisted. | Evidence profile: baseline_before_after_diff; targeted proof pytest in VC5. |
| AC6 | CS-253 gate stays closed. | Evidence profile: reintroduction_guard; `rg` checks CS-253 gate evidence; targeted `pytest`. |
| AC7 | Story evidence artifacts exist. | Evidence profile: baseline_before_after_diff; `python` checks story evidence directory. |

## Implementation Tasks

- [ ] Task 1: Identify all backend simplified astronomy paths reachable from natal or temporal runtime orchestration. (AC: AC2)
- [ ] Task 2: Add a production-mode guard proving `swisseph` or an authorized equivalent before public temporal runtime use. (AC: AC1, AC2)
- [ ] Task 3: Create minimal sensitive golden cases for Paris, DST, high latitude, Lahiri, topocentric, whole sign, and Placidus. (AC: AC3)
- [ ] Task 4: Centralize tolerance constants and document the precision reason for every tolerance band. (AC: AC4)
- [ ] Task 5: Capture ephemeris version, path hash, loaded config, or reproducibility blocker inside test evidence. (AC: AC5)
- [ ] Task 6: Add the CS-253 gate proof so public temporal technique work remains blocked without proof closure. (AC: AC6)
- [ ] Task 7: Persist validation output and proof snapshots under the story evidence folder. (AC: AC7)

## Files to Inspect First

- `_story_briefs/cs-250-astronomical-proof-before-public-temporal-runtime.md` - source contract.
- `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md` - sensitive astronomical proof requirements.
- `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md` - temporal runtime gate context.
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/00-story.md` - gate target once generated or implemented.
- `backend/app/domain/astrology/natal_calculation.py` - runtime engine selection and calculation orchestration.
- `backend/app/domain/astrology/ephemeris_provider.py` - SwissEph position provider and metadata behavior.
- `backend/app/domain/astrology/houses_provider.py` - house-system provider and high-latitude behavior.
- `backend/app/core/ephemeris.py` - ephemeris bootstrap, path, hash, and required-file configuration.
- `backend/tests/unit/domain/astrology/**` - existing deterministic astrology proof tests.
- `backend/tests/architecture/**` - existing architecture guards and public runtime boundary checks.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, loaded config, ephemeris bootstrap state, generated proof manifest, and targeted `pytest` golden tests.
- Secondary evidence:
  - Targeted `rg` scans for simplified engine reachability, `swisseph` usage, ephemeris metadata, and CS-253 gate markers.
- Static scans alone are not sufficient for this story because:
  - Runtime qualification must prove actual mode selection, loaded ephemeris configuration, and deterministic chart outputs.

## Contract Shape

- Contract type:
  - Backend astronomy runtime proof and temporal gate contract.
- Fields:
  - `mode`: production calculation mode such as `swisseph`.
  - `authorized_public_temporal`: boolean gate value.
  - `golden_case_id`: stable identifier for each sensitive chart.
  - `input_profile`: date, timezone, latitude, longitude, house system, zodiac, frame, and altitude.
  - `expected_reference`: expected longitudes, houses, ayanamsa, or documented reference source.
  - `tolerance`: named tolerance from the canonical policy.
  - `ephemeris_trace`: version, path hash, loaded config, or reproducibility blocker.
  - `cs253_gate_state`: `blocked`, `proof-closed`, or `risk-accepted-non-public`.
- Required fields:
  - `mode`
  - `authorized_public_temporal`
  - `golden_case_id`
  - `input_profile`
  - `expected_reference`
  - `tolerance`
  - `ephemeris_trace`
  - `cs253_gate_state`
- Optional fields:
  - none
- Status codes:
  - none; this is not an API route.
- Serialization names:
  - Internal proof artifacts keep snake_case field names.
- Frontend type impact:
  - none.
- Generated contract impact:
  - Generated proof manifest or evidence transcript must preserve the required fields.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-250-astronomical-proof-before-public-temporal-runtime.md`
  - `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md`
  - `backend/app/domain/astrology/natal_calculation.py`
  - `backend/app/domain/astrology/ephemeris_provider.py`
  - `backend/app/core/ephemeris.py`
- Comparison after implementation:
  - `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/validation.txt`
  - `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/astronomical-proof.json`
- Expected invariant:
  - The only intended behavior delta is public temporal qualification becoming impossible without production astronomical proof.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Production astronomy guard | `backend/app/domain/astrology/` | `frontend/src/**` |
| Ephemeris configuration proof | `backend/app/core/ephemeris.py` or existing config owner | `backend/app/api/**` |
| Golden astronomy tests | `backend/tests/unit/domain/astrology/` | `backend/tests/evaluation/**` |
| Public temporal gate guard | `backend/tests/architecture/` | `frontend/src/**` |
| Story proof artifacts | `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/` | `backend/app/**` |

## Mandatory Reuse / DRY Constraints

- Reuse existing `swisseph`, ephemeris bootstrap, natal calculation, and house-provider surfaces.
- Reuse existing astrology test fixtures before creating new fixture families.
- Use one canonical tolerance owner for all new golden assertions.
- Use one canonical CS-253 gate marker across tests, evidence, and story references.
- Do not duplicate large expected chart payloads across tests; share fixtures or data builders.
- Do not add external packages or parallel ephemeris wrappers.

## No Legacy / Forbidden Paths

- No legacy public temporal path may rely on simplified astronomy.
- No compatibility route, adapter, or wrapper may qualify simplified astronomy for public temporal use.
- No fallback branch may silently convert failed `swisseph` proof into simplified public temporal output.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/migrations/**`
  - `docs/db_seeder/**`
  - `node_modules/**`
  - `.venv/**`

## Reintroduction Guard

- Guard scope:
  - Public temporal runtime surfaces must stay blocked unless production astronomy proof passes.
  - Simplified mode may remain for bounded internal or test surfaces, but it cannot qualify public temporal behavior.
- Deterministic guard:
  - `pytest -q backend/tests/architecture/test_temporal_public_runtime_gate.py`
  - `rg -n "engine=.simplified.|engine == .simplified.|simplified" backend/app/domain/astrology backend/tests/architecture`
- Forbidden alternate route:
  - Do not satisfy the gate by adding a public API, frontend-only block, broad allowlist, compatibility shim, or silent fallback.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| Registry gap | No exact public temporal astronomy proof guardrail was present in scoped resolver output. | Scoped search reviewed. |

Non-applicable examples retained to prevent scope drift:

- RG-002 API router organization is out of scope because no `backend/app/api/**` route changes are planned.
- RG-022 prompt-generation validation paths are out of scope because this story changes backend astrology proof tests.
- RG-047 frontend inline styles are out of scope because no frontend files are touched.
- RG-052 frontend CSS namespace migration is out of scope because no styling files are touched.
- RG-041 entitlement documentation is out of scope because astronomy proof, not billing entitlement, is changed.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/validation.txt` | Keep lint and test transcript. |
| Proof manifest | `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/astronomical-proof.json` | Keep mode and case proof. |
| Open gate note | `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/cs-253-gate.md` | Keep gate state evidence. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this backend astronomy proof story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/natal_calculation.py` - enforce qualified production astronomy mode for public temporal readiness.
- `backend/app/domain/astrology/ephemeris_provider.py` - expose or preserve deterministic ephemeris trace evidence.
- `backend/app/core/ephemeris.py` - prove configured ephemeris path, hash, version, and required files.
- `backend/tests/unit/domain/astrology/test_astronomical_proof.py` - prove production mode and ephemeris trace.
- `backend/tests/unit/domain/astrology/test_astronomical_golden_cases.py` - cover sensitive golden cases.
- `backend/tests/architecture/test_temporal_public_runtime_gate.py` - block public temporal runtime without proof closure.
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/validation.txt` - persist validation transcript.
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/astronomical-proof.json` - persist proof manifest.

Likely tests:

- `backend/tests/unit/domain/astrology/test_astronomical_proof.py`
- `backend/tests/unit/domain/astrology/test_astronomical_golden_cases.py`
- `backend/tests/architecture/test_temporal_public_runtime_gate.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public API route is added.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `docs/db_seeder/**` - out of scope; no seed artifact is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `python -c "from pathlib import Path; assert Path('backend').exists()"`
- VC3: `ruff format backend`
- VC4: `ruff check backend`
- VC5: `pytest -q backend/tests/unit/domain/astrology/test_astronomical_proof.py`
- VC6: `pytest -q backend/tests/unit/domain/astrology/test_astronomical_golden_cases.py`
- VC7: `pytest -q backend/tests/architecture/test_temporal_public_runtime_gate.py`
- VC8: `pytest -q`
- VC9: `rg -n "engine=.simplified.|engine == .simplified.|simplified" backend/app/domain/astrology backend/tests/architecture`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/validation.txt').exists()"`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/evidence/astronomical-proof.json').exists()"`

Before VC3 through VC11, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Tests could prove imports while missing active runtime mode selection.
- Golden cases could encode current output rather than source-backed astronomical reference values.
- Tolerances could become wide enough to hide meaningful precision drift.
- Ephemeris trace could omit version or hash evidence, making proof non-reproducible on another machine.
- CS-253 could proceed through documentation drift without a deterministic gate.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all Python commands inside the activated venv.
- Treat `swisseph` proof as valid only when loaded runtime behavior and deterministic outputs are covered.
- Treat risk acceptance as valid only for non-public experimentation with exact scope, forbidden surface, known drift, and closure date or story.
- Keep frontend, public API, DB, migration, auth, i18n, styling, build tooling, and doctrine expansion out of scope.

## References

- `_story_briefs/cs-250-astronomical-proof-before-public-temporal-runtime.md`
- `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md`
- `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md`
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/00-story.md`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/ephemeris_provider.py`
- `backend/app/core/ephemeris.py`
- `_condamad/stories/regression-guardrails.md`
