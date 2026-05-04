# Implementation Plan

## Initial repository findings

- `backend/app/prediction/public_projection.py` assemblait le payload public et declenchait `AIEngineAdapter.generate_horoscope_narration` avec `uuid.uuid4()`.
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py` est deja le chemin canonique vers `LLMGateway`.
- `backend/app/services/prediction/public_predictions.py` contient deja les helpers non HTTP du flux public prediction.

## Proposed changes

- Garder `PublicPredictionAssembler` deterministe: projection, application de narration persistee, aucun appel LLM.
- Ajouter `enrich_public_prediction_with_horoscope_narration` sous `services/prediction/public_predictions.py`.
- Faire appeler ce service par les routeurs public et QA apres assemblage, avec IDs de correlation issus de la requete.
- Ajouter une garde AST sur les symboles interdits dans la projection.

## Files to modify

- `backend/app/prediction/public_projection.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`
- Tests de projection, narration variant et guardrails.

## Files to delete

- None.

## Tests to add or update

- Update tests that patched the former direct `AIEngineAdapter` call.
- Add guardrail test for forbidden projection symbols.

## Risk assessment

- Main risk: payload public drift. Mitigated by before/after runtime comparison and existing projection/API tests.
- Main risk: narration no longer called. Mitigated by integration test patching `generate_horoscope_narration_via_gateway`.

## Rollback strategy

- Revert the service orchestration and route call changes as one patch if validation fails; no migration or dependency change is involved.
