# DB Session Allowlist

Exceptions temporaires restantes pour les imports directs `SessionLocal` ou `engine`
depuis `app.infra.db.session` dans les tests backend.

| File | Pattern | Reason | Exit condition |
|---|---|---|---|

Aucune exception active. Les tests backend doivent utiliser les helpers canoniques:

- `backend/app/tests/helpers/db_session.py` pour `backend/app/tests`;
- `backend/tests/integration/app_db.py` pour `backend/tests`.
