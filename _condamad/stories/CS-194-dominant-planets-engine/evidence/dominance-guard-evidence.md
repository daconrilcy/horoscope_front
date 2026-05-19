<!-- Evidence de garde CS-194 pour documenter les controles de dominance. -->

# CS-194 Dominance Guard Evidence

Date locale: 2026-05-19

## Sequencing check

La precondition initialement bloquante est levee:

- `_condamad/stories/story-status.md` marque `CS-193` comme `done`;
- `NatalResult` expose `condition_signals`;
- `json_builder.py` projette `planet_condition_signals`.

## Guard evidence

| Guard | Result | Notes |
|---|---|---|
| Domain boundary scan | PASS | `rg -n "Session\|select\\(\|from app\\.infra\|from app\\.services\|from app\\.api\|from app\\.domain\\.prediction\|from app\\.services\\.prediction" backend/app/domain/astrology/dominance -g "*.py"` -> zero hit. |
| LLM/text scan | PASS | `rg -n "OpenAI\|AIEngineAdapter\|chat\\.completions\|\\bprompt\\b\|narration\|micro_note" backend/app/domain/astrology/dominance -g "*.py"` -> zero hit. |
| Local dominance weights scan | PASS_WITH_CLASSIFIED_HITS | No active dominance weight map remains. Existing hits are unrelated historical/test rulership fixtures: `SIGN_RULERSHIPS`, `COMPLETE_SIGN_RULERS`, and the existing runtime guard literal. |
| Projection scan | PASS | `json_builder.py` contains only `_serialize_dominant_planets` and payload projection; no `PlanetDominanceEngine` call. |
| Aspect centrality reuse | PASS | `PlanetDominanceEngine` routes aspect centrality through `DominantAspectEvaluator.rank(...)`; no local orb-strength fallback remains. |
| Chart balance classification | PASS | `chart_balance.dominant_planets` remains the pre-existing structural balance field sourced from `sign_runtime`; top-level `dominant_planets` is the canonical factual planetary dominance output for CS-194. |
| Runtime guard tests | PASS | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` -> updated after review fixes. |

## Generated contract check

OpenAPI does not model the dynamic chart JSON internals added here as a typed
`dominant_planets` schema. No route, HTTP method, status code or declared
OpenAPI response model changed; the contract evidence is therefore held in the
chart JSON projection tests and before/after story snapshots.

## RG-121

`_condamad/stories/regression-guardrails.md` now contains `RG-121`, protecting:

- `PlanetDominanceEngine` as canonical factual dominance engine;
- DB/runtime ownership for factors and weights;
- no DB/API/services/prediction/LLM imports in the dominance domain;
- aspect centrality sourced from the canonical dominant-aspect evaluator;
- `ChartSignatureCalculator.dominant_planets` classified as structural chart
  balance, not the canonical CS-194 factual dominance engine;
- projection-only behavior in `json_builder.py`.
