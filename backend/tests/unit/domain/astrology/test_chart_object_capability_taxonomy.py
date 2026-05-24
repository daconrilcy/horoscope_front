# Tests de la matrice canonique des capacites d'objets astrologiques.
"""Verifie la gouvernance runtime des familles d'objets astrologiques."""

import pytest

from app.domain.astrology.runtime.chart_object_capability_taxonomy import (
    CHART_OBJECT_CAPABILITY_TAXONOMY_DECLARATIONS,
    MANDATORY_CHART_OBJECT_FAMILIES,
    ChartObjectCapabilityTaxonomyEntry,
    ChartObjectCapabilityTaxonomyError,
    ChartObjectDecisionStatus,
    ChartObjectFamily,
    build_chart_object_capability_taxonomy,
    get_chart_object_capability_taxonomy,
    list_chart_object_capability_taxonomy,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectCapabilities,
    ChartObjectSourceType,
    ChartObjectType,
)

REQUIRED_TAXONOMY_FIELDS = {
    "object_family",
    "canonical_type",
    "source_kind",
    "positionable",
    "aspectable",
    "interpretable",
    "scorable",
    "dignity_eligible",
    "dominance_eligible",
    "public_projection",
    "decision_status",
    "motion_visibility",
    "house_rulership",
    "fixed_star_contact",
}


def test_taxonomy_declares_all_mandatory_families_once() -> None:
    """La matrice couvre toutes les familles requises par CS-249."""
    entries = list_chart_object_capability_taxonomy()

    assert tuple(entry.object_family for entry in entries) == MANDATORY_CHART_OBJECT_FAMILIES
    assert len({entry.object_family for entry in entries}) == len(MANDATORY_CHART_OBJECT_FAMILIES)


def test_each_taxonomy_row_exposes_required_columns() -> None:
    """Chaque ligne expose les colonnes de contrat attendues."""
    assert set(ChartObjectCapabilityTaxonomyEntry.__dataclass_fields__) == (
        REQUIRED_TAXONOMY_FIELDS
    )
    for entry in list_chart_object_capability_taxonomy():
        assert isinstance(entry.object_family, ChartObjectFamily)
        assert isinstance(entry.canonical_type, ChartObjectType)
        assert isinstance(entry.source_kind, ChartObjectSourceType)
        assert isinstance(entry.decision_status, ChartObjectDecisionStatus)
        assert isinstance(entry.runtime_capabilities, ChartObjectCapabilities)


def test_existing_runtime_capabilities_are_preserved_for_active_families() -> None:
    """Les familles deja supportees gardent les valeurs de capacite runtime."""
    sun = get_chart_object_capability_taxonomy(ChartObjectFamily.SUN)
    angle = get_chart_object_capability_taxonomy(ChartObjectFamily.ANGLE)
    node = get_chart_object_capability_taxonomy(ChartObjectFamily.LUNAR_NODE)
    fixed_star = get_chart_object_capability_taxonomy(ChartObjectFamily.FIXED_STAR)

    assert sun.runtime_capabilities == ChartObjectCapabilities(
        supports_aspects=True,
        supports_dignities=True,
        supports_house_position=True,
        supports_visibility=True,
        supports_motion=True,
        supports_interpretation=True,
        supports_dominance=True,
        supports_rulership=True,
        supports_fixed_star_conjunction=True,
    )
    assert angle.runtime_capabilities == ChartObjectCapabilities(
        supports_aspects=True,
        supports_house_position=True,
        supports_interpretation=True,
    )
    assert node.runtime_capabilities == ChartObjectCapabilities(
        supports_aspects=True,
        supports_house_position=True,
        supports_interpretation=True,
    )
    assert fixed_star.runtime_capabilities == ChartObjectCapabilities()


def test_unknown_family_is_rejected_without_fallback() -> None:
    """Un code inconnu ne se rabat jamais sur une famille existante."""
    with pytest.raises(ChartObjectCapabilityTaxonomyError, match="Unknown chart object family"):
        get_chart_object_capability_taxonomy("unknown_object")


def test_duplicate_family_declarations_are_rejected() -> None:
    """La construction refuse deux lignes pour la meme famille."""
    duplicated = (
        *CHART_OBJECT_CAPABILITY_TAXONOMY_DECLARATIONS,
        _copy_entry(CHART_OBJECT_CAPABILITY_TAXONOMY_DECLARATIONS[0]),
    )

    with pytest.raises(ChartObjectCapabilityTaxonomyError, match="Duplicate"):
        build_chart_object_capability_taxonomy(duplicated)


def test_unresolved_families_are_explicit_user_decisions() -> None:
    """Les choix produit ou doctrine non tranches restent bloquants."""
    unresolved = {
        ChartObjectFamily.LILITH,
        ChartObjectFamily.APSIDE,
        ChartObjectFamily.LOT,
        ChartObjectFamily.ASTEROID,
        ChartObjectFamily.CHIRON,
        ChartObjectFamily.MIDPOINT,
    }

    assert {
        entry.object_family
        for entry in list_chart_object_capability_taxonomy()
        if entry.decision_status is ChartObjectDecisionStatus.NEEDS_USER_DECISION
    } == unresolved


def test_no_new_family_calculators_are_declared_in_taxonomy() -> None:
    """La matrice ne deguise pas les familles non decidees en calculateurs actifs."""
    for family in (
        ChartObjectFamily.LOT,
        ChartObjectFamily.ASTEROID,
        ChartObjectFamily.CHIRON,
        ChartObjectFamily.MIDPOINT,
    ):
        entry = get_chart_object_capability_taxonomy(family)

        assert entry.decision_status is ChartObjectDecisionStatus.NEEDS_USER_DECISION
        assert entry.scorable is False
        assert entry.dignity_eligible is False
        assert entry.dominance_eligible is False


def _copy_entry(
    entry: ChartObjectCapabilityTaxonomyEntry,
) -> ChartObjectCapabilityTaxonomyEntry:
    """Copie une ligne pour prouver la detection de doublon."""
    return ChartObjectCapabilityTaxonomyEntry(
        object_family=entry.object_family,
        canonical_type=entry.canonical_type,
        source_kind=entry.source_kind,
        positionable=entry.positionable,
        aspectable=entry.aspectable,
        interpretable=entry.interpretable,
        scorable=entry.scorable,
        dignity_eligible=entry.dignity_eligible,
        dominance_eligible=entry.dominance_eligible,
        public_projection=entry.public_projection,
        decision_status=entry.decision_status,
        motion_visibility=entry.motion_visibility,
        house_rulership=entry.house_rulership,
        fixed_star_contact=entry.fixed_star_contact,
    )
