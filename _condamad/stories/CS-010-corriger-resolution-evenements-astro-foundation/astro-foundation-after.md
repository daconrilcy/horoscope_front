# Astro Foundation After

## Fixed behavior

Apres CS-010, `PublicAstroFoundationPolicy` utilise `resolve_public_astro_events`, partage avec `PublicAstroDailyEventsPolicy`:

- `evidence.metadata["astro_events"]`;
- `core.events`;
- `core.detected_events`;
- `snapshot.v3_metrics["detected_events"]` pour les predictions cachees.

Les aspects dominants utilisent `PUBLIC_ASTRO_ASPECT_EVENT_TYPES`:

- `aspect`;
- `aspect_exact_to_angle`;
- `aspect_exact_to_luminary`;
- `aspect_exact_to_personal`.

## Validation

- `test_astro_foundation_reads_detected_events_from_engine_output` prouve que `detected_events` remplit `astro_foundation`.
- `test_astro_foundation_recognizes_all_exact_aspect_event_types` prouve que les trois types `aspect_exact_*` alimentent `dominant_aspects`.
- `app/tests/unit/test_public_projection.py` et `app/tests/integration/test_daily_prediction_api.py` passent, sans changement de schema public detecte.

## Difference autorisee

`astro_foundation` peut etre rempli dans des cas ou il etait auparavant vide. Aucun champ public nouveau ou supprime n'est introduit.
