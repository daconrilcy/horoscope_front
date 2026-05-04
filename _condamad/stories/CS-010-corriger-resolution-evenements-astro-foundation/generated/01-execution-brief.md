# Execution Brief - CS-010

## Primary objective

Corriger `PublicAstroFoundationPolicy` pour que `astro_foundation` soit alimente depuis les sources canoniques `events` puis `detected_events`, avec reconnaissance des types `aspect_exact_to_angle`, `aspect_exact_to_luminary` et `aspect_exact_to_personal`.

## Boundaries

- Modifier uniquement la projection publique prediction et ses tests.
- Preserver le schema JSON public: aucun champ ajoute, renomme ou supprime.
- Reutiliser la resolution et la taxonomie d'evenements de `public_astro_daily_events.py`.
- Ne pas toucher au runtime LLM ni aux invariants RG-016 a RG-019.

## Done conditions

- AC1 a AC4 ont une preuve de code et une preuve de validation.
- Les artefacts `astro-foundation-before.md` et `astro-foundation-after.md` existent.
- Les tests ciblés et le lint Ruff passent.
- Le registre `_condamad/stories/story-status.md` est synchronise en `ready-to-review`.

## Halt conditions

- Les sources runtime ne sont pas `events` ou `detected_events`.
- La correction necessite un changement de schema public.
- Une validation ciblee CS-010 echoue sans correction sure.
