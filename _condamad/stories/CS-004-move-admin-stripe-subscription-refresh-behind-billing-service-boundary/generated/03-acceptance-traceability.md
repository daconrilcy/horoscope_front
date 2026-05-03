# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | La route admin refresh reste exposee avec reponse succes stable. | Route `users.py` conserve le chemin, l'autorisation et `{"status": "success"}`. | `pytest -q app/tests/integration/test_admin_stripe_actions_api.py` + OpenAPI command passed. | PASS |
| AC2 | Aucun routeur API n'appelle directement le client Stripe SDK. | Suppression de l'import `get_stripe_client` et des appels `stripe_client.*` depuis `backend/app/api/v1/routers`. | AST guard passed + direct Stripe router scan returned zero hits. | PASS |
| AC3 | Le refresh force est orchestre par un service billing/admin. | `StripeBillingProfileService.force_admin_subscription_refresh` owns retrieve, synthetic event, sync and audit. | `pytest -q app/tests/unit/test_stripe_billing_profile_service.py` passed. | PASS |
| AC4 | Les erreurs existantes restent mappees avec statuts/messages equivalents. | Route traduit les erreurs service en 400/503 sans FastAPI dans le service et garde 500 generique. | Admin integration error tests passed. | PASS |
| AC5 | Les couches billing/infra ne dependent pas de `app.api` ni de FastAPI. | Service billing n'importe ni FastAPI ni `app.api`; route seule traduit HTTP. | Service architecture guard + service/infra dependency scan passed. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
