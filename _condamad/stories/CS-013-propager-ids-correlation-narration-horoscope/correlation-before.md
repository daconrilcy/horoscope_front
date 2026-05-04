# Baseline avant implementation

## Etat observe au preflight

Au demarrage de cette execution, le workspace contenait deja un chemin applicatif converge:

- `backend/app/api/v1/routers/public/predictions.py` appelait deja `resolve_request_id(request)` et `resolve_trace_id(request, fallback=request_id)`.
- `backend/app/services/prediction/public_predictions.py` acceptait deja `request_id` et `trace_id` en parametres explicites.
- `backend/app/prediction/public_projection.py` ne contenait deja plus `uuid.uuid4()`.

## Commande d'inspection

```powershell
rg -n "uuid|request_id = str|trace_id = str|generate_horoscope_narration|enrich_public_prediction_with_horoscope_narration|resolve_request_id|resolve_trace_id" backend/app/prediction/public_projection.py backend/app/services/prediction backend/app/api/v1/routers/public/predictions.py
```

## Resultat utile

Les seuls hits de correlation etaient:

- `backend/app/api/v1/routers/public/predictions.py`: imports `resolve_request_id`, `resolve_trace_id`, resolution des IDs, puis appel de `enrich_public_prediction_with_horoscope_narration`.
- `backend/app/services/prediction/public_predictions.py`: signature avec `request_id` et `trace_id`, puis appel de `generate_horoscope_narration_via_gateway`.

Cette baseline classe le travail restant comme durcissement de preuve: tests de propagation, garde anti-retour et evidence CONDAMAD.
