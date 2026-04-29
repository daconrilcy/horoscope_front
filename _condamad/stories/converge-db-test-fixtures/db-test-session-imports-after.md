# DB Test Session Imports - After

Inventaire après migration du lot représentatif et durcissement de la garde DB.

## Commandes

```powershell
rg -n "from app\.infra\.db\.session import .*\b(SessionLocal|engine)\b|db_session_module\.SessionLocal" backend/app/tests backend/tests -g "*.py"
rg -n "Base\.metadata\.create_all" backend/app/tests backend/tests -g "*.py"
rg -n "create_engine\(|sqlite://|sqlite\+aiosqlite" backend/app/tests backend/tests -g "*.py"
```

## Résultat synthétique

| Inventory | Hits | Files | Classification |
|---|---:|---:|---|
| Direct DB session imports / `db_session_module.SessionLocal` | 165 | 109 | Helpers canoniques, garde elle-même, ou exceptions listées dans `db-session-allowlist.md`. |
| `Base.metadata.create_all` | 131 | 126 | Tous les fichiers existants sont classifiés dans `APPROVED_CREATE_ALL_PATHS`; aucune référence `horoscope.db` non approuvée. |
| Factories SQLite / URLs SQLite de test | 142 | 63 | Tous les fichiers de factory active sont classifiés dans `APPROVED_SQLITE_FACTORY_PATHS`. |

## Lot migré vérifié

| File | Before | After |
|---|---|---|
| `backend/tests/integration/test_llm_release.py` | `from app.infra.db.session import SessionLocal, get_db_session` | `from app.infra.db.session import get_db_session` + `from tests.integration.app_db import open_app_db_session` |
| `backend/app/tests/integration/test_admin_content_api.py` | `from app.infra.db.session import SessionLocal, engine` | `from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session` |

## Classifications persistées

| Category | Files |
|---|---|
| Canonical helper internals | `backend/tests/integration/app_db.py`, `backend/app/tests/helpers/db_session.py` |
| Guard self-reference | `backend/app/tests/unit/test_backend_db_test_harness.py` |
| Temporary legacy exceptions | Exact file list in `_condamad/stories/converge-db-test-fixtures/db-session-allowlist.md` |
| `create_all` classified paths | Exact set `APPROVED_CREATE_ALL_PATHS` in `backend/app/tests/unit/test_backend_db_test_harness.py` |
| SQLite factory classified paths | Exact set `APPROVED_SQLITE_FACTORY_PATHS` in `backend/app/tests/unit/test_backend_db_test_harness.py` |

## Reintroduction guard result

`pytest -q app/tests/unit/test_backend_db_test_harness.py` passe avec 4 tests:

- aucun nouveau test ne peut importer directement `SessionLocal` ou `engine` hors allowlist;
- les deux fichiers migrés restent sans import production direct;
- aucun nouveau `Base.metadata.create_all` ne peut apparaître hors classification;
- aucune nouvelle factory SQLite secondaire ne peut apparaître hors classification.
