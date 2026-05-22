# CS-221 Final Evidence

## Summary

- Story: `CS-221-chart-object-house-position-rulership-runtime`
- Outcome: PASS
- Python venv: all Python commands were run after `.\.venv\Scripts\Activate.ps1`.
- Public/API/frontend/DB impact: none.

## Baseline And Scope

- `ChartObjectHousePositionPayload` previously carried only `house_number`.
- `ChartObjectPayloads` previously had no `rulership` payload.
- `HouseRulerResolver` and `HouseRulerResult` already produced canonical house rulers.
- `resolve_house_kind` already classified houses as `angular`, `succedent`, or `cadent`.
- `RG-148` was already registered in `_condamad/stories/regression-guardrails.md`.

## Implementation Evidence

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
  - added `supports_rulership`;
  - enriched `ChartObjectHousePositionPayload`;
  - added `RulershipRuntimePayload`;
  - added `ChartObjectPayloads.rulership`;
  - added `validate_rulership_payloads`.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
  - centralizes house-position payload construction through `build_house_position_payload`;
  - reuses `resolve_house_kind`;
  - declares rulership capability for eligible planet/luminary runtime objects.
- `backend/app/domain/astrology/builders/chart_object_house_runtime_enricher.py`
  - projects `HouseRulerResult` and `sign_rulerships`;
  - derives `rules_houses`, ASC/MC flags and `dispositor_code`;
  - does not instantiate `HouseRulerResolver` and does not define a local sign-ruler table.
- `backend/app/domain/astrology/natal_calculation.py`
  - enriches `chart_objects` after `house_rulers` and initial chart-object construction.

## Validation Commands

| Command | Result | Evidence |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | PASS | 33 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | PASS | 18 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py -k replacing_collections` | PASS | AC11 review fix passed; historical collections remain populated with chart objects |
| `pytest -q backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | PASS | Review-fix rerun: 51 passed |
| `ruff format .` from `backend/` | PASS | 3 files reformatted |
| `ruff check . --fix; ruff check .` from `backend/` | PASS | import order fixed, all checks passed |
| `pytest -q` from `backend/` | PASS | Final rerun: 3014 passed, 1 skipped, 1177 deselected |
| `python -B -c "from app.main import app; print(len(app.routes))"` from `backend/` | PASS | FastAPI app imports; 221 routes |
| `git diff --check` | PASS | no whitespace errors; CRLF warnings only |

## Scan Evidence

| Scan | Result | Classification |
|---|---|---|
| `rg -n "object_type ==|\.object_type ==|ChartObjectType\.PLANET|ChartObjectType\.LUMINARY" backend/app/domain/astrology/builders backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance -g "*.py"` | PASS with one hit | Existing builder construction classifies luminary/planet; not a house/rulership consumer eligibility branch. |
| `rg -n "HouseRulershipPayloadBuilder|MarsRulershipPayloadBuilder|new.*HouseRulerResolver|SIGN_RULERS|sign_rulers\s*=\s*\{" backend/app/domain/astrology -g "*.py"` | PASS | Zero active hits. |
| `rg -n "\{1, 4, 7, 10\}|\{2, 5, 8, 11\}|angular.*succedent.*cadent" backend/app/domain/astrology/builders backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance -g "*.py"` | PASS | Zero hits; modality is delegated to `resolve_house_kind`. |
| `rg -n "interpretation|narrative|prompt|llm|meaning|psychological" backend/app/domain/astrology/runtime backend/app/domain/astrology/builders -g "*.py"` | PASS with classified hits | Hits are pre-existing runtime/reference/interpretation surfaces or `supports_interpretation`; no narrative field in house/rulership payloads. |
| `rg -n "RG-148" _condamad/stories/regression-guardrails.md` | PASS | `RG-148` present. |
| `git diff -- backend/app/domain/astrology/planetary_conditions backend/app/domain/astrology/interpretation backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | PASS | Empty diff. |

## Review Fix Evidence

- Accepted CR-1: story status synchronized to `ready-to-review` in `00-story.md` and `_condamad/stories/story-status.md`.
- Accepted CR-2: diff evidence now explicitly classifies untracked CS-221 files instead of relying on `git diff --stat` alone.
- Accepted CR-3: AC11 now has a targeted assertion in `test_build_natal_result_populates_chart_objects_without_replacing_collections`.

## Remaining Risks

- Aucun risque restant identifie.
