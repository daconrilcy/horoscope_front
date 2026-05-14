"""Tests des exports publics canoniques astrology."""


def test_runtime_public_exports_are_importable() -> None:
    """Les symboles runtime annonces par `__all__` sont importables."""
    from app.domain.astrology.runtime import (
        AspectModifierRuntimeData,
        AspectRuntimeData,
        DominantAspectRuntimeData,
        PatternRuntimeData,
    )

    assert AspectRuntimeData.__name__ == "AspectRuntimeData"
    assert AspectModifierRuntimeData.__name__ == "AspectModifierRuntimeData"
    assert DominantAspectRuntimeData.__name__ == "DominantAspectRuntimeData"
    assert PatternRuntimeData.__name__ == "PatternRuntimeData"


def test_interpretation_public_exports_are_importable() -> None:
    """Les symboles interpretation annonces par `__all__` sont importables."""
    from app.domain.astrology.interpretation import (
        AspectInterpretationBuilder,
        AspectInterpretationFacts,
        AspectStrengthEvaluator,
        SemanticProvenance,
    )

    assert AspectStrengthEvaluator.__name__ == "AspectStrengthEvaluator"
    assert AspectInterpretationFacts.__name__ == "AspectInterpretationFacts"
    assert AspectInterpretationBuilder.__name__ == "AspectInterpretationBuilder"
    assert SemanticProvenance.__name__ == "SemanticProvenance"
