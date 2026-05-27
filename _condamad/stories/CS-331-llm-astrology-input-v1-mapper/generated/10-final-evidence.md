# Final Evidence — CS-331-llm-astrology-input-v1-mapper

## Story status

- Validation outcome: pass
- Ready for review: yes
- Story key: CS-331-llm-astrology-input-v1-mapper
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-331-llm-astrology-input-v1-mapper`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/00-story.md`
- Story-status source alignment: PASS for `CS-331`, target path and brief source.
- Initial `git status --short`: `?? _condamad/run-state.json`
- Pre-existing dirty files: `_condamad/run-state.json`
- AGENTS.md considered: repository root `AGENTS.md`.
- Capsule generated: repaired target `generated/` files after confirming they were missing.

## Capsule validation

- Initial target capsule validation after repair: PASS.
- Final capsule validation after evidence update: PASS.

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Canonical `LLMAstrologyInputV1Builder` in interpretation domain. | Unit and architecture tests PASS. | PASS | One mapper owner. |
| AC2 | Facts sourced from `structured_facts_v1`. | Unit assertions and AST import guard PASS. | PASS | No raw carrier source. |
| AC3 | Signals sourced from `AINarrativeInputContract`. | Unit assertions and AST import guard PASS. | PASS | Readiness and masking included. |
| AC4 | Limits include missing data and readiness gaps. | Missing-data unit test PASS. | PASS | Prompt-visible shape. |
| AC5 | Evidence uses compact refs through validation owner. | Unit serialization and import guard PASS. | PASS | No verbose audit payload. |
| AC6 | Shaping remains metadata-only. | Disjoint ownership test PASS. | PASS | Facts exclude plan/module. |
| AC7 | Complete natal fixture covered. | Complete mapping assertions PASS. | PASS | Positions, houses, aspects, balances, dominants. |
| AC8 | Missing-data fixture covered. | Missing-data assertions PASS. | PASS | Empty sections explicit. |
| AC9 | Field ownership is disjoint. | Non-duplication test PASS. | PASS | Facts/signals/shaping split. |
| AC10 | Raw carriers are excluded. | Negative assertions and targeted scan PASS. | PASS | Exclusions only. |
| AC11 | Public API unchanged. | OpenAPI/routes/TestClient guards PASS. | PASS | No public route/schema. |
| AC12 | Evidence artifacts persisted. | Capsule evidence files present and validate. | PASS | `evidence/*.txt` and sample payload. |

## Files changed

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- `backend/tests/architecture/test_llm_astrology_input_boundary.py`
- `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/generated/**`
- `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Updated `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` for complete mapping, missing data, disjoint ownership and raw-carrier exclusions.
- Added `backend/tests/architecture/test_llm_astrology_input_boundary.py` for canonical owner and public-surface neutrality.

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `ruff format app\domain\astrology\interpretation\structured_facts_v1_builder.py app\domain\astrology\interpretation\llm_astrology_input_v1.py tests\unit\domain\astrology\test_llm_astrology_input_v1.py tests\architecture\test_llm_astrology_input_boundary.py` | `backend` | PASS | Scoped formatting applied. |
| `ruff check .` | `backend` | PASS | All checks passed. |
| `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_v1.py tests\unit\domain\astrology\test_structured_facts_v1_builder.py tests\architecture\test_llm_astrology_input_boundary.py --tb=short` | `backend` | PASS | 18 passed. |
| `python -B -m pytest -q tests\architecture\test_astrology_doctrine_governance_guardrails.py tests\unit\domain\astrology\test_llm_astrology_input_v1.py --tb=short` | `backend` | PASS | 10 passed. |
| `python -B -m pytest -q tests --tb=short` | `backend` | PASS | 1172 passed, 215 deselected. |
| `python -B -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"` | `backend` | PASS | No OpenAPI exposure. |
| `python -B -c "from app.main import app; assert all('llm_astrology' not in getattr(r, 'path', '') for r in app.routes)"` | `backend` | PASS | No route exposure. |
| `rg -n "from app\.api|from app\.infra|from app\.infrastructure|sqlalchemy|fastapi|OpenAI|AIEngineAdapter" ...` | repo root | PASS | No matches; exit code 1 expected for negative scan. |

## Commands skipped or blocked

- none

## DRY / No Legacy evidence

- One canonical mapper owner: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`.
- No compatibility shim, alias, fallback, public route, frontend path, DB path, migration, prompt template edit or provider integration.
- Raw carriers remain excluded only: `ChartObjectRuntimeData`, `CalculationGraph`, `chart_json`, `natal_data`.

## Diff review

- `git diff --stat` reviewed for backend mapper, tests and capsule paths.
- `git diff --check`: PASS for story-touched tracked paths.

## Final worktree status

- Modified tracked files:
  - `_condamad/stories/story-status.md`
  - `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
  - `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
  - `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- New story files:
  - `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/generated/**`
  - `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/evidence/**`
  - `backend/tests/architecture/test_llm_astrology_input_boundary.py`
- Pre-existing untracked file retained: `_condamad/run-state.json`.

## Remaining risks

- None known. The mapper is internal and not wired into runtime prompt execution by design.

## Suggested reviewer focus

- Verify the facts/signals split: facts are prompt-readable structural data from `structured_facts_v1`, while interpretive signal codes/readiness stay under `AINarrativeInputContract`.
