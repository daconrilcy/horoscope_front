<!-- Evidence finale CONDAMAD de l'implementation CS-194. -->

# Final Evidence

## Story status

- Validation outcome: PASS
- Review verdict: CLEAN
- Story registry status: `done`
- Story key: `CS-194-dominant-planets-engine`
- Source story: `_condamad/stories/CS-194-dominant-planets-engine/00-story.md`
- Capsule path: `_condamad/stories/CS-194-dominant-planets-engine`

## Current review/fix cycle

- Iteration count in this request: 1 review with findings, 1 fix batch, 1 clean
  follow-up review.
- Issue fixed: evidence drift from retired `planet_dominance` naming to the
  implemented `dominant_planets` public contract.
- Frontend contract: not applicable; no `frontend/**` files changed.
- Unrelated dirty files preserved: `_condamad/stories/story-status.md` already
  contains a CS-195 row, and `_condamad/stories/CS-195-advanced-planetary-conditions/`
  is untracked.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Migration, model, seed JSON and seed service add the dominance factor table; tests assert the full active rows. | Runtime repository tests and migration evidence. | PASS |
| AC2 | `AstrologyRuntimeReference.dominance_factor_types` and `dominance_reference` load active factors, `natal_standard_v1` and weights. | Runtime repository tests. | PASS |
| AC3 | `PlanetDominance*` dataclasses are frozen. | Dominance engine tests. | PASS |
| AC4 | Engine sorts `total_score` descending then `planet_code`. | Dominance engine tests. | PASS |
| AC5 | Each planet result contains one contribution per active factor. | Dominance engine tests. | PASS |
| AC6 | `chart_ruler` reads `house_rulers`; no local rulership map was added. | Dominance engine tests and scans. | PASS |
| AC7 | `condition_strength` and `visibility` read `PlanetConditionProfile`. | Dominance engine tests. | PASS |
| AC8 | `aspect_centrality` routes through `DominantAspectEvaluator.rank(...)`. | Dominance engine tests. | PASS |
| AC9 | `NatalResult.dominant_planets` is added and populated after chart balance. | Natal contract tests and targeted suite. | PASS |
| AC10 | `build_chart_json` projects `dominant_planets` without engine calls and nulls it in no-time modes. | Chart JSON/result tests and projection guard. | PASS |
| AC11 | `RG-121` and guard tests block local weights and boundary drift. | Runtime guard tests and scans. | PASS |
| AC12 | Existing public payload sections remain stable; `dominant_planets` is the authorized addition. | Before/after JSON snapshots, Ruff and targeted pytest. | PASS |

## Files changed by this request

| File | Purpose |
|---|---|
| `_condamad/stories/CS-194-dominant-planets-engine/00-story.md` | Align public contract/evidence text with implemented `dominant_planets`. |
| `_condamad/stories/CS-194-dominant-planets-engine/generated/03-acceptance-traceability.md` | Align AC9/AC10 traceability with current contract. |
| `_condamad/stories/CS-194-dominant-planets-engine/generated/04-target-files.md` | Align target scan with current contract names. |
| `_condamad/stories/CS-194-dominant-planets-engine/generated/06-validation-plan.md` | Align projection scan with current contract names. |
| `_condamad/stories/CS-194-dominant-planets-engine/generated/07-no-legacy-dry-guardrails.md` | Align serializer ownership evidence. |
| `_condamad/stories/CS-194-dominant-planets-engine/generated/10-final-evidence.md` | Replace stale evidence with current review/fix evidence. |
| `_condamad/stories/CS-194-dominant-planets-engine/generated/11-code-review.md` | Persist the fresh clean review. |
| `_condamad/stories/CS-194-dominant-planets-engine/evidence/dominance-guard-evidence.md` | Align projection and OpenAPI evidence with `dominant_planets`. |

## Commands run

All Python commands below were run after `.\\.venv\\Scripts\\Activate.ps1`.

| Command | Result | Evidence summary |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` | PASS | 56 passed. |
| `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` | PASS | 5 passed. |
| `ruff format --check .` | PASS | 1440 files already formatted. |
| `ruff check .` | PASS | All checks passed. |
| `Set-Location backend; python -c "from app.main import app; print(app.title)"` | PASS | `horoscope-backend`. |
| `pytest -q` | PASS | 2712 passed, 1 skipped, 1177 deselected. |
| `git diff --check` | PASS_WITH_WARNINGS | CRLF warnings only on dirty governance files. |

## Targeted scans

| Scan | Result | Notes |
|---|---|---|
| `rg -n "Session\|select\\(\|from app\\.infra\|from app\\.services\|from app\\.api\|from app\\.domain\\.prediction\|from app\\.services\\.prediction" backend/app/domain/astrology/dominance -g "*.py"` | PASS | Zero hits. |
| `rg -n "OpenAI\|AIEngineAdapter\|chat\\.completions\|\\bprompt\\b\|narration\|micro_note" backend/app/domain/astrology/dominance -g "*.py"` | PASS | Zero hits. |
| `rg -n "DOMINANCE_FACTORS\|DOMINANCE_WEIGHTS\|CHART_RULER_WEIGHT\|ANGULARITY_WEIGHT\|SIGN_RULERS\|PLANET_RULERS" backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"` | PASS_WITH_CLASSIFIED_HITS | No active dominance weight map; remaining hits are pre-existing test fixtures or guard literals. |
| `rg -n "dominant_planets\|DominantPlanets\|PlanetDominance" backend/app/services/chart/json_builder.py backend/app/domain/astrology/natal_calculation.py backend/app/domain/astrology/dominance -g "*.py"` | PASS | Expected integration and projection sites only. |

## Persistent evidence

- `evidence/planet-dominance-before.json`
- `evidence/planet-dominance-after.json`
- `evidence/planet-dominance-diff.json`
- `evidence/dominance-runtime-reference.md`
- `evidence/dominance-guard-evidence.md`
- `generated/11-code-review.md`

## Remaining risks

- No blocking or material residual risk identified.
- Broad `SIGN_RULERS` scan hits remain pre-existing fixtures or guard literals
  outside the CS-194 dominance engine.
