<!-- Tracabilite des criteres d'acceptation CONDAMAD pour CS-205. -->

# CS-205 Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Runtime assignments are audited with day/night/participating roles. | `evidence/triplicity-runtime-audit-before.md`. | Runtime audit + evidence `rg` content check. | PASS |
| AC2 | G1 day chart activates the day triplicity ruler from runtime. | `test_day_chart_uses_day_triplicity_ruler`. | `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` PASS. | PASS |
| AC3 | G2 night chart activates the night triplicity ruler from runtime. | `test_night_chart_uses_night_triplicity_ruler`. | `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` PASS. | PASS |
| AC4 | Same-element day/night behavior is tested or documented from runtime. | `test_same_element_can_select_different_triplicity_ruler_by_sect` + G3 snapshot. | Targeted pytest + `triplicity-golden-after.json`. | PASS |
| AC5 | Participating triplicity ruler behavior is tested or documented. | `test_participating_triplicity_ruler_behavior` + audit participant note. | Targeted pytest + validation note. | PASS |
| AC6 | A non-ruler does not receive active triplicity for the active sect. | `test_non_ruler_does_not_receive_triplicity`. | Targeted pytest PASS. | PASS |
| AC7 | Full scoring service integration consumes `ChartSectResult`. | `test_planet_dignity_scoring_service_selects_triplicity_by_chart_sect`. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` PASS. | PASS |
| AC8 | No production triplicity constants or local doctrine tables are introduced. | No production code changed. | Anti-constant and forbidden-pattern scans zero-hit. | PASS |
| AC9 | Essential dignity scores remain unchanged. | Test-only story; production scoring unchanged. | Snapshot evidence + `test_traditional_golden_cases.py` PASS. | PASS |
| AC10 | Persistent evidence artifacts exist. | Four evidence artifacts added. | `python -m json.tool` and evidence `rg` PASS. | PASS |
| AC11 | Public JSON remains unchanged. | No public JSON code changed. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` PASS + forbidden path diff empty. | PASS |
