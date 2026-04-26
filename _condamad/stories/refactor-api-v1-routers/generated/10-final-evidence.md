# Final Evidence — refactor-api-v1-routers

## Story Status

- Validation outcome: PASS
- Ready for review: yes
- Story key: refactor-api-v1-routers
- Source story: `_condamad/stories/refactor-api-v1-routers/00-story.md`
- Capsule path: `_condamad/stories/refactor-api-v1-routers`

## Summary

- Routers API v1 classes sous `admin`, `admin/llm`, `b2b`, `ops`, `public`, et `internal/llm`.
- Schemas extraits sous `backend/app/api/v1/schemas/routers`.
- Helpers prives/non-HTTP extraits sous `backend/app/api/v1/router_logic`.
- Aucun endpoint HTTP supprime; seuls les anciens chemins Python plats ont ete retires.
- Tests mis a jour pour patcher les modules canoniques (`router_logic` ou `schemas`) au lieu des routeurs.

## AC Validation

| AC | Status | Evidence |
|---|---|---|
| AC1 | PASS | `_condamad/stories/refactor-api-v1-routers/router-audit.md` contient l inventaire route-par-route avec prefixes, endpoints, schemas, helpers, refs backend/frontend et decision. |
| AC2 | PASS | `backend/app/main.py` et les tests utilisent les packages canoniques; garde `test_router_modules_are_classified_under_domain_packages`. |
| AC3 | PASS | Plus de wrappers plats; `routers/__init__.py` ne re-exporte pas les routeurs; negative import tests verts. |
| AC4 | PASS | `rg -n "class .*\(BaseModel\)" backend/app/api/v1/routers --glob "*.py"` ne retourne aucun schema actif. |
| AC5 | PASS | `rg -n "^def _|^async def _" backend/app/api/v1/routers --glob "*.py"` ne retourne aucun helper prive; garde architecture ajoutee. |
| AC6 | NOT_APPLICABLE | Aucun endpoint HTTP n a ete supprime; l audit documente la preservation explicite. |
| AC7 | PASS | `test_api_v1_router_contracts.py` valide les routes conservees et OpenAPI. |
| AC8 | PASS | Ruff, tests cibles, `app/tests/integration`, et `tests/integration` passent dans le venv. |

## Validation Commands

| Command | Working directory | Result |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .` | repo root | PASS: `1218 files already formatted` |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS: `All checks passed!` |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/integration/test_api_v1_router_contracts.py tests/integration/test_admin_llm_catalog.py tests/unit/test_admin_manual_execute_response.py tests/integration/test_llm_release.py::test_activation_evidence_requires_timezone_aware_datetime` | repo root | PASS: `44 passed` |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration` | repo root | PASS: `908 passed, 2 skipped` |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/integration` | repo root | PASS: `185 passed, 9 skipped` |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | PASS: `3077 passed, 12 skipped` |
| `rg -n "^class " backend/app/api/v1/routers --glob "*.py"` | repo root | PASS_WITH_ALLOWED_ENUM: only `admin/llm/error_codes.py:AdminLlmErrorCode` remains. |
| `rg -n "^def _|^async def _|^class .*\(.*BaseModel" backend/app/api/v1/routers --glob "*.py"` | repo root | PASS: no matches. |

## Files Added Or Significantly Changed

- `backend/app/api/v1/routers/**`: canonical router domain packages.
- `backend/app/api/v1/schemas/routers/**`: extracted Pydantic/API schema modules.
- `backend/app/api/v1/router_logic/**`: extracted route support logic and private helpers.
- `backend/app/main.py`: imports canonical router modules.
- `backend/app/tests/unit/test_api_router_architecture.py`: guards canonical domains, no wrappers, no router schemas, no private helpers.
- `backend/app/tests/integration/test_api_v1_router_contracts.py`: OpenAPI/route preservation guard.
- `backend/docs/llm-db-cleanup-registry.json`: allowlist updated for canonical moved LLM admin paths.
- `_condamad/stories/refactor-api-v1-routers/router-audit.md`: route-by-route audit.

## Remaining Notes

- `backend/horoscope.db` was already dirty before this work and remains unrelated to the router refactor.
- `_condamad/` contains story artifacts and may be untracked depending on the local git state.
- No dependency changes were made.
