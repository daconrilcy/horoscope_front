# Implementation Plan

## Current Findings

- `app.core.request_id` est le standard existant pour `request_id` et `trace_id`.
- Le routeur public daily prediction resout deja les IDs depuis la requete.
- `public_predictions.enrich_public_prediction_with_horoscope_narration` transmet deja les IDs au service de narration.
- `public_projection.py` ne contient deja plus de generation locale d'UUID.

## Selected Approach

- Ne pas re-ecrire le chemin applicatif deja converge.
- Ajouter une preuve runtime unitaire sur la propagation vers la narration.
- Ajouter une garde explicite contre le retour de generation locale dans `public_projection.py`.
- Completer les artefacts CONDAMAD de source, baseline et evidence.

## Files to Modify

- `backend/app/tests/unit/test_daily_prediction_service.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/**`
- `_condamad/stories/story-status.md`

## No Legacy Stance

- Aucun fallback UUID local n'est ajoute.
- Aucun shim, alias ou wrapper n'est ajoute.
- La projection publique reste hors runtime LLM et hors ownership correlation.

## Rollback

- Retirer les deux tests ajoutes et les artefacts de preuve CS-013; aucun changement applicatif runtime n'est necessaire.
