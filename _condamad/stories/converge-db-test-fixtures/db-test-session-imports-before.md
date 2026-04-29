# DB Test Session Imports - Before

Baseline capturé avant migration du lot représentatif avec:

```powershell
rg -n "from app\.infra\.db\.session import .*\b(SessionLocal|engine)\b|db_session_module\.SessionLocal" backend/app/tests backend/tests -g "*.py"
```

## Résumé

- Imports production directs présents dans `backend/app/tests`, `backend/tests/integration`, `backend/tests/unit` et `backend/tests/evaluation`.
- Le lot représentatif contenait:
  - `backend/tests/integration/test_llm_release.py:35` avec `SessionLocal`.
  - `backend/app/tests/integration/test_admin_content_api.py:13` avec `SessionLocal, engine`.
- Les helpers canoniques étaient incomplets:
  - `backend/tests/integration/app_db.py` existait mais n'était pas utilisé par `test_llm_release.py`.
  - Aucun helper équivalent n'existait sous `backend/app/tests/helpers/`.

## Classification

- Dette hors scope immédiat: les fichiers listés dans `db-session-allowlist.md`.
- Lot à migrer dans cette story: `test_llm_release.py`, `test_admin_content_api.py`.
- Owner canonique ciblé: `tests/integration/app_db.py` et `app/tests/helpers/db_session.py`.
