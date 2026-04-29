# No Legacy / DRY Guardrails

## Canonical ownership

- `backend/tests/integration/app_db.py` is the canonical helper for integration tests under `backend/tests/integration/` that need the effective application DB session.
- `backend/app/tests/helpers/db_session.py` is the canonical helper for tests under `backend/app/tests/` that need the globally patched app-test DB session.
- `ensure_configured_sqlite_file_matches_alembic_head` remains the owner of SQLite/Alembic alignment.

## Forbidden patterns

- New direct imports of `SessionLocal` or `engine` from `app.infra.db.session` in backend tests.
- New test files using `db_session_module.SessionLocal` outside canonical helper/fixture owners.
- New `Base.metadata.create_all` against `backend/horoscope.db`.
- Compatibility aliases or re-export modules that hide production `SessionLocal`.

## Allowed temporary exceptions

- Existing files listed in `_condamad/stories/converge-db-test-fixtures/db-session-allowlist.md`.
- Existing global monkeypatch in `backend/app/tests/conftest.py`, because the story explicitly keeps full removal out of scope.

## Required evidence

- Before/after import inventory.
- AST guard test.
- Targeted migrated tests.
- SQLite alignment test.
