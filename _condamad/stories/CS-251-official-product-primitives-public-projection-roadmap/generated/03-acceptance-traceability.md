# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Official primitives are documented. | `docs/architecture/official-product-primitives-public-projections.md`; `evidence/product-primitives.json`. | `rg -n "structured facts\|beginner summary\|expert technical projection\|fixed-star contacts\|LLM input" docs/architecture`; `python -B -m pytest -q backend/tests/architecture/test_api_contract_neutrality.py`. | PASS |
| AC2 | Every CS-244 audience is mapped. | Audience mapping table in official roadmap; JSON audiences for beginner, expert, astrologer, debug, AI, PDF, public-user. | `python -B -m pytest -q backend/tests/architecture/test_api_contract_neutrality.py`; full `python -B -m pytest -q`. | PASS |
| AC3 | Internal surfaces are rejected. | Roadmap non-public surface table; expanded public contract guard. | `python -B -m pytest -q backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`. | PASS |
| AC4 | Fixed-star exposure policy is explicit. | `fixed_star_contacts` is `needs-user-decision`; CS-257 consequence recorded. | `rg -n "API contract\|frontend client\|UI component\|needs-user-decision" docs/architecture/official-product-primitives-public-projections.md`; architecture test. | PASS |
| AC5 | Roadmap splits implementation layers. | Roadmap rows split `API contract`, `frontend client`, and `UI component`. | `rg -n "API contract\|frontend client\|UI component\|needs-user-decision" docs/architecture/official-product-primitives-public-projections.md`. | PASS |
| AC6 | Public projection remains OpenAPI-ready. | OpenAPI/route checks added to API neutrality test; `evidence/openapi-routes.md` persisted. | `python -B -m pytest -q backend/tests/architecture/test_api_contract_neutrality.py`; Python `app.openapi()` and `app.routes` checks. | PASS |
| AC7 | Raw runtime exposure cannot reappear. | Public contract and architecture guards reject raw runtime names. | `python -B -m pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`; full pytest. | PASS |
| AC8 | Evidence artifacts are persisted. | `evidence/product-primitives.json`, `evidence/openapi-routes.md`, `evidence/validation.txt`, generated traceability/final evidence. | `python -B -c "from pathlib import Path; assert Path(...).exists()"`; capsule validation. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
