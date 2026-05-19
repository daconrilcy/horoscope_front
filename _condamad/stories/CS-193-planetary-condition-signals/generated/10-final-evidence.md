# Final Evidence

## Story status

- Validation outcome: CLEAN
- Ready for review: yes
- Story key: CS-193-planetary-condition-signals
- Source story: `_condamad/stories/CS-193-planetary-condition-signals/00-story.md`
- Capsule path: `_condamad/stories/CS-193-planetary-condition-signals`
- Review/fix loop outcome: clean after the second review pass.

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial dirty files before CS-193 edits: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, `_condamad/stories/CS-194-dominant-planets-engine/`
- AGENTS.md considered: `AGENTS.md`
- Capsule generated: yes

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Migration and SQLAlchemy model for `astral_planet_condition_signal_profiles`. | `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` -> 5 passed. | PASS | Exact command without `--long` deselects integration tests by repo marker policy. |
| AC2 | Runtime field `AstrologyRuntimeReference.condition_signal_profiles`. | Runtime repository/guard tests -> 22 passed. | PASS | |
| AC3 | Builder emits technical signal payload only. | Builder/natal contract tests -> 5 passed; LLM/narrative scan zero hit. | PASS | |
| AC4 | Repository loads signal profiles and builder consumes runtime reference. | Runtime repository/guard tests -> 22 passed. | PASS | |
| AC5 | Inclusive ranges come from runtime rows. | Builder tests -> 5 passed; threshold scan zero hit. | PASS | |
| AC6 | `NatalResult.condition_signals` added and populated after profiles. | Natal contract tests included in 5 passed. | PASS | |
| AC7 | `planet_condition_signals` projected by chart JSON. | Chart JSON/result tests -> 20 passed; projection scan reviewed. | PASS | |
| AC8 | `RG-120` protected by guard tests and scans. | Guard tests included in 22 passed; three forbidden scans zero hit. | PASS | |
| AC9 | Existing public sections remain asserted while new fields are added. | Chart tests -> 20 passed; `ruff format .` PASS; `ruff check .` PASS. | PASS | Root Ruff config excludes generated hidden tool bundles so the required repo-level commands validate application/story code. |
| AC10 | Signals sorted by priority, axis, code. | Builder tests -> 5 passed. | PASS | |

## Files changed

- Story evidence: `_condamad/stories/CS-193-planetary-condition-signals/generated/**`, `_condamad/stories/CS-193-planetary-condition-signals/evidence/**`
- Governance touched by worktree/story: `_condamad/stories/story-status.md`
- Repo quality config: `ruff.toml`
- Preflight-only out-of-scope work: `_condamad/stories/CS-194-dominant-planets-engine/**`
- Backend runtime/contracts: `backend/app/domain/astrology/runtime/runtime_reference.py`, `backend/app/domain/astrology/condition/contracts.py`, `backend/app/domain/astrology/condition/planet_condition_signal_builder.py`, `backend/app/domain/astrology/condition/__init__.py`
- Backend integration: `backend/app/domain/astrology/natal_calculation.py`, `backend/app/services/chart/json_builder.py`
- DB/seed/runtime loading: `backend/app/infra/db/models/dignity_reference.py`, `backend/app/infra/db/models/__init__.py`, `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`, `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`, `backend/app/services/reference_data/dignity_seed_service.py`, `backend/migrations/versions/20260519_0131_create_planet_condition_signal_profiles.py`, `docs/db_seeder/astrology/astral_planet_condition_signal_profiles.json`
- Tests: `backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py`, `backend/tests/unit/domain/astrology/test_natal_result_contract.py`, `backend/tests/factories/astrology_runtime_reference_factory.py`, `backend/app/tests/unit/test_chart_json_builder.py`, `backend/app/tests/unit/test_chart_result_service.py`, `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`, `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`, `backend/app/tests/integration/test_reference_data_migrations.py`

## Files deleted

None.

## Tests added or updated

