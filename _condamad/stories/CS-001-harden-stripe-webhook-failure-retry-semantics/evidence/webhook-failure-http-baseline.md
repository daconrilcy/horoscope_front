# Baseline HTTP webhook failure

<!-- Preuve persistante avant correction: le webhook signe acquitte silencieusement un echec metier. -->

## Commande

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/integration/test_stripe_webhook_api.py::test_webhook_business_failure_persists_failed_and_retry_is_accepted
```

## Resultat observe avant implementation

- Resultat pytest: `1 passed`
- Statut HTTP verrouille par le test existant: `200`
- Corps JSON verrouille par le test existant: `{"status": "failed_internal"}`
- Ligne idempotence attendue: `status=failed`, `processing_attempts=1`, `last_error="boom"`

## Conclusion baseline

Le comportement audite est confirme: un traitement metier signe peut etre persiste en `failed` tout en etant acquitte par HTTP `200`, ce qui empeche le retry automatique Stripe.
