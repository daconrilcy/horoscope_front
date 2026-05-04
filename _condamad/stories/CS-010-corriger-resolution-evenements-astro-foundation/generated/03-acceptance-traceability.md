# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `detected_events` alimente `astro_foundation`. | `PublicAstroFoundationPolicy` utilise `resolve_public_astro_events`, qui lit `core.events` puis `core.detected_events`. | `pytest -q tests/unit/prediction/test_public_astro_foundation.py` passe avec `test_astro_foundation_reads_detected_events_from_engine_output`. | PASS |
| AC2 | Les aspects exacts sont reconnus. | `PUBLIC_ASTRO_ASPECT_EVENT_TYPES` centralise `aspect` et les trois `aspect_exact_*`; la fondation l'utilise pour `dominant_aspects`. | `pytest -q tests/unit/prediction/test_public_astro_foundation.py` passe avec `test_astro_foundation_recognizes_all_exact_aspect_event_types`. | PASS |
| AC3 | Le schema public reste stable. | Aucun champ public n'est ajoute ou supprime; seule la source de remplissage de `astro_foundation` change. | `pytest -q app/tests/unit/test_public_projection.py` et `pytest -q app/tests/integration/test_daily_prediction_api.py` passent. | PASS |
| AC4 | Les preuves du bugfix sont persistees. | Les artefacts avant/apres documentent le drift et le comportement corrige. | `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-before.md` et `astro-foundation-after.md` existent. | PASS |
