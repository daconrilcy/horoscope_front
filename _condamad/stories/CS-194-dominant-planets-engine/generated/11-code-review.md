<!-- Revue CONDAMAD finale de CS-194. -->

# CONDAMAD Code Review

## Review target

- Story: `CS-194-dominant-planets-engine`
- Verdict: `CLEAN`
- Date locale: 2026-05-19
- Reviewer mode: main Codex review, sans sous-agent.

## Inputs reviewed

- `_condamad/stories/CS-194-dominant-planets-engine/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- Generated capsule files `03`, `04`, `06`, `07`, `10`
- Evidence files under `_condamad/stories/CS-194-dominant-planets-engine/evidence/`
- Application code for DB migration/model/seed, runtime reference, dominance
  domain, natal integration, chart JSON projection and tests
- Current worktree status, including unrelated CS-195 dirty files scoped out

## Diff summary

CS-194 adds `astral_dominance_factor_types`,
`astral_dominance_score_profiles` and `astral_dominance_score_weights`, loads
them through `AstrologyRuntimeReference`, adds immutable dominance contracts
and `PlanetDominanceEngine`, populates `NatalResult.dominant_planets`, and
projects top-level JSON `dominant_planets` through `build_chart_json`.

No frontend files, dependencies, routes or status codes were changed.

## Findings

No open findings.

### Fixed in this review/fix cycle

#### CR-1 Medium - Capsule evidence used the retired public field name

- Bucket: patch
- Location: `_condamad/stories/CS-194-dominant-planets-engine/generated/11-code-review.md`
- Source layer: evidence / validation
- Evidence: several CS-194 evidence files still claimed
  `NatalResult.planet_dominance` and JSON `planet_dominance`, while the
  post-review addendum and implementation use `NatalResult.dominant_planets`
  and top-level `dominant_planets`.
- Impact: a future review could approve the wrong public contract or miss a
  serializer regression because the capsule contradicted the repository state.
- Fix applied: normalized the story/evidence references to
  `dominant_planets`, `_serialize_dominant_planets` and the current
  `PlanetDominanceResult` contract.

## Acceptance audit

- AC1: PASS. Migration, model, seed JSON, seed service and tests cover the
  dominance factor table and active rows.
- AC2: PASS. Runtime repository exposes active dominance factors ordered by
  `sort_order` and loads the scoring profile/weights.
- AC3: PASS. Dominance contracts are frozen dataclasses.
- AC4: PASS. `PlanetDominanceEngine` ranks by descending `total_score`, then
  `planet_code`.
- AC5: PASS. Each planet has a contribution breakdown for every active factor.
- AC6: PASS. `chart_ruler` consumes resolved `house_rulers`; no local
  rulership map was introduced in the dominance engine.
- AC7: PASS. `condition_strength` and `visibility` consume
  `PlanetConditionProfile`.
- AC8: PASS. `aspect_centrality` uses the canonical `DominantAspectEvaluator`.
- AC9: PASS. `NatalResult` exposes `dominant_planets` without removing
  `chart_balance.dominant_planets`.
- AC10: PASS. `json_builder.py` serializes `NatalResult.dominant_planets` and
  does not instantiate the dominance engine.
- AC11: PASS. `RG-121` and runtime guard tests block forbidden local weights,
  boundary imports and narrative/LLM symbols.
- AC12: PASS. The authorized public payload difference is the added
  `dominant_planets` field.

## Validation audit

Commands run from repository root with `.\\.venv\\Scripts\\Activate.ps1` for
Python tooling:

- `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
  -> PASS, 56 passed.
- `ruff format --check .` -> PASS, 1440 files already formatted.
- `ruff check .` -> PASS, all checks passed.
- `Set-Location backend; python -c "from app.main import app; print(app.title)"`
  -> PASS, `horoscope-backend`.
- `pytest -q` -> PASS, 2712 passed, 1 skipped, 1177 deselected.
- `git diff --check` -> PASS, CRLF warnings only on pre-existing dirty
  governance files.

Targeted scans:

- `rg -n "Session|select\\(|from app\\.infra|from app\\.services|from app\\.api|from app\\.domain\\.prediction|from app\\.services\\.prediction" backend/app/domain/astrology/dominance -g "*.py"`
  -> PASS, zero hits.
- `rg -n "OpenAI|AIEngineAdapter|chat\\.completions|\\bprompt\\b|narration|micro_note" backend/app/domain/astrology/dominance -g "*.py"`
  -> PASS, zero hits.
- `rg -n "DOMINANCE_FACTORS|DOMINANCE_WEIGHTS|CHART_RULER_WEIGHT|ANGULARITY_WEIGHT|SIGN_RULERS|PLANET_RULERS" backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"`
  -> PASS_WITH_CLASSIFIED_HITS. No active dominance factor/weight map;
  remaining hits are pre-existing test fixtures or guard literals outside the
  CS-194 dominance engine.

## DRY / No Legacy audit

- No compatibility wrapper, alias, duplicate serializer or fallback engine was
  added.
- Dominance weights and factor metadata are DB/runtime-backed.
- `ChartSignatureCalculator.dominant_planets` remains a structural
  chart-balance output, not the CS-194 canonical factual dominance engine.
- `json_builder.py` does not import or instantiate `PlanetDominanceEngine`.

## Residual risks

- No blocking or material residual risk identified.
- Broad `SIGN_RULERS` scan hits remain pre-existing fixtures or guard literals
  outside the CS-194 dominance engine.

## Verdict

`CLEAN`
