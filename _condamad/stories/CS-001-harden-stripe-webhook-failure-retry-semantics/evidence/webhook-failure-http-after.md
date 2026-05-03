# After HTTP webhook failure

<!-- Preuve persistante apres correction: le webhook signe demande un retry Stripe. -->

## Commande

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_idempotency_service.py app/tests/integration/test_stripe_webhook_api.py
```

## Resultat observe apres implementation

- Resultat pytest: `36 passed`
- Premier traitement metier signe en erreur: HTTP `500`
- Code d'erreur API: `stripe_webhook_processing_failed`
- Ligne idempotence conservee: `status=failed`, `processing_attempts=1`, `last_error="boom"`
- Redelivery du meme `event.id`: HTTP `200`, corps `{"status": "processed"}`
- Ligne idempotence apres redelivery: `status=processed`, `processing_attempts=2`, `last_error=NULL`

## Comparaison avec baseline

Seul le cas d'echec de traitement apres signature valide passe de HTTP `200` a HTTP `500` retryable. Les succes, doublons, evenements ignores, signatures invalides et absence de secret conservent leurs contrats existants.
