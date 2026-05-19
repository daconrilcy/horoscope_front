# Condition Signal Guard Evidence

## RG-120 Evidence

| Guard | Result | Evidence |
|---|---|---|
| Condition boundary scan | PASS | `rg -n "Session\|select\\(\|from app\\.infra\|from app\\.services\|from app\\.api\|from app\\.domain\\.prediction\|from app\\.services\\.prediction" backend/app/domain/astrology/condition -g "*.py"` returned zero hits. |
| LLM/narrative scan | PASS | `rg -n "OpenAI\|AIEngineAdapter\|chat\\.completions\|\\bprompt\\b\|narration\|micro_note" backend/app/domain/astrology/condition -g "*.py"` returned zero hits. |
| Local threshold scan | PASS | `rg -n "SIGNAL_THRESHOLDS\|CONDITION_SIGNAL_RULES\|CONDITION_SIGNAL_PROFILES\|FUNCTIONAL_STRENGTH_THRESHOLDS\|VISIBILITY_SIGNAL_LEVELS" backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"` returned zero hits. |
| Projection scan | PASS | `json_builder.py` only projects `NatalResult.condition_signals`; signal building is in `natal_calculation.py` through `PlanetConditionSignalBuilder`. |

## OpenAPI Note

The affected chart JSON payload is dynamic and is not represented by a generated response schema in this story. No route, HTTP method or status code changed.

