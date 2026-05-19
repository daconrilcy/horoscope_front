<!-- Evidence finale CONDAMAD de l'implementation CS-194. -->

# Final Evidence

## Story status

- Validation outcome: PASS
- Review verdict: CLEAN
- Story registry status: `done`
- Story key: `CS-194-dominant-planets-engine`
- Source story: `_condamad/stories/CS-194-dominant-planets-engine/00-story.md`
- Capsule path: `_condamad/stories/CS-194-dominant-planets-engine`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `?? _condamad/stories/CS-194-dominant-planets-engine/`
- Pre-existing dirty files: `_condamad/stories/CS-194-dominant-planets-engine/**`
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing generated execution files created.
- CS-193 precondition: satisfied; story status registry marks `CS-193` as `done`.
- Frontend subagent: not used; no `frontend/**` surface changed.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Migration, model, seed JSON and seed service add `astral_dominance_factor_types`; tests assert all eight full rows. | Runtime repository tests and migration tests. | PASS |
| AC2 | `AstrologyRuntimeReference.dominance_factor_types` loads active rows sorted by `sort_order`. | Runtime repository tests. | PASS |
| AC3 | `PlanetDominance*` dataclasses are frozen. | Dominance engine tests. | PASS |
| AC4 | Engine sorts `dominance_score` descending then `planet_code`. | Dominance engine tests. | PASS |
| AC5 | Each planet result contains one contribution per active factor. | Dominance engine tests. | PASS |
| AC6 | `chart_ruler` reads `house_rulers`; no local rulership map was added. | Dominance engine tests and scans. | PASS |
| AC7 | `condition_strength` and `visibility` read `PlanetConditionProfile`. | Dominance engine tests. | PASS |
| AC8 | `aspect_centrality` routes through `DominantAspectEvaluator.rank(...)` and ignores non-ranked point participants for normalization. | Dominance engine tests. | PASS |
| AC9 | `NatalResult.planet_dominance` is added and populated after chart balance. | Natal contract tests and full suite. | PASS |
| AC10 | `build_chart_json` projects `planet_dominance` without engine calls and nulls it in no-time modes. | Chart JSON/result tests and projection guard. | PASS |
| AC11 | `RG-121` and guard tests block local weights and boundary drift. | Runtime guard tests and scans. | PASS |
| AC12 | Existing public payload sections remain stable; `planet_dominance` is the authorized addition. | Before/after JSON snapshots, diff evidence, Ruff and full pytest. | PASS |

## Review fixes applied

- Replaced `generated/11-code-review.md` with the current main-session review
  evidence after detecting an execution-mode inconsistency in the previous
  review artifact.
- Replaced direct aspect centrality accumulation with canonical `DominantAspectEvaluator.rank(...)`.
- Added tests for aspect factor raw values, weights, evidence and point-participant normalization.
- Gated public `planet_dominance` to `null` for `no_time` and `no_location_no_time`.
- Added guard evidence classifying `chart_balance.dominant_planets` as structural balance output, not CS-194 canonical factual dominance.
- Replaced schematic before/after evidence with concrete JSON payload snapshots plus `planet-dominance-diff.json`.
- Strengthened AC1 tests and runtime evidence to cover labels, categories, all weights, activity flags and descriptions.
- The earlier startup import attempted from `backend/` with the wrong relative activation path is discarded and is not counted as validation evidence; the valid startup command was rerun from repo root after venv activation.

## Files changed

| File | Purpose |
|---|---|
| `backend/migrations/versions/20260519_0132_create_dominance_factor_types.py` | Create dominance factor table. |
| `docs/db_seeder/astrology/astral_dominance_factor_types.json` | Seed exact factor contract. |
| `backend/app/infra/db/models/dignity_reference.py` | Add SQLAlchemy model. |
| `backend/app/infra/db/models/__init__.py` | Register model in metadata. |
| `backend/app/services/reference_data/dignity_seed_service.py` | Sync dominance factor rows per reference version. |
| `backend/app/domain/astrology/runtime/runtime_reference.py` | Add runtime factor contract. |
| `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` | Load and validate dominance factors. |
| `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` | Map infra rows to runtime contract. |
| `backend/app/domain/astrology/dominance/**` | Add immutable contracts and pure dominance engine. |
| `backend/app/domain/astrology/natal_calculation.py` | Populate `NatalResult.planet_dominance`. |
| `backend/app/services/chart/json_builder.py` | Project `planet_dominance` and suppress it when birth time is absent. |
| `backend/tests/**`, `backend/app/tests/**` | Unit, integration and guard coverage. |
| `_condamad/stories/regression-guardrails.md` | Add `RG-121`. |
| `_condamad/stories/CS-194-dominant-planets-engine/**` | Capsule, review and persistent evidence. |
| `_condamad/stories/story-status.md` | Mark CS-194 as `done`. |

## Commands run

All counted Python commands below were run after `.\\.venv\\Scripts\\Activate.ps1`.

| Command | Result | Evidence summary |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_natal_result_contract.py` | PASS | Initial dominance/natal contract validation. |
| `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | PASS | Initial chart JSON/persistence validation. |
| `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` | PASS | Initial runtime/guard validation. |
| `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` | PASS | 5 passed. |
| `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | PASS | 52 passed after review fixes. |
| `ruff format .; ruff check .` | PASS | 1440 files left unchanged; all checks passed after final fix. |
| `Set-Location backend; python -c "from app.main import app; print(app.title)"` | PASS | `horoscope-backend`. |
| `pytest -q` | PASS | 2710 passed, 1 skipped, 1177 deselected. |
| `git diff --check` | PASS | CRLF warnings only. |
| `pytest -q` | PASS | 2710 passed, 1 skipped, 1177 deselected after the final review evidence correction. |

## Targeted scans

| Scan | Result | Notes |
|---|---|---|
| `rg -n "Session\|select\\(\|from app\\.infra\|from app\\.services\|from app\\.api\|from app\\.domain\\.prediction\|from app\\.services\\.prediction" backend/app/domain/astrology/dominance -g "*.py"` | PASS | Zero hits. |
| `rg -n "OpenAI\|AIEngineAdapter\|chat\\.completions\|\\bprompt\\b\|narration\|micro_note" backend/app/domain/astrology/dominance -g "*.py"` | PASS | Zero hits. |
| `rg -n "DOMINANCE_FACTORS\|DOMINANCE_WEIGHTS\|CHART_RULER_WEIGHT\|ANGULARITY_WEIGHT\|SIGN_RULERS\|PLANET_RULERS" backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"` | PASS_WITH_CLASSIFIED_HITS | No active dominance weight map; remaining hits are pre-existing test fixtures or guard literals. |
| `rg -n "planet_dominance\|PlanetDominance\|DominantAspectEvaluator\|dominant_aspect" ...` | PASS | Shows expected integration, projection and guard sites. |

## Persistent evidence

- `evidence/planet-dominance-before.json`
- `evidence/planet-dominance-after.json`
- `evidence/planet-dominance-diff.json`
- `evidence/dominance-runtime-reference.md`
- `evidence/dominance-guard-evidence.md`
- `generated/11-code-review.md`

## Final worktree status

Worktree contains the CS-194 implementation and capsule/evidence updates only; no commit was made.

## Remaining risks

- No blocking or material residual risk identified.
- Broad `SIGN_RULERS` scan hits are pre-existing fixtures/guard literals outside the CS-194 dominance engine.
