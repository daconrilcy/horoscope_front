# DB Fixture Topology - After

## Topologie cible introduite

- `backend/tests/integration/app_db.py` est le propriétaire canonique pour ouvrir une session DB effective depuis `backend/tests/integration`.
- `backend/app/tests/helpers/db_session.py` est le propriétaire canonique pour ouvrir une session DB effective depuis `backend/app/tests`.
- Les deux helpers résolvent la session au runtime via `app.infra.db.session`, après application des fixtures et du monkeypatch global existant.
- `ensure_configured_sqlite_file_matches_alembic_head` reste appelé par:
  - `backend/tests/conftest.py`
  - `backend/app/tests/integration/conftest.py`

## Lot migré

- `backend/tests/integration/test_llm_release.py`
- `backend/app/tests/integration/test_admin_content_api.py`

## Invariant protégé

`backend/app/tests/unit/test_backend_db_test_harness.py` échoue si:

- un nouveau fichier de tests importe directement `SessionLocal` ou `engine` depuis `app.infra.db.session`;
- un nouveau fichier utilise `db_session_module.SessionLocal` hors helpers canoniques et allowlist persistée;
- un nouveau `Base.metadata.create_all` apparaît hors registre classifié;
- une nouvelle factory SQLite secondaire apparaît hors registre classifié;
- un fichier de test applique `create_all` dans un contexte qui référence directement `horoscope.db`.
