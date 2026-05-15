"""Tests des modifiers et de la taxonomie des poids aspect."""

import pytest

from app.domain.astrology.builders.aspect_runtime_builder import build_aspect_runtime_data
from app.domain.astrology.natal_calculation import AspectResult
from app.domain.astrology.runtime.aspect_modifiers import (
    AspectModifierRuntimeData,
    AspectModifierType,
    AspectRuntimeWeightTaxonomy,
)
from tests.factories.celestial_catalog_factory import make_celestial_catalog

ASPECT_META = {
    "family": "major",
    "is_major": True,
    "is_minor": False,
    "default_valence": "positive",
    "interpretive_valence": "harmonious",
    "energy_type": "harmonious_flow",
}


def test_aspect_modifier_runtime_data_is_typed() -> None:
    """Un modifier porte un type enumere, une source et une intensite."""
    modifier = AspectModifierRuntimeData(
        modifier_type=AspectModifierType.LUMINARY,
        source="participants",
        intensity=0.8,
        applies_to=("moon",),
    )

    assert modifier.modifier_type is AspectModifierType.LUMINARY
    assert modifier.source == "participants"
    assert modifier.intensity == 0.8


def test_aspect_modifier_rejects_invalid_local_weighting() -> None:
    """Un modifier ne doit pas accepter de source vide ni d'intensite invalide."""
    with pytest.raises(ValueError, match="source is required"):
        AspectModifierRuntimeData(
            modifier_type=AspectModifierType.LUMINARY,
            source=" ",
            intensity=0.8,
        )
    with pytest.raises(ValueError, match="between 0 and 1"):
        AspectModifierRuntimeData(
            modifier_type=AspectModifierType.LUMINARY,
            source="participants",
            intensity=1.2,
        )


def test_aspect_runtime_exposes_typed_modifiers() -> None:
    """AspectRuntimeData porte les modifiers typés issus du builder."""
    aspect = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.0,
        orb=0.2,
        orb_used=0.2,
        orb_max=6.0,
        **ASPECT_META,
    )

    runtime = build_aspect_runtime_data(aspect, make_celestial_catalog())

    assert {item.modifier_type for item in runtime.modifiers} == {
        AspectModifierType.EXACT_ORB,
        AspectModifierType.LUMINARY,
    }


def test_weight_taxonomy_separates_owners() -> None:
    """La taxonomie distingue force, dominance, interpretation et produit."""
    taxonomy = AspectRuntimeWeightTaxonomy()

    assert taxonomy.technical_strength.startswith("AspectStrengthEvaluator")
    assert taxonomy.structural_dominance.startswith("DominantAspectEvaluator")
    assert taxonomy.interpretive_weight.startswith("AspectModifierRuntimeData")
    assert taxonomy.product_owner == "domain/prediction owns prediction weighting"
