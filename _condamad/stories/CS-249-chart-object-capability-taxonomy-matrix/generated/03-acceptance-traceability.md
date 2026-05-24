# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | All required object families are registered. | `chart_object_capability_taxonomy.py` declares `MANDATORY_CHART_OBJECT_FAMILIES` and one entry per family. | `python -B -m pytest -q backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py` PASS; `taxonomy-after.json` persisted. | PASS |
| AC2 | Each matrix row exposes required columns. | `ChartObjectCapabilityTaxonomyEntry` has every required field plus enum-typed status/source/type. | Unit test `test_each_taxonomy_row_exposes_required_columns` PASS. | PASS |
| AC3 | Existing capability values are preserved. | Active families map to current `ChartObjectCapabilities`; fixed stars remain documentary-only. | Unit test `test_existing_runtime_capabilities_are_preserved_for_active_families` PASS; `taxonomy-before.md` and `taxonomy-after.json`. | PASS |
| AC4 | Unknown object families are rejected. | `get_chart_object_capability_taxonomy` raises `ChartObjectCapabilityTaxonomyError`. | Unit test `test_unknown_family_is_rejected_without_fallback` PASS. | PASS |
| AC5 | Unresolved object decisions are explicit. | Lilith, apside, lot, asteroid, Chiron and midpoint use `needs-user-decision`. | Unit test `test_unresolved_families_are_explicit_user_decisions` PASS. | PASS |
| AC6 | New unmanaged `object_type` branches fail. | Architecture guard allowlists only runtime owners and scans AST branches. | `python -B -m pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py` PASS; negative `rg` scan PASS no matches. | PASS |
| AC7 | New family calculators are not introduced. | No calculator files/classes added; taxonomy tests keep unresolved families non-scorable/non-dignity/non-dominance. | `rg -n "LotCalculator\|AsteroidCalculator\|ChironCalculator\|MidpointCalculator" backend/app/domain/astrology backend/tests -g "*.py"` PASS no matches. | PASS |
| AC8 | Public API runtime contract is unchanged. | No API routes/schemas changed; API neutrality test covers taxonomy absence. | `python -B -m pytest -q backend/tests/architecture/test_api_contract_neutrality.py` PASS; OpenAPI route evidence persisted. | PASS |
| AC9 | Evidence artifacts are persisted. | Evidence folder contains validation, before, after and API neutrality artifacts. | Capsule validation PASS; Python evidence generation commands PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
