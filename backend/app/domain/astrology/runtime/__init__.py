"""Contrats runtime riches pour les objets astrologiques calculés."""

from importlib import import_module
from typing import Any

from app.domain.astrology.runtime.house_runtime_data import (
    HouseAxisRuntimeData,
    HouseOccupantRuntimeData,
    HouseRulerRuntimeData,
    HouseRuntimeData,
    HouseStrengthRuntimeData,
    resolve_house_kind,
)
from app.domain.astrology.runtime.runtime_reference import (
    AnglePointReferenceData,
    AnglePointReferenceSet,
    AspectOrbRuleReferenceData,
    AspectReferenceData,
    AspectReferenceSet,
    AstrologyRuntimeReference,
    AstrologySystemReferenceData,
    AstrologySystemReferenceSet,
    DignityReferenceData,
    DignityReferenceSet,
    HouseAxisReferenceData,
    HouseReferenceData,
    HouseReferenceSet,
    HouseSystemReferenceData,
    HouseSystemReferenceSet,
    PlanetReferenceData,
    PlanetReferenceSet,
    SignReferenceData,
    SignReferenceSet,
)

__all__ = [
    "AspectIdentityRuntimeData",
    "AspectInterpretationRuntimeData",
    "AspectMetadataRuntimeData",
    "AspectModifierRuntimeData",
    "AspectModifierType",
    "AspectOrbRuntimeData",
    "AspectParticipantsRuntimeData",
    "AspectPhaseRuntimeData",
    "AspectRuntimeData",
    "AspectRuntimeWeightTaxonomy",
    "AnglePointReferenceData",
    "AnglePointReferenceSet",
    "AspectOrbRuleReferenceData",
    "AspectReferenceData",
    "AspectReferenceSet",
    "AstrologyRuntimeReference",
    "AstrologySystemReferenceData",
    "AstrologySystemReferenceSet",
    "AstrologicalGraphEdgeType",
    "AstrologicalGraphNodeType",
    "DominantAspectReason",
    "DominantAspectRuntimeData",
    "DignityReferenceData",
    "DignityReferenceSet",
    "HouseAxisRuntimeData",
    "HouseAxisReferenceData",
    "HouseOccupantRuntimeData",
    "HouseReferenceData",
    "HouseReferenceSet",
    "HouseRulerRuntimeData",
    "HouseRuntimeData",
    "HouseSystemReferenceData",
    "HouseSystemReferenceSet",
    "HouseStrengthRuntimeData",
    "PatternGraphEdge",
    "PatternGraphNode",
    "PatternRuntimeData",
    "PatternType",
    "PlanetReferenceData",
    "PlanetReferenceSet",
    "SignReferenceData",
    "SignReferenceSet",
    "resolve_house_kind",
]

_LAZY_EXPORTS = {
    "AspectIdentityRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectInterpretationRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectMetadataRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectModifierRuntimeData": "app.domain.astrology.runtime.aspect_modifiers",
    "AspectModifierType": "app.domain.astrology.runtime.aspect_modifiers",
    "AspectOrbRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectParticipantsRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectPhaseRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectRuntimeWeightTaxonomy": "app.domain.astrology.runtime.aspect_modifiers",
    "AstrologicalGraphEdgeType": "app.domain.astrology.runtime.astrological_graph_contracts",
    "AstrologicalGraphNodeType": "app.domain.astrology.runtime.astrological_graph_contracts",
    "DominantAspectReason": "app.domain.astrology.runtime.dominant_aspect_runtime_data",
    "DominantAspectRuntimeData": "app.domain.astrology.runtime.dominant_aspect_runtime_data",
    "PatternGraphEdge": "app.domain.astrology.runtime.pattern_runtime_data",
    "PatternGraphNode": "app.domain.astrology.runtime.pattern_runtime_data",
    "PatternRuntimeData": "app.domain.astrology.runtime.pattern_runtime_data",
    "PatternType": "app.domain.astrology.runtime.pattern_runtime_data",
}


def __getattr__(name: str) -> Any:
    """Charge paresseusement les exports runtime pour eviter les cycles."""
    if name not in _LAZY_EXPORTS:
        raise AttributeError(name)
    module = import_module(_LAZY_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
