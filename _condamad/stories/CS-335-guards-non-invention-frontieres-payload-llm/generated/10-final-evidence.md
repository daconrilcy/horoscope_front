# Final Evidence — CS-335-guards-non-invention-frontieres-payload-llm

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-335-guards-non-invention-frontieres-payload-llm
- Source story: `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/00-story.md`
- Capsule path: `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story status row verified: `CS-335`, target `Path`, and source brief match.
- Initial `git status --short`: pre-existing `_condamad/run-state.json` untracked; no tracked story files modified before implementation.
- AGENTS.md considered: repository root `AGENTS.md`.
- Capsule generated/repaired: yes, missing generated files were created with `condamad_prepare.py`; `condamad_validate.py` passed.

## Capsule validation

- Required generated files present: yes.
- `condamad_validate.py` after capsule repair: PASS.
- `condamad_validate.py` after final evidence completion: PASS.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Gateway prompt projection plus orchestration and AST guards. | `tests\llm_orchestration\test_llm_astrology_input_boundaries.py` and payload AST guard passed. | PASS |
| AC2 | Rendered prompt payload contains `facts`, `signals`, `limits`, `evidence`, `shaping`, `provenance`. | `payload-boundary-after.json` and orchestration tests. | PASS |
| AC3 | Missing-data profile limits are decoded from the gateway-rendered payload. | `test_gateway_payload_makes_missing_data_limits_prompt_visible`. | PASS |
| AC4 | Raw runtime and legacy metadata are not serialized into prompt-visible material. | Boundary tests and `payload-boundary-scan.txt`. | PASS |
| AC5 | `chart_json`/`natal_data` are not selected as prompt owners when rich input exists. | Legacy-owner negative test plus existing runtime suppression tests. | PASS |
| AC6 | Facts/signals/shaping remain disjoint with one canonical contract owner. | `tests\unit\domain\astrology\test_llm_astrology_input_v1.py` passed. | PASS |
| AC7 | Handoff validation uses a local mocked client, not an external provider. | `test_gateway_provider_handoff_uses_local_double_and_prompt_boundary`. | PASS |
| AC8 | Evidence artifacts persisted under story evidence directory. | Python existence check passed. | PASS |

## Files changed

- `backend/app/domain/llm/runtime/gateway.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/generated/**`
- `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- Added orchestration boundary tests for gateway-rendered `llm_astrology_input_v1`.
- Added architecture guard preventing full rich-contract serialization in prompt material.
- Reused existing contract tests for facts/signals/shaping non-duplication.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-335-guards-non-invention-frontieres-payload-llm` | repo root after venv activation | PASS |
| `python -B -m ruff format app\domain\llm\runtime\gateway.py tests\llm_orchestration\test_llm_astrology_input_boundaries.py tests\architecture\test_llm_astrology_input_payload_boundaries.py` | `backend` after venv activation | PASS |
| `python -B -m ruff check .` | `backend` after venv activation | PASS |
| `python -B -m pytest -q tests\llm_orchestration\test_llm_astrology_input_boundaries.py --tb=short` | `backend` after venv activation | PASS, 4 passed |
| `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_v1.py --tb=short` | `backend` after venv activation | PASS, 9 passed |
| `python -B -m pytest -q tests\architecture\test_llm_astrology_input_payload_boundaries.py --tb=short` | `backend` after venv activation | PASS, 3 passed |
| `python -B -m pytest -q tests\architecture\test_llm_astrology_input_boundary.py tests\architecture\test_llm_astrology_input_runtime_boundary.py --tb=short` | `backend` after venv activation | PASS, 7 passed |
| `python -B -m pytest -q tests --tb=short` | `backend` after venv activation | PASS, 1202 passed, 218 deselected |
| `python -B -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"` | `backend` after venv activation | PASS |
| `rg -n "prompt-visible|runtime-only|validation-only|audit-only|llm_astrology_input_v1|chart_json|natal_data|ChartObjectRuntimeData|CalculationGraph" app tests` | `backend` | PASS, expected scoped matches |
| `git diff --check -- <story paths>` | repo root | PASS with line-ending warning only |

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

- One prompt-owner path remains: `llm_astrology_input_v1` is projected by the gateway when present.
- `chart_json` and `natal_data` remain runtime/validation carriers and are not serialized as prompt owners for migrated natal requests.
- No frontend, API router, DB migration, provider policy or prompt editorial copy was changed.
- No new dependency, shim, alias or fallback path was added.

## Diff review

- `git diff --stat` tracked code delta: `backend/app/domain/llm/runtime/gateway.py` changed; new tests/evidence are untracked until added by reviewer.
- `git diff --check`: PASS, with Git warning that LF may be converted to CRLF on next touch.

## Final worktree status

- Modified tracked: `backend/app/domain/llm/runtime/gateway.py`.
- Untracked story scope: new boundary tests, generated capsule files and evidence artifacts.
- Pre-existing unrelated untracked: `_condamad/run-state.json`.

## Remaining risks

- The `before` snapshot is reconstructed from pre-change source inspection and current contract shape because the required evidence file did not exist before implementation.

## Suggested reviewer focus

- Verify the gateway prompt projection intentionally excludes `exclusions` and `data_roles` while preserving `provenance`.

## Feedback loop routing

- No propagation: the only execution issue was a local command working-directory mistake, corrected and recorded in validation evidence; no reusable repository guardrail change was needed.