- Added builder tests for inclusive runtime ranges, deterministic sorting and non-editorial payload.
- Updated runtime repository tests for DB-loaded signal profiles, missing profiles and invalid `expression_quality` axis.
- Updated natal contract, chart JSON/result persistence and migration tests.
- Updated architecture guard for `RG-120` and projection-only serialization.

## Commands run

All Python commands below were run after `.\\.venv\\Scripts\\Activate.ps1`.

| Command | Result |
|---|---|
| `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py backend/tests/unit/domain/astrology/test_natal_result_contract.py` | PASS, 5 passed |
| `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | PASS, 20 passed |
| `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` | PASS, 22 passed |
| `pytest -q backend/app/tests/integration/test_reference_data_migrations.py` | NOT RUN by marker policy, 5 deselected |
| `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` | PASS, 5 passed |
| `ruff format --check backend/app backend/tests` | PASS, 1210 files already formatted |
| `ruff check backend/app backend/tests` | PASS |
| `ruff check .` | PASS after adding root `ruff.toml` exclusions for generated hidden tool bundles |
| `ruff format --check .` | PASS, 1435 files already formatted |
| `ruff format .` | PASS, 1435 files left unchanged |
| `git diff --check` | PASS, CRLF warnings only |
| `rg -n "Session\|select\\(\|from app\\.infra\|from app\\.services\|from app\\.api\|from app\\.domain\\.prediction\|from app\\.services\\.prediction" backend/app/domain/astrology/condition -g "*.py"` | PASS, zero hits |
| `rg -n "OpenAI\|AIEngineAdapter\|chat\\.completions\|\\bprompt\\b\|narration\|micro_note" backend/app/domain/astrology/condition -g "*.py"` | PASS, zero hits |
| `rg -n "SIGNAL_THRESHOLDS\|CONDITION_SIGNAL_RULES\|CONDITION_SIGNAL_PROFILES\|FUNCTIONAL_STRENGTH_THRESHOLDS\|VISIBILITY_SIGNAL_LEVELS" backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"` | PASS, zero hits |
| `rg -n "planet_condition_signals\|condition_signals" backend/app/services/chart/json_builder.py backend/app/domain/astrology/natal_calculation.py backend/app/domain/astrology/condition -g "*.py"` | PASS, integration/projection sites only |
| `Set-Location backend; python -c "from app.main import app; print(app.title)"` | PASS, `horoscope-backend` |

## Commands skipped or blocked

- No frontend command run: CS-193 does not touch `frontend/**`.
- No server kept running: backend application import was validated; local run remains the normal backend launch flow.

## DRY / No Legacy evidence

- The domain builder imports only condition contracts and runtime contracts.
- DB table/model/repository stay under infra and seed service.
- `json_builder.py` only serializes `NatalResult.condition_signals`; it does not compare condition scores or instantiate the builder.
- No local threshold map, fallback, compatibility wrapper, alias, prompt adapter, frontend logic or LLM integration was introduced.

## Review findings fixed

- Fixed accepted finding: remove `expression_quality` from allowed runtime signal axes and add rejection test.
- Fixed accepted finding: complete final evidence and AC traceability.
- Fixed accepted finding: enrich before/after evidence with explicit contract diff and stable-section assertions.
- Fixed accepted finding: make repository-level Ruff validation executable by excluding generated hidden tool bundles from the root lint scope.

## Diff review

- Scope matches CS-193 backend-only target plus persistent story evidence.
- CS-194 governance/story artifacts were dirty before implementation and are classified as pre-existing, not part of CS-193 closure.

## Final worktree status

See final `git status --short` in chat response.

## Remaining risks

- Aucun risque restant identifie pour CS-193.
- Worktree note: `_condamad/stories/CS-194-dominant-planets-engine/**` remains pre-existing out-of-scope work and must stay isolated from the CS-193 delivery boundary.

## Suggested reviewer focus

- Verify `PlanetConditionSignalBuilder` remains a projection from `PlanetConditionProfile` plus runtime profiles only.
- Verify `ruff.toml` keeps generated hidden tool bundles out of repository-level application lint.
