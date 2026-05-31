# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Full birth time enables all time-dependent families. | `basic_natal_eligibility.py` returns `full_birth_time` with all gates true when time, timezone, houses and rulers are present. | `python -B -m pytest -q backend/tests/unit/domain/astrology/test_basic_natal_eligibility_context.py ...` PASS. | PASS |
| AC2 | Approximate birth time marks cautious eligibility. | `build_basic_natal_eligibility_context` maps approximate time to `approximate_birth_time` and keeps cautious family gates. | `test_approximate_birth_time_keeps_cautious_family_access` PASS. | PASS |
| AC3 | Date-only input disables house-dependent families. | Date-only branch disables houses, angles, house rulers and lunar nodes by house. | `test_date_only_disables_house_dependent_families_with_public_limitation` PASS. | PASS |
| AC4 | Date-only limitation is public. | Limitation text is readable French and excludes internal markers. | Public marker assertion in `test_basic_natal_eligibility_context.py` PASS. | PASS |
| AC5 | Missing timezone prevents full-time confidence. | `structured_facts_v1_builder.py` exposes `birth_timezone`; eligibility downgrades missing timezone to `approximate_birth_time`. | `test_missing_timezone_prevents_full_birth_time_confidence` PASS. | PASS |
| AC6 | Partial chart state cannot enable absent surfaces. | Family gates require actual house/ruler surfaces; absent houses remain false even with full time. | `test_partial_chart_state_cannot_enable_absent_surfaces` PASS. | PASS |
| AC7 | Downstream Basic uses eligibility. | `llm_astrology_input_v1.py` imports and calls `apply_basic_natal_eligibility_to_llm_blocks`. | AST guard `test_llm_input_builder_consumes_canonical_eligibility_guard` PASS. | PASS |
| AC8 | Non-time-dependent facts remain available. | Date-only LLM filtering keeps zodiac positions, sign balances and major aspects while clearing house data. | `test_date_only_llm_input_removes_house_surfaces_but_keeps_core_facts` PASS. | PASS |
| AC9 | No noon surrogate drives house interpretation. | No default-hour path added; eligibility never invents a replacement time. | Bounded `rg` scan: only `afternoon` false positive outside target LLM/astrology surfaces. | PASS |
| AC10 | Story evidence artifacts are persisted. | `evidence/*.md`, `evidence/*.txt`, this traceability file and final evidence are present. | Capsule validation final PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
