# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | La source canonique des IDs est documentee. | `correlation-source.md` documente `app.core.request_id`; le routeur public utilise `resolve_request_id` et `resolve_trace_id`. | `pytest -q app/tests/unit/test_request_id.py` PASS | Passed |
| AC2 | Les IDs sont transmis au service narration. | `test_horoscope_narration_receives_caller_correlation_ids` prouve la transmission a `generate_horoscope_narration_via_gateway`. | `pytest -q app/tests/unit/test_daily_prediction_service.py` PASS | Passed |
| AC3 | La projection ne genere plus d'UUID. | `public_projection.py` reste sans generation locale; garde ajoutee. | `rg -n "uuid\\.uuid4\\(|request_id = str\\(|trace_id = str\\(" app/prediction/public_projection.py` zero hit | Passed |
| AC4 | Le payload public reste stable. | Aucun champ public ajoute; tests projection et integration daily prediction passent. | `pytest -q app/tests/unit/test_public_projection.py`; `pytest -q app/tests/integration/test_daily_prediction_api.py` PASS | Passed |
| AC5 | La garde anti-retour est executable. | `test_public_projection_does_not_generate_local_correlation_ids` ajoute la garde. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` PASS | Passed |
