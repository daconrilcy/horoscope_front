# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | G1/G2 prove day/night chart sect plus Sun horizon fields. | `test_traditional_golden_cases.py` and `golden-cases-after.json` cover G1/G2. | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` PASS. | PASS |
| AC2 | G3-G6 prove in-sect/out-of-sect for diurnal/nocturnal planets. | Runtime-backed dignity cases assert `PlanetSectCondition` and `out_of_sect`. | Targeted pytest PASS; snapshot G3-G6 present. | PASS |
| AC3 | G7/G8 prove hayz complete versus in-sect-only incomplete. | G7 asserts `hayz`, advanced profile contribution and governed signal; G8 asserts in-sect without advanced `hayz` condition or profile contribution. | Targeted pytest PASS; snapshot G7/G8 present. | PASS |
| AC4 | G9 proves planetary rejoicing remains stable. | G9 asserts `planetary_joy` accidental score and profile contribution. | Targeted pytest PASS; snapshot G9 present. | PASS |
| AC5 | G10 proves explicit runtime-backed Mercury handling. | G10 asserts Mercury `common` / `variable_by_condition` from runtime rule input. | Targeted pytest PASS; index documents G10. | PASS |
| AC6 | G11 proves at least one essential dignity remains stable. | G11 asserts Sun domicile and score axes. | Targeted pytest PASS; snapshot G11 present. | PASS |
| AC7 | G12 proves full pipeline propagation to downstream JSON outputs. | G12 runs `build_natal_result`, `build_chart_json`, dominance and adapter fixture. | Targeted pytest PASS; G12 snapshot present. | PASS |
| AC8 | Snapshots stay curated compact without volatile fields. | `golden_snapshot.py` normalizes/rounds; G12 JSON projection is curated. | `python -m json.tool` before/after PASS. | PASS |
| AC9 | No local production doctrine constants, test-local doctrine engines or recalculations are introduced. | Helpers use canonical services, explicit case inputs and shared runtime fixture `complete_reference_with_planet_sect_rules`. | Required `rg` scans PASS with classified hits. | PASS |
| AC10 | No forbidden path or dependency change is made. | Diff limited to backend tests, story evidence/capsule files and the shared test factory used by those tests. | Diff review PASS; validation markdown records no forbidden changes. | PASS |
| AC11 | Public JSON remains aligned with CS-197/CS-198. | G12 asserts JSON `dignities.sect` and `sect_condition`; existing JSON tests pass. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` PASS. | PASS |
| AC12 | Persistent evidence artifacts cover all case IDs G1-G12. | Index, before marker, after snapshot and validation summary exist. | `Test-Path` and case-ID `rg` evidence PASS. | PASS |
