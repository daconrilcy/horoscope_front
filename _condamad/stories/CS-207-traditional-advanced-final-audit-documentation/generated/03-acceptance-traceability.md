# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Tous les contrats CS-197 a CS-206 sont mappes. | Evidence only: contract map. | `traditional-advanced-contract-map.md` present and references all contracts. | PASS |
| AC2 | Aucun recalcul local interdit n'est present ou non classe. | Evidence only unless blocker found. | Four required `rg` scans and classified hits in scan results. | PASS |
| AC3 | Les tests backend cibles passent. | No code change expected. | Targeted pytest command: 100 passed. | PASS |
| AC4 | Les checks qualite backend passent. | No code change expected. | `ruff format .` and `ruff check .` after venv activation. | PASS |
| AC5 | Frontend expert panel sans doctrine locale. | No frontend change expected. | `npm --prefix frontend test -- NatalExpertPanel`, frontend derivation scan, lint/build. | PASS |
| AC6 | La persistance d'audit ne recalcule pas. | No persistence change expected. | `test_chart_result_service.py` included in targeted pytest and calculator scan. | PASS |
| AC7 | Le JSON public conserve les chemins requis. | No JSON projection change expected. | `test_natal_result_contract.py`, `test_chart_json_builder.py`, contract map. | PASS |
| AC8 | Les scores de dignite sont stables. | No scoring change expected. | Scoring and golden pytest coverage plus regression matrix. | PASS |
| AC9 | Les golden cases traditionnels passent. | No golden case change expected. | `test_traditional_golden_cases.py` included in targeted pytest. | PASS |
| AC10 | Limites restantes sans blocker cache. | Evidence only. | Audit report documents no remaining in-domain blocker. | PASS |
| AC11 | Aucun nouveau comportement metier n'est introduit. | Evidence/generated files only. | App-surface diff review: no production files changed. | PASS |
| AC12 | Le statut final JSON est valide. | Evidence only: final status JSON. | `python -m json.tool` passes. | PASS |
| AC13 | Les downstream facts sont stables. | No downstream code change expected. | `test_planet_condition_profile_service.py`, dominance and adapter tests included. | PASS |
| AC14 | Les golden cases de triplicite passent. | No triplicity code change expected. | `test_triplicity_golden_cases.py` included in targeted pytest. | PASS |

