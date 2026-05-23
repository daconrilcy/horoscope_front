# CS-224 Runtime Surface Removal Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `planet_positions` | NatalResult projection | external-active | API/front, tests, chart JSON, transition runtime | `NatalResult.chart_objects` for new calculators | keep | `pytest -q` full backend OK; public schema tests OK | Suppression cassante hors scope |
| `astral_points` | NatalResult projection | external-active | API/front, interpretation service legacy, tests | `chart_objects` astral point objects | keep | Guardrail allowlist exact: `interpretation/astral_point_interpretation.py` | Migration interpretative future requise |
| `houses` | NatalResult projection | external-active | API/front, dominance, public JSON, tests | `payloads.house_position` and house runtime | keep | Scan direct `natal_result.houses` in domain: PASS no matches | Suppression cassante hors scope |
| `angles` | Legacy conceptual surface | historical-facade | Projected as `asc`, `dsc`, `mc`, `ic` objects | angle payloads in `chart_objects` | keep | No top-level `NatalResult.angles` introduced; builder owner allowlisted | None for CS-224 |
| `aspects` | Chart-level result | canonical-active | API/front, dominance, interpretation input | aspect engine fed by `chart_objects` | keep | Existing and new tests pass; no API changes | Suppression cassante hors scope |
| `dignities` / `dignity_results` | NatalResult projection | external-active | API/front, condition profiles, traditional conditions | `payloads.dignity` for object-level facts | keep | Projection test validates payload scores against `result.dignities` | Suppression cassante hors scope |
| `dominant_planets` / `dominance_result` | Chart-level result | canonical-active | API/front, interpretation input | dominance calculator and `payloads.dominance` | keep | Contract and projection tests pass | Suppression cassante hors scope |
| `advanced_conditions` | NatalResult projection | external-active | traditional normalizer, interpretation adapter, public compatibility | condition facts and chart-object payloads | keep | Scan direct `natal_result.advanced_conditions` in domain: PASS no matches | Migration future needed |
| `fixed_star_conjunctions` | Payload projection | canonical-active | interpretation input via chart-object payloads | `payloads.fixed_star_conjunctions` | keep | Projection test validates Regulus contact payload; no top-level public field | None for CS-224 |

No code deletion was performed in CS-224 because no candidate reached `dead` classification without public/API risk.
