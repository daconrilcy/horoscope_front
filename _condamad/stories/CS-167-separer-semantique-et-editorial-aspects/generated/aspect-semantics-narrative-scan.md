# aspect-semantics-narrative-scan.md

Story: CS-167-separer-semantique-et-editorial-aspects
Date: 2026-05-14

Before: no canonical owner existed for this exact story surface, or the previous surface was flat/untyped.
After: AspectInterpretationFacts ajoute comme couche semantique pure issue des profils.
Validation: pytest -q tests/unit/domain/astrology/test_aspect_interpretation_facts.py tests/unit/domain/astrology/test_aspect_interpretation_builder.py. Expanded targeted regression: 76 tests passed.
