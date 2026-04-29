# DB Fixture Topology - Before

## Topologie observée

- `backend/app/tests/conftest.py` construit une SQLite fichier temporaire sous `backend/.tmp-pytest` et remplace globalement `app.infra.db.session.engine` et `SessionLocal`.
- `backend/app/tests/integration/conftest.py` appelle `ensure_configured_sqlite_file_matches_alembic_head(...)`, puis applique un `Base.metadata.create_all(bind=engine)` borné à la SQLite secondaire de test.
- `backend/tests/conftest.py` appelle `ensure_configured_sqlite_file_matches_alembic_head()` en fixture session autouse après collecte.
- `backend/tests/integration/app_db.py` expose déjà `app_engine()` et `open_app_db_session()`, mais le lot `test_llm_release.py` importait encore `SessionLocal` directement.

## Risques

- Les tests peuvent dépendre d'import-time rewiring plutôt que d'un propriétaire DB explicite.
- Les nouveaux tests peuvent augmenter la dette sans garde.
- L'alignement Alembic doit rester propriétaire du schéma SQLite de test.
