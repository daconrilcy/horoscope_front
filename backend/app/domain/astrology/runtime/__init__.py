"""Contrats runtime riches pour les objets astrologiques calculés."""

from importlib import import_module
from typing import Any

from app.domain.astrology.runtime.chart_signature_runtime_data import (
    BalanceScoreRuntimeData,
    ChartBalanceRuntimeData,
    ChartSignatureRuntimeData,
    DominanceRankRuntimeData,
)
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
    PlanetNatureReferenceData,
    PlanetNatureReferenceSet,
    PlanetReferenceData,
    PlanetReferenceSet,
    SignReferenceData,
    SignReferenceSet,
)
from app.domain.astrology.runtime.sign_runtime_data import (
    SignDignityRuntimeData,
    SignDominanceReason,
    SignOccupantRuntimeData,
    SignRuntimeData,
)

__all__ = [
    "AspectIdentityRuntimeData",
    "AspectInterpretiveHintsRuntimeData",
    "AspectInterpretiveHintResolver",
    "AspectMetadataRuntimeData",
    "AspectModifierRuntimeData",
    "AspectModifierType",
    "AspectOrbRuntimeData",
    "AspectParticipantsRuntimeData",
    "AspectPhaseRuntimeData",
    "AspectRuntimeData",
    "AspectRuntimeWeightTaxonomy",
    "AspectStructuralRuntimeData",
    "AspectStructuralModifierRuntimeData",
    "resolve_aspect_interpretive_hints",
    "AstrologyDoctrineGovernanceEntry",
    "AstrologyDoctrineGovernanceError",
    "CanonicalRuleOwner",
    "DoctrineDecisionStatus",
    "RuleSourceOwnerStatus",
    "SchoolPolicy",
    "VersionPolicy",
    "build_astrology_doctrine_governance",
    "get_astrology_doctrine_governance",
    "list_astrology_doctrine_governance",
    "validate_doctrine_status_transition",
    "validate_owner_status_transition",
    "DEPENDENCY_STORY_IDS",
    "SELECTED_TEMPORAL_FAMILY_CODE",
    "SELECTED_TEMPORAL_TECHNIQUE_NAME",
    "TEMPORAL_SELECTION_DECISION_STORY_ID",
    "TEMPORAL_SELECTION_OWNER",
    "FirstTemporalTechniqueSelection",
    "TemporalCandidateDecision",
    "TemporalCandidateStatus",
    "TemporalChartObjectRequirement",
    "TemporalInputRequirement",
    "TemporalPublicProjectionStatus",
    "TemporalRelationshipRequirement",
    "TemporalTechniqueSelectionStatus",
    "build_first_temporal_technique_selection",
    "temporal_selection_to_dict",
    "ChartObjectCapabilityTaxonomyEntry",
    "ChartObjectCapabilityTaxonomyError",
    "ChartObjectDecisionStatus",
    "ChartObjectFamily",
    "build_chart_object_capability_taxonomy",
    "get_chart_object_capability_taxonomy",
    "list_chart_object_capability_taxonomy",
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
    "BalanceScoreRuntimeData",
    "ChartBalanceRuntimeData",
    "ChartSignatureRuntimeData",
    "DominantAspectReason",
    "DominantAspectRuntimeData",
    "DominanceRankRuntimeData",
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
    "PlanetNatureReferenceData",
    "PlanetNatureReferenceSet",
    "PlanetReferenceSet",
    "SignReferenceData",
    "SignReferenceSet",
    "SignDignityRuntimeData",
    "SignDominanceReason",
    "SignOccupantRuntimeData",
    "SignRuntimeData",
    "resolve_house_kind",
]

