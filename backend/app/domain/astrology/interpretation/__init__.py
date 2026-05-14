"""Package d'interpretation astrologique pure.

Les contrats et evaluateurs sont consommes depuis leurs modules canoniques.
"""

from importlib import import_module
from typing import Any

__all__ = [
    "AspectEditorialInterpretation",
    "AspectInterpretationBuilder",
    "AspectInterpretationFacts",
    "AspectSemanticCandidate",
    "AspectStrengthEvaluator",
    "AspectStrengthLevel",
    "AspectStrengthReason",
    "AspectStrengthRuntimeData",
    "DominantAspectEvaluator",
    "SemanticProvenance",
    "prioritize_semantic_candidates",
]

_LAZY_EXPORTS = {
    "AspectEditorialInterpretation": (
        "app.domain.astrology.interpretation.aspect_interpretation_contracts"
    ),
    "AspectInterpretationBuilder": (
        "app.domain.astrology.interpretation.aspect_interpretation_builder"
    ),
    "AspectInterpretationFacts": (
        "app.domain.astrology.interpretation.aspect_interpretation_facts"
    ),
    "AspectSemanticCandidate": ("app.domain.astrology.interpretation.aspect_semantic_provenance"),
    "AspectStrengthEvaluator": "app.domain.astrology.interpretation.aspect_strength",
    "AspectStrengthLevel": ("app.domain.astrology.interpretation.aspect_strength_contracts"),
    "AspectStrengthReason": ("app.domain.astrology.interpretation.aspect_strength_contracts"),
    "AspectStrengthRuntimeData": ("app.domain.astrology.interpretation.aspect_strength_contracts"),
    "DominantAspectEvaluator": "app.domain.astrology.interpretation.dominant_aspects",
    "SemanticProvenance": "app.domain.astrology.interpretation.aspect_semantic_provenance",
    "prioritize_semantic_candidates": (
        "app.domain.astrology.interpretation.aspect_semantic_provenance"
    ),
}


def __getattr__(name: str) -> Any:
    """Charge paresseusement les exports d'interpretation pour eviter les cycles."""
    if name not in _LAZY_EXPORTS:
        raise AttributeError(name)
    module = import_module(_LAZY_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
