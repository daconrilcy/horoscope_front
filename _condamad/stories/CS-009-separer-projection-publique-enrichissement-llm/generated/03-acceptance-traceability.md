# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | La projection publique ne depend plus du runtime LLM. | `backend/app/prediction/public_projection.py` ne lit plus `settings`, ne genere plus d'ID et n'importe plus `AIEngineAdapter`; `backend/app/tests/unit/test_daily_prediction_guardrails.py` verrouille l'invariant. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`; scan `rg -n "AIEngineAdapter\|uuid\\.uuid4\\(\|settings\|Session" app/prediction/public_projection.py`. | PASS |
| AC2 | Le payload public reste stable. | L'assembleur conserve les memes champs publics; l'enrichissement narratif agit apres projection. | `pytest -q app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py app/tests/integration/test_daily_prediction_api.py`; artefacts before/after. | PASS |
| AC3 | La narration passe par le service canonique. | `backend/app/services/prediction/public_predictions.py` appelle `generate_horoscope_narration_via_gateway`; routeurs public et QA lui transmettent `request_id`/`trace_id`. | `pytest -q app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/integration/test_horoscope_daily_variant_narration.py`. | PASS |
| AC4 | Les exceptions restantes sont exactes. | `projection-exceptions.md` limite l'exception restante aux helpers deterministes de projection. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`; `projection-exceptions.md`. | PASS |
| AC5 | Les snapshots avant apres sont conserves. | `public-payload-before.md` et `public-payload-after.md` documentent la comparaison runtime. | Execution runtime de l'ancien assembleur depuis `git show HEAD:...` et de l'assembleur courant sur le meme snapshot; resultat `same: true`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
