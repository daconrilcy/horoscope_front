"""Tests des contrats structurels et interpretatifs d'aspects CS-229."""

from __future__ import annotations

from dataclasses import fields

import pytest

from app.domain.astrology.builders.aspect_runtime_builder import build_aspect_runtime_data
from app.domain.astrology.interpretation.aspect_strength_contracts import (
    AspectStrengthLevel,
    AspectStrengthReason,
    AspectStrengthRuntimeData,
)
from app.domain.astrology.natal_calculation import AspectResult
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectInterpretiveProfileRuntimeData,
    AspectStructuralDefinitionRuntimeData,
)
from app.domain.astrology.runtime.aspect_modifiers import (
    AspectModifierRuntimeData,
    AspectModifierType,
    AspectStructuralModifierRuntimeData,
)
from app.domain.astrology.runtime.aspect_runtime_data import (
    AspectIdentityRuntimeData,
    AspectInterpretiveHintsRuntimeData,
    AspectMetadataRuntimeData,
    AspectOrbRuntimeData,
    AspectParticipantsRuntimeData,
    AspectStructuralRuntimeData,
    project_structural_aspect_runtime,
    resolve_aspect_interpretive_hints,
)

FORBIDDEN_STRUCTURAL_FIELDS = {
    "default_valence",
    "interpretive_valence",
    "energy_type",
    "interpretive_weight",
    "meaning",
    "narrative",
    "prompt",
    "llm",
}


def test_structural_aspect_runtime_contract_excludes_interpretive_fields() -> None:
    """Le contrat structurel cible ne declare aucun hint interpretatif."""
    contract_fields = {field.name for field in fields(AspectStructuralRuntimeData)}

    assert contract_fields == {
        "aspect",
        "participants",
        "orb",
        "metadata",
        "strength",
        "phase",
        "modifiers",
    }
    assert contract_fields.isdisjoint(FORBIDDEN_STRUCTURAL_FIELDS)


def test_interpretive_hints_accept_typed_sources_and_optional_weight() -> None:
    """Les hints interpretatifs acceptent axes, sources et poids optionnel."""
    hints = AspectInterpretiveHintsRuntimeData(
        aspect_code="trine",
        default_valence="positive",
        interpretive_valence="harmonious",
        energy_type="harmonious_flow",
        semantic_axes=("cooperation",),
        growth_axes=("integration",),
        interpretive_weight=0.7,
        source_profile_code="modern-trine",
        source_codes=("aspect_profile:trine", "reference:modern"),
    )

    assert hints.aspect_code == "trine"
    assert hints.source_codes == ("aspect_profile:trine", "reference:modern")
    assert hints.interpretive_weight == 0.7


def test_interpretive_hints_require_sources() -> None:
    """Les hints restent sources pour eviter un signal implicite."""
    with pytest.raises(ValueError, match="source_codes"):
        AspectInterpretiveHintsRuntimeData(
            aspect_code="trine",
            default_valence="positive",
            interpretive_valence="harmonious",
            energy_type="harmonious_flow",
        )


def test_aspect_reference_splits_structural_definition_and_profile() -> None:
    """Les contrats separes remplacent la definition legacy hybride."""
    structural = AspectStructuralDefinitionRuntimeData(
        code="trine",
        name="Trine",
        angle=120.0,
        family="major",
        default_orb_deg=6.0,
        is_enabled=True,
        is_major=True,
        is_minor=False,
    )
    profile = AspectInterpretiveProfileRuntimeData(
        aspect_code="trine",
        default_valence="positive",
        interpretive_valence="harmonious",
        energy_type="harmonious_flow",
    )

    assert isinstance(structural, AspectStructuralDefinitionRuntimeData)
    assert isinstance(profile, AspectInterpretiveProfileRuntimeData)
    assert {field.name for field in fields(structural)}.isdisjoint(FORBIDDEN_STRUCTURAL_FIELDS)
    assert profile.energy_type == "harmonious_flow"


