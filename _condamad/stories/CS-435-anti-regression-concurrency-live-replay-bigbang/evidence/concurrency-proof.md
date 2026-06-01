# Concurrency proof

Status: PASS

Preuve runtime:

- Test: `python -B -m pytest -q backend\tests\integration\test_theme_natal_concurrency.py --tb=short`
- Resultat observe pendant validation ciblee: inclus dans `8 passed, 5 deselected`.

Scenario `generate_full`:

- Deux demandes logiques utilisent la meme `ThemeNatalReadingSlotKey`.
- Les deux runs techniques pointent vers un seul slot public.
- La premiere publication retourne `accepted_now=True`.
- La seconde publication retourne `accepted_now=False`.
- Le payload public conserve la premiere lecture acceptee.
- `ThemeNatalReadingSlotService.consume_quota_after_publication` debite une seule fois.

Preuve verrou applicatif:

- `test_slot_claim_section_is_serialized_for_simultaneous_generate_full` lance deux claims en `ThreadPoolExecutor`.
- Le compteur `max_active_claims` reste a `1`, donc la section critique de claim est serialisee.

AC couverts: AC5, AC14.