_LAZY_EXPORTS = {
    "AspectIdentityRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectInterpretiveHintsRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectInterpretiveHintResolver": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectMetadataRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectModifierRuntimeData": "app.domain.astrology.runtime.aspect_modifiers",
    "AspectModifierType": "app.domain.astrology.runtime.aspect_modifiers",
    "AspectOrbRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectParticipantsRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectPhaseRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectRuntimeWeightTaxonomy": "app.domain.astrology.runtime.aspect_modifiers",
    "AspectStructuralRuntimeData": "app.domain.astrology.runtime.aspect_runtime_data",
    "AspectStructuralModifierRuntimeData": "app.domain.astrology.runtime.aspect_modifiers",
    "resolve_aspect_interpretive_hints": "app.domain.astrology.runtime.aspect_runtime_data",
    "AstrologyDoctrineGovernanceEntry": (
        "app.domain.astrology.runtime.astrology_doctrine_governance"
    ),
    "AstrologyDoctrineGovernanceError": (
        "app.domain.astrology.runtime.astrology_doctrine_governance"
    ),
    "CanonicalRuleOwner": "app.domain.astrology.runtime.astrology_doctrine_governance",
    "DoctrineDecisionStatus": "app.domain.astrology.runtime.astrology_doctrine_governance",
    "RuleSourceOwnerStatus": "app.domain.astrology.runtime.astrology_doctrine_governance",
    "SchoolPolicy": "app.domain.astrology.runtime.astrology_doctrine_governance",
    "VersionPolicy": "app.domain.astrology.runtime.astrology_doctrine_governance",
    "build_astrology_doctrine_governance": (
        "app.domain.astrology.runtime.astrology_doctrine_governance"
    ),
    "get_astrology_doctrine_governance": (
        "app.domain.astrology.runtime.astrology_doctrine_governance"
    ),
    "list_astrology_doctrine_governance": (
        "app.domain.astrology.runtime.astrology_doctrine_governance"
    ),
    "validate_doctrine_status_transition": (
        "app.domain.astrology.runtime.astrology_doctrine_governance"
    ),
    "validate_owner_status_transition": (
        "app.domain.astrology.runtime.astrology_doctrine_governance"
    ),
    "DEPENDENCY_STORY_IDS": "app.domain.astrology.runtime.temporal_technique_selection",
    "SELECTED_TEMPORAL_FAMILY_CODE": "app.domain.astrology.runtime.temporal_technique_selection",
    "SELECTED_TEMPORAL_TECHNIQUE_NAME": (
        "app.domain.astrology.runtime.temporal_technique_selection"
    ),
    "TEMPORAL_SELECTION_DECISION_STORY_ID": (
        "app.domain.astrology.runtime.temporal_technique_selection"
    ),
    "TEMPORAL_SELECTION_OWNER": "app.domain.astrology.runtime.temporal_technique_selection",
    "FirstTemporalTechniqueSelection": (
        "app.domain.astrology.runtime.temporal_technique_selection"
    ),
    "TemporalCandidateDecision": "app.domain.astrology.runtime.temporal_technique_selection",
    "TemporalCandidateStatus": "app.domain.astrology.runtime.temporal_technique_selection",
    "TemporalChartObjectRequirement": ("app.domain.astrology.runtime.temporal_technique_selection"),
    "TemporalInputRequirement": "app.domain.astrology.runtime.temporal_technique_selection",
    "TemporalPublicProjectionStatus": ("app.domain.astrology.runtime.temporal_technique_selection"),
    "TemporalRelationshipRequirement": (
        "app.domain.astrology.runtime.temporal_technique_selection"
    ),
    "TemporalTechniqueSelectionStatus": (
        "app.domain.astrology.runtime.temporal_technique_selection"
    ),
    "build_first_temporal_technique_selection": (
        "app.domain.astrology.runtime.temporal_technique_selection"
    ),
    "temporal_selection_to_dict": "app.domain.astrology.runtime.temporal_technique_selection",
    "ChartObjectCapabilityTaxonomyEntry": (
        "app.domain.astrology.runtime.chart_object_capability_taxonomy"
    ),
    "ChartObjectCapabilityTaxonomyError": (
        "app.domain.astrology.runtime.chart_object_capability_taxonomy"
    ),
    "ChartObjectDecisionStatus": "app.domain.astrology.runtime.chart_object_capability_taxonomy",
    "ChartObjectFamily": "app.domain.astrology.runtime.chart_object_capability_taxonomy",
    "build_chart_object_capability_taxonomy": (
        "app.domain.astrology.runtime.chart_object_capability_taxonomy"
    ),
    "get_chart_object_capability_taxonomy": (
        "app.domain.astrology.runtime.chart_object_capability_taxonomy"
    ),
    "list_chart_object_capability_taxonomy": (
        "app.domain.astrology.runtime.chart_object_capability_taxonomy"
    ),
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
