# aspect-modifiers-after.md

Story: CS-168-canonicaliser-modifiers-et-poids-aspects
Date: 2026-05-14

Before: no canonical owner existed for this exact story surface, or the previous surface was flat/untyped.
After: AspectModifierRuntimeData, AspectModifierType et taxonomie des poids ajoutes.
Validation: pytest -q tests/unit/domain/astrology/test_aspect_modifiers.py app/tests/unit/test_astrology_prediction_boundary.py. Expanded targeted regression: 76 tests passed.
