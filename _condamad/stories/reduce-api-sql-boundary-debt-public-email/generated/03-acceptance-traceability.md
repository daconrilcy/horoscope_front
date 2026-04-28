# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `unsubscribe` n'a plus de SQL/session. | `backend/app/api/v1/routers/public/email.py` retire SQLAlchemy, `UserModel`, `get_db_session`, `db` et appels `db.*`. | OpenAPI import PASS; architecture tests PASS; scan négatif route sans hit. | PASS |
| AC2 | La persistance est hors API. | `EmailService.mark_user_unsubscribed` possède l’update SQL dans `backend/app/services/email/service.py`. | Tests d’intégration unsubscribe PASS; scan service trouve l’update dans `app/services`. | PASS |
| AC3 | L'allowlist retire les lignes `public/email.py`. | Les sept lignes `app/api/v1/routers/public/email.py` sont retirées de `router-sql-allowlist.md`. | Exact SQL allowlist guard PASS; `allowlist-diff.md` persisté. | PASS |
| AC4 | `GET /api/email/unsubscribe` conserve son comportement. | Le routeur garde le décodage token, erreurs API, HTML et no-store. | `pytest -q tests/integration/test_email_unsubscribe.py` PASS, 7 tests. | PASS |
| AC5 | Le contrat runtime de route reste stable. | Aucun changement de montage route; snapshots OpenAPI before/after créés. | Assertion OpenAPI route PASS; comparaison du chemin unsubscribe before/after PASS. | PASS |
| AC6 | Les garde-fous API existants passent. | Aucun contournement RG-006/RG-008; guard ciblé ajouté. | `pytest -q app/tests/unit/test_api_router_architecture.py` PASS, 53 tests. | PASS |