def test_aspect_runtime_facade_does_not_expose_legacy_interpretation() -> None:
    """La facade runtime ne declare plus l'alias legacy interpretation."""
    runtime = build_aspect_runtime_data(
        AspectResult(
            aspect_code="trine",
            planet_a="sun",
            planet_b="moon",
            angle=120.0,
            orb=0.2,
            orb_used=0.2,
            orb_max=6.0,
            family="major",
            is_major=True,
            is_minor=False,
        )
    )

    structural = project_structural_aspect_runtime(runtime)

    assert structural.aspect.code == "trine"
    assert not hasattr(runtime, "interpretation")
    assert not hasattr(structural, "interpretation")
    assert all(
        isinstance(item, AspectStructuralModifierRuntimeData) for item in structural.modifiers
    )


def test_structural_contract_can_be_instantiated_without_hints() -> None:
    """Le contrat structurel complet reste purement calculatoire."""
    structural = AspectStructuralRuntimeData(
        aspect=AspectIdentityRuntimeData(code="square", family="major", angle=90.0),
        participants=AspectParticipantsRuntimeData(planet_a="mars", planet_b="saturn"),
        orb=AspectOrbRuntimeData(exact=1.0, max=6.0, ratio=0.1667, strength_level="strong"),
        metadata=AspectMetadataRuntimeData(is_major=True, is_exact=False, is_tight=True),
        strength=AspectStrengthRuntimeData(
            normalized_score=0.75,
            level=AspectStrengthLevel.STRONG,
            is_exact=False,
            is_tight=True,
            reasons=(AspectStrengthReason.TIGHT_ORB,),
        ),
        modifiers=(
            AspectModifierRuntimeData(
                modifier_type=AspectModifierType.TIGHT_ORB,
                source="aspect_strength",
                intensity=0.75,
                applies_to=("mars", "saturn"),
            ),
        ),
    )

    assert structural.modifiers[0].source == "aspect_strength"


def test_resolve_interpretive_hints_uses_structural_runtime_and_profile() -> None:
    """Le resolver dedie assemble des hints sans enrichir le contrat structurel."""
    structural = AspectStructuralRuntimeData(
        aspect=AspectIdentityRuntimeData(code="trine", family="major", angle=120.0),
        participants=AspectParticipantsRuntimeData(planet_a="sun", planet_b="moon"),
        orb=AspectOrbRuntimeData(exact=0.4, max=6.0, ratio=0.0667, strength_level="strong"),
        metadata=AspectMetadataRuntimeData(is_major=True, is_exact=False, is_tight=True),
        strength=AspectStrengthRuntimeData(
            normalized_score=0.9,
            level=AspectStrengthLevel.STRONG,
            is_exact=False,
            is_tight=True,
            reasons=(AspectStrengthReason.TIGHT_ORB,),
        ),
    )
    profile = AspectInterpretiveProfileRuntimeData(
        aspect_code="trine",
        default_valence="positive",
        interpretive_valence="harmonious",
        energy_type="harmonious_flow",
        semantic_axes=("cooperation",),
        source_profile_code="modern-trine",
        reference_version="v1",
    )

    hints = resolve_aspect_interpretive_hints(structural, profile)

    assert hints.aspect_code == "trine"
    assert hints.semantic_axes == ("cooperation",)
    assert hints.source_profile_code == "modern-trine"
    assert hints.source_codes == (
        "aspect:trine",
        "aspect_profile:modern-trine",
        "reference:v1",
    )


def test_resolve_interpretive_hints_rejects_mismatched_profile() -> None:
    """Le resolver refuse un profil qui ne correspond pas a l'aspect structurel."""
    structural = AspectStructuralRuntimeData(
        aspect=AspectIdentityRuntimeData(code="square", family="major", angle=90.0),
        participants=AspectParticipantsRuntimeData(planet_a="mars", planet_b="saturn"),
        orb=AspectOrbRuntimeData(exact=1.0, max=6.0, ratio=0.1667, strength_level="strong"),
        metadata=AspectMetadataRuntimeData(is_major=True, is_exact=False, is_tight=True),
        strength=AspectStrengthRuntimeData(
            normalized_score=0.75,
            level=AspectStrengthLevel.STRONG,
            is_exact=False,
            is_tight=True,
            reasons=(AspectStrengthReason.TIGHT_ORB,),
        ),
    )
    profile = AspectInterpretiveProfileRuntimeData(
        aspect_code="trine",
        default_valence="positive",
        interpretive_valence="harmonious",
        energy_type="harmonious_flow",
    )

    with pytest.raises(ValueError, match="does not match"):
        resolve_aspect_interpretive_hints(structural, profile)
