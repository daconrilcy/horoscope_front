# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le client central applique une politique reseau Stripe explicite. | `Settings` expose `stripe_timeout_seconds` et `stripe_max_network_retries`; `get_stripe_client` les passe au SDK et cache par politique effective. | `pytest -q app/tests/unit/test_stripe_client.py` + full `pytest -q` passes. | PASS |
| AC2 | La politique reseau Stripe reste centralisee hors consommateurs. | Garde AST dans `test_stripe_client.py`; aucun timeout/retry Stripe dans services/API/startup. | `pytest -q app/tests/unit/test_stripe_client.py` + scan ownership Stripe classifiant uniquement infra Stripe et faux positifs LLM. | PASS |
| AC3 | Les use cases de session Stripe conservent leurs mappings d'erreur. | Tests timeout checkout et portal ajoutés; mapping `stripe_api_error` conserve. | Tests ciblés et full `pytest -q` passent. | PASS |
| AC4 | Les hydrations Stripe transitoires ont une decision testee. | Tests startup warn fail-open/strict fail-closed; webhook upgrade hydration fail-closed retryable; admin refresh mappe `StripeError`. | Tests ciblés et full `pytest -q` passent. | PASS |
| AC5 | La documentation operateur suit la source config. | `.env.example` documente les variables configurables; `RG-025` ajoute l'invariant durable. | `pytest -q app/tests/unit/test_stripe_client.py`, scan env/docs/settings et full `pytest -q` passent. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
