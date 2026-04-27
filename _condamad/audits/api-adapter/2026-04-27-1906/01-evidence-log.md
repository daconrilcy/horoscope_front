# Evidence Log

| ID | Evidence type | Command / Source | Result | Notes |
|---|---|---|---|---|
| E-001 | target-inventory | `rg --files backend\app\api` | PASS | 64 fichiers API inspectables dans le périmètre `backend/app/api`. |
| E-002 | dependency-direction-scan | `rg -n "from app\.api\|import app\.api" backend\app\services backend\app\domain` | PASS | Aucun import de `app.api` depuis `services` ou `domain`. |
| E-003 | framework-leak-scan | `rg -n "fastapi\|HTTPException\|JSONResponse" backend\app\domain backend\app\services` | PASS | Aucun type HTTP FastAPI détecté dans `domain` ou `services`. |
| E-004 | router-source-inventory | `rg -n "router = APIRouter" backend\app\api\v1\routers` | FAIL | 49 modules routeurs détectés, dont `admin/llm/observability.py` hors registre et hors `main.py`. |
| E-005 | runtime-openapi-contract | `.\.venv\Scripts\Activate.ps1; cd backend; python -B -` importing `app.main.app.openapi()` | PASS | OpenAPI runtime généré avec 192 paths. Les routes `/v1/admin/llm/call-logs`, `/dashboard`, `/replay`, `/call-logs/purge` sont exposées. |
| E-006 | duplicate-route-owner-scan | `rg -n "call-logs\|dashboard\|replay\|purge" backend\app\api\v1\routers\admin\llm\prompts.py backend\app\api\v1\routers\admin\llm\observability.py` | FAIL | Les mêmes endpoints d'observabilité existent dans `prompts.py` et `observability.py`; le runtime monte ceux de `prompts.py`. |
| E-007 | direct-db-scan | AST read-only script over `backend/app/api/v1/routers` for `db.execute`, `db.commit`, `db.add`, `db.flush`, `db.refresh` | FAIL | 39 fichiers routeurs contiennent des opérations DB directes. Exemples: `admin/llm/prompts.py` 40 hits, `admin/content.py` 25 hits, `ops/entitlement_mutation_audits.py` 20 hits. |
| E-008 | infra-import-scan | `rg -n "from app\.infra\.db\.models\|from app\.infra\.db\.session\|from sqlalchemy" backend\app\api\v1\routers backend\app\api\dependencies` | FAIL | Les routers importent largement SQLAlchemy, modèles DB et session infra. |
| E-009 | main-registration-source | `rg -n "app\.include_router\|include_api_v1_routers\|email_router\|internal_llm_qa_router" backend\app\main.py backend\app\tests\unit\test_api_router_architecture.py` | FAIL | `main.py` monte `health_router`, le registre v1, `email_router` et le routeur interne conditionnel; le test autorise explicitement ces exceptions. |
| E-010 | error-guard-inventory | `Get-Content backend\app\tests\unit\test_api_error_architecture.py` | PASS | Gardes présentes contre `HTTPException`, ancien module d'erreurs API et enveloppes d'erreur JSONResponse dans les routeurs. |
| E-011 | architecture-guard-inventory | `Get-Content backend\app\tests\unit\test_api_router_architecture.py` | LIMITATION | Gardes de registre et d'import présentes, mais aucune garde équivalente n'interdit la persistance directe dans les routeurs. |
| E-012 | legacy-negative-scan | `rg -n "legacy\|deprecated\|compat\|shim\|alias\|fallback" backend\app\api backend\app\tests backend\tests` | FAIL | Des surfaces legacy existent dans les tests et la transition LLM; le signal pertinent API est la coexistence `prompts.py` et `observability.py`. |
