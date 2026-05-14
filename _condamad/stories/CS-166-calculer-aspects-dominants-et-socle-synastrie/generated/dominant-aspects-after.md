# dominant-aspects-after.md

Story: CS-166-calculer-aspects-dominants-et-socle-synastrie
Date: 2026-05-14

Before: no canonical owner existed for this exact story surface, or the previous surface was flat/untyped.
After: DominantAspectEvaluator, contrat runtime dominant et socle calculate_interchart_aspects ajoutes.
Validation: pytest -q tests/unit/domain/astrology/test_dominant_aspects.py tests/unit/domain/astrology/test_interchart_aspects.py app/tests/unit/test_aspect_orb_overrides.py. Expanded targeted regression: 76 tests passed.
