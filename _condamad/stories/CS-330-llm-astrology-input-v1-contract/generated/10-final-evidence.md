# Final Evidence — CS-330-llm-astrology-input-v1-contract

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-330-llm-astrology-input-v1-contract
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-330-llm-astrology-input-v1-contract`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-330-llm-astrology-input-v1-contract/00-story.md`
- Initial `git status --short`: PASS, pre-existing untracked `_condamad/run-state.json`
- Pre-existing dirty files: `_condamad/run-state.json`
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing generated files prepared with explicit `--story-key`

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | |
| `generated/01-execution-brief.md` | yes | yes | PASS | |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | |
| `generated/04-target-files.md` | yes | yes | PASS | |
| `generated/06-validation-plan.md` | yes | yes | PASS | |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | |
| `generated/10-final-evidence.md` | yes | yes | PASS | |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | `evidence/validation.txt` targeted pytest PASS | PASS | Internal contract owner added. |
| AC2 | Payload emits seven required blocks plus id/version | Unit shape test and `evidence/sample-payload.json` | PASS | Blocks: facts, signals, limits, evidence, shaping, provenance, exclusions. |
| AC3 | Facts guarded by `STRUCTURED_FACTS_V1_PROJECTION_ID` | Unit rejection test and `evidence/architecture-guard.txt` | PASS | Wrong projection source raises `ValueError`. |
| AC4 | Signals guarded by `AINarrativeInputContract` | AST import assertion and source scan | PASS | Debug/provider payloads are not copied. |
| AC5 | B2C projection metadata limited to shaping | Unit assertion excludes `sections` from shaping | PASS | B2C is not a factual source. |
| AC6 | Raw carriers listed only under exclusions | Unit negative assertions and scan evidence | PASS | `chart_json` and `natal_data` absent from canonical facts. |
| AC7 | `llm_input_hash` via `compute_projection_hash` | Deterministic hash test PASS | PASS | Hash policy covers prompt-influencing blocks. |
| AC8 | Prompt wiring unchanged | Prompt/provider scan and no service diff | PASS | No `backend/app/services/llm_generation/**` edits. |
| AC9 | Public API surface unchanged | `evidence/public-surface-guard.txt` | PASS | OpenAPI, routes and `/health` smoke PASS. |
| AC10 | Evidence artifacts persisted | Evidence files present and capsule validation PASS | PASS | Required evidence folder populated. |

## Files changed

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- `_condamad/stories/CS-330-llm-astrology-input-v1-contract/evidence/*`
- `_condamad/stories/CS-330-llm-astrology-input-v1-contract/generated/*`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `ruff format app\domain\astrology\interpretation\llm_astrology_input_v1.py app\domain\astrology\runtime\astrology_doctrine_governance.py tests\unit\domain\astrology\test_llm_astrology_input_v1.py` | `backend` | PASS | 0 | Scoped formatting. |
| `ruff check app\domain\astrology\interpretation\llm_astrology_input_v1.py app\domain\astrology\runtime\astrology_doctrine_governance.py tests\unit\domain\astrology\test_llm_astrology_input_v1.py` | `backend` | PASS | 0 | Scoped lint. |
| `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_v1.py --tb=short` | `backend` | PASS | 0 | 6 tests passed. |
| `python -B -m pytest -q tests --tb=short` | `backend` | PASS | 0 | 1167 passed, 215 deselected. |
| OpenAPI/routes/TestClient guards | `backend` | PASS | 0 | See `evidence/public-surface-guard.txt`. |
| Architecture owner/source/prompt scans | `backend` | PASS | 0 | See `evidence/architecture-guard.txt`. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-330-llm-astrology-input-v1-contract` | repo root | PASS | 0 | Capsule structure valid. |

## Commands skipped or blocked

- none

## DRY / No Legacy evidence

- One canonical contract owner: `LLMAstrologyInputV1Builder` appears only in `llm_astrology_input_v1.py`.
- Facts source is guarded by `structured_facts_v1`; signals source is guarded by `AINarrativeInputContract`.
- `client_interpretation_projection_v1` is shaping metadata only; no public API route or OpenAPI schema exposes the internal contract.
- No compatibility shim, alias, fallback, prompt wiring, provider integration, frontend file, DB model or migration was added.

## Diff review

- `git diff --stat -- <story paths>`: reviewed; app delta is one new contract, one architecture governance classification and one test file.
- `git diff --check -- backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`: PASS.

## Final worktree status

- Story files modified/added plus pre-existing `_condamad/run-state.json` untracked.

## Remaining risks

- none known

## Suggested reviewer focus

- Verify the contract block boundaries: B2C projection remains shaping-only and raw carriers remain exclusions, not canonical sources.
