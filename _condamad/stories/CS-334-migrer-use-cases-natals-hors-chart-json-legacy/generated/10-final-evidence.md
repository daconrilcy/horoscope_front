# Final Evidence — CS-334-migrer-use-cases-natals-hors-chart-json-legacy

## Story status

- Validation outcome: pass
- Ready for review: yes
- Story key: CS-334-migrer-use-cases-natals-hors-chart-json-legacy
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy`
- Story registry status: `done`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source and brief alignment verified in `_condamad/stories/story-status.md`.
- Initial `git status --short`: dirty worktree already contained CS-334 files and generated capsule artifacts.
- AGENTS.md considered: repository root `AGENTS.md`.
- Capsule validation before implementation: `CONDAMAD validation: PASS`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status synchronized to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Capsule generated before implementation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC8 classified. |
| `generated/04-target-files.md` | yes | yes | PASS | Capsule generated before implementation. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Validation commands executed or classified. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | No-legacy checks recorded. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Final evidence completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Modern natal contracts require `llm_astrology_input_v1`. | Unit contract guard passes. | PASS | |
| AC2 | Modern natal input schemas require `llm_astrology_input_v1`. | After snapshot persisted and unit guard passes. | PASS | |
| AC3 | Modern natal placeholders and schema required keys reject `chart_json`; assembly nominal payload migrated. | Unit guard plus forbidden replacement scan pass. | PASS | |
| AC4 | Renderer tests inspect final prompt material with `llm_astrology_input_v1` and no old carrier. | Prompt renderer targeted suite passes. | PASS | |
| AC5 | Runtime transition carriers are named and bounded; modern validation payload ignores old carriers when modern key is present. | Runtime transition integration suite passes with `--long`. | PASS | |
| AC6 | No prompt editorial file changed; code delta limited to key migration support and tests. | Diff review and snapshots recorded. | PASS | |
| AC7 | `app.routes` and `app.openapi()` before/after are semantically identical. | App import/OpenAPI checks pass. | PASS | |
| AC8 | Evidence artifacts and validation summary are persisted under `evidence/`. | Capsule/evidence files present. | PASS | |

## Files changed

- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/tests/unit/test_natal_llm_use_case_input_contract.py`
- `backend/tests/llm_orchestration/test_prompt_renderer.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/integration/test_llm_runtime_suppression.py`
- `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/**`
- `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/generated/10-final-evidence.md`
- `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/generated/11-code-review.md`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- New unit contract guard: `tests/unit/test_natal_llm_use_case_input_contract.py`.
- Renderer coverage for final modern natal prompt material.
- Assembly resolution test payload migrated to the modern key.
- Runtime transition test proving old carriers stay bounded when modern input is present.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py .\_condamad\stories\CS-334-migrer-use-cases-natals-hors-chart-json-legacy` | repo root | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format <touched files>` | repo root | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/unit/test_natal_llm_use_case_input_contract.py --tb=short` | repo root | PASS, 5 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/llm_orchestration/test_prompt_renderer.py --tb=short` | repo root | PASS, 6 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/llm_orchestration/test_assembly_resolution.py --tb=short` | repo root | PASS, 15 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q --long tests/integration/test_llm_runtime_suppression.py --tb=short` | repo root | PASS, 8 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests --tb=short` | repo root | PASS, 1195 passed, 218 deselected |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"` | repo root | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"` | repo root | PASS |
| `rg -n "llm_astrology_input_v1\|chart_json\|natal_data\|input_schema\|placeholder\|legacy\|fallback" app tests` | `backend` | PASS, scan persisted/classified |
| `rg -n "chart_json_v2\|natal_data_v2\|\{\{\*\|shim\|compatibility wrapper\|fallback prompt branch" ...` | repo root | PASS: no matches, exit 1 expected |
| `git diff --check` | repo root | PASS, line-ending warnings only |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m uvicorn app.main:app --host 127.0.0.1 --port 8765` then `GET /docs` | repo root | PASS |

## Commands skipped or blocked

- Initial `python -B -m pytest -q tests/integration/test_llm_runtime_suppression.py --tb=short` without `--long` was deselected by `backend/conftest.py`; rerun with `--long` passed.

## DRY / No Legacy evidence

- One helper owns the migrated modern natal contract list: `list_modern_natal_use_case_contracts()`.
- No alias key, shim, `chart_json_v2`, `natal_data_v2`, compatibility wrapper or fallback prompt branch introduced.
- Residual `chart_json`/`natal_data` runtime handling is explicitly labeled as legacy transition.
- No public API route or OpenAPI surface changed.

## Diff review

- `git diff --stat` reviewed for story paths: 6 application/test files changed before evidence updates.
- `git diff --check`: PASS, with CRLF normalization warnings only.

## Final worktree status

- `git status --short` after evidence/status update shows only story-scoped modified/untracked files plus pre-existing `_condamad/run-state.json`.

## Remaining risks

- Full integration/regression/slow tests beyond the fast `tests` suite remain deselected by project default; the story-specific integration file was run with `--long`.

## Suggested reviewer focus

- Verify whether keeping `chart_json` optional in the natal placeholder governance registry is still acceptable as a bounded transition for non-migrated prompts.

## Feedback loop routing

- no-propagation: no reusable skill or guardrail correction identified beyond story-local evidence and tests.

## Implementation review closure

- Fresh implementation review artifact: `generated/11-code-review.md`.
- Review verdict: CLEAN.
- Tracker closure: `story-status.md` updated to `done` on 2026-05-27.
