# Evidence Log

| ID | Evidence type | Command / Source | Result | Notes |
|---|---|---|---|---|
| E-001 | target-inventory | `rg --files backend\app\api` | PASS | 65 fichiers API inspectables dans le périmètre `backend/app/api`, dont le nouveau registre `route_exceptions.py`. |
| E-002 | guardrail-registry | `_condamad/stories/regression-guardrails.md` | PASS | `RG-007` protège le propriétaire unique LLM observability; `RG-008` protège les exceptions de montage et l'allowlist SQL. |
| E-003 | dependency-direction-scan | `rg -n "from app\.api\|import app\.api" backend\app\services backend\app\domain backend\app\infra backend\app\core` | PASS | Aucun import de `app.api` depuis `services`, `domain`, `infra` ou `core`. |
| E-004 | framework-leak-scan | `rg -n "fastapi\|HTTPException\|JSONResponse" backend\app\domain backend\app\services` | PASS | Aucun type HTTP FastAPI détecté dans `domain` ou `services`. |
| E-005 | runtime-openapi-contract | `.\.venv\Scripts\Activate.ps1; cd backend; python -B -` importing `app.main.app.openapi()` | PASS | OpenAPI runtime généré avec 192 paths. Les quatre routes admin LLM observability sont exposées par `app.api.v1.routers.admin.llm.observability`. |
| E-006 | duplicate-route-owner-scan | `rg -n "list_call_logs\|get_dashboard\|replay_request\|purge_logs" backend\app\api\v1\routers\admin\llm` | PASS | Les handlers observability existent uniquement dans `observability.py`; aucun handler équivalent n'est redéfini dans `prompts.py`. |
| E-007 | route-registration-inventory | AST read-only script over `backend/app/api/v1/routers`, `registry.py`, `main.py`, `route_exceptions.py` | PASS | 49 modules routeurs avec `router = APIRouter`; tous sont référencés par le registre v1 ou par le registre d'exceptions. |
| E-008 | structured-exception-register | `Get-Content backend\app\api\route_exceptions.py` | PASS | 7 exceptions de montage déclarées: health, public email unsubscribe et 5 routes QA internes conditionnelles. |
| E-009 | sql-boundary-allowlist | `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` | FAIL | 848 entrées SQL/session/API dependency directes restent actives et sont allowlistées avec reason/decision. |
| E-010 | architecture-tests | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py` | PASS | 52 tests passés; inclut propriétaire LLM observability, exceptions de montage, direction de dépendance et allowlist SQL exacte. |
| E-011 | integration-contract-tests | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_admin_llm_config_api.py app/tests/integration/test_api_v1_router_contracts.py app/tests/integration/test_api_openapi_contract.py` | PASS | 11 tests passés; couvre OpenAPI, routes déplacées et endpoints admin LLM. |
| E-012 | legacy-route-surface | `backend/app/api/route_exceptions.py` | FAIL | `/api/email/unsubscribe` reste une URL publique historique hors préfixe `/v1`, explicitement conservée jusqu'à story de migration dédiée. |
