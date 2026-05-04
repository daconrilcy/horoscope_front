# Evidence apres implementation

## Etat cible

- La source canonique reste `app.core.request_id`.
- La projection publique ne genere aucun ID local.
- La narration horoscope recoit les IDs fournis par le chemin appelant.
- Le payload public n'ajoute aucun champ de correlation.

## Preuves code

- `backend/app/tests/unit/test_daily_prediction_service.py` ajoute `test_horoscope_narration_receives_caller_correlation_ids`.
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` ajoute `test_public_projection_does_not_generate_local_correlation_ids`.
- `backend/app/prediction/public_projection.py` reste sans `uuid.uuid4()`, `request_id = str(` ou `trace_id = str(`.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_request_id.py app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_public_projection.py app/tests/unit/test_daily_prediction_guardrails.py
rg -n "uuid\.uuid4\(|request_id = str\(|trace_id = str\(" app/prediction/public_projection.py
```
