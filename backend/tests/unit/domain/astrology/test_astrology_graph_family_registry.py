# Tests du registre canonique des familles de graphes astrologiques.
"""Verifie la gouvernance runtime des familles de graphes astrologiques."""

import pytest

from app.domain.astrology.runtime.astrology_graph_family_registry import (
    ASTROLOGY_GRAPH_FAMILY_DECLARATIONS,
    ASTRONOMICAL_PROOF_BLOCKER,
    CACHE_POLICY_BLOCKER,
    MANDATORY_ASTROLOGY_GRAPH_FAMILY_CODES,
    AstrologyGraphFamilyMetadata,
    AstrologyGraphFamilyOwner,
    AstrologyGraphFamilyRegistryError,
    AstrologyGraphFamilyStatus,
    build_astrology_graph_family_registry,
    get_astrology_graph_family,
    list_astrology_graph_families,
    list_astrology_graph_families_by_status,
    resolve_astrology_graph_definition,
)
from app.domain.astrology.runtime.calculation_graph_validator import (
    validate_calculation_graph_definition,
)
from app.domain.astrology.runtime.natal_calculation_graph import NATAL_GRAPH_CODE


def test_registry_declares_all_mandatory_family_codes_once() -> None:
    """Le registre couvre toutes les familles obligatoires de CS-246."""
    families = list_astrology_graph_families()

    assert tuple(family.code for family in families) == MANDATORY_ASTROLOGY_GRAPH_FAMILY_CODES
    assert len({family.code for family in families}) == len(MANDATORY_ASTROLOGY_GRAPH_FAMILY_CODES)


def test_each_family_exposes_required_metadata_fields() -> None:
    """Chaque famille publie les metadonnees internes necessaires."""
    for family in list_astrology_graph_families():
        assert family.code
        assert isinstance(family.status, AstrologyGraphFamilyStatus)
        assert isinstance(family.target_owner, AstrologyGraphFamilyOwner)
        assert family.required_inputs
        assert family.expected_graph_type == "CalculationGraphDefinition"
        assert family.required_objects
        assert family.internal_surfaces
        assert family.trace_replay_needs
        assert family.cache_invalidation_boundary
        if family.status != AstrologyGraphFamilyStatus.ACTIVE:
            assert family.blockers or family.user_decisions


def test_blocked_families_document_cache_policy_blocker() -> None:
    """Chaque famille bloquee garde le blocker cache explicite du brief."""
    for family in list_astrology_graph_families():
        if family.status != AstrologyGraphFamilyStatus.ACTIVE:
            assert CACHE_POLICY_BLOCKER in family.blockers


def test_natal_family_is_active_and_linked_to_current_graph_definition() -> None:
    """La famille natale pointe vers le graphe existant sans changer sa validation."""
    family = get_astrology_graph_family(NATAL_GRAPH_CODE)
    graph = resolve_astrology_graph_definition(NATAL_GRAPH_CODE)
    validation = validate_calculation_graph_definition(graph)

    assert family.status == AstrologyGraphFamilyStatus.ACTIVE
    assert family.target_owner == AstrologyGraphFamilyOwner.NATAL_RUNTIME
    assert family.cache_invalidation_boundary
    assert graph.graph_code == NATAL_GRAPH_CODE
    assert validation.is_valid is True


def test_temporal_families_are_blocked_by_astronomical_proof() -> None:
    """Les familles temporelles restent bloquees jusqu'a CS-250 ou risk acceptance."""
    temporal_codes = {
        "transit_chart_v1",
        "solar_return_v1",
        "lunar_return_v1",
        "progressed_chart_v1",
        "profection_v1",
    }
    blocked = list_astrology_graph_families_by_status(
        AstrologyGraphFamilyStatus.BLOCKED_BY_ASTRONOMICAL_PROOF
    )

    assert temporal_codes <= {family.code for family in blocked}
    for code in temporal_codes:
        assert ASTRONOMICAL_PROOF_BLOCKER in get_astrology_graph_family(code).blockers


def test_registry_answers_owner_inputs_blocker_and_cache_queries() -> None:
    """Les requetes attendues par le brief repondent de facon deterministe."""
    assert (
        get_astrology_graph_family("transit_chart_v1").target_owner
        == AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME
    )
    assert "secondary_birth_data" in get_astrology_graph_family("synastry_chart_v1").required_inputs
    assert get_astrology_graph_family(NATAL_GRAPH_CODE).cache_invalidation_boundary
    assert get_astrology_graph_family("forecasting_v1").blockers


def test_duplicate_family_codes_are_rejected() -> None:
    """La construction refuse deux declarations portant le meme code."""
    duplicated = (
        *ASTROLOGY_GRAPH_FAMILY_DECLARATIONS,
        _copy_family(ASTROLOGY_GRAPH_FAMILY_DECLARATIONS[0]),
    )

    with pytest.raises(AstrologyGraphFamilyRegistryError, match="Duplicate"):
        build_astrology_graph_family_registry(duplicated)


def test_unknown_family_code_is_rejected_without_fallback() -> None:
    """Un code inconnu ne se rabat jamais sur une famille existante."""
    with pytest.raises(AstrologyGraphFamilyRegistryError, match="Unknown astrology graph family"):
        get_astrology_graph_family("unknown_chart_v1")


def test_blocked_family_has_no_executable_graph_definition() -> None:
    """Une famille bloquee ne declare pas de runner implicite."""
    with pytest.raises(AstrologyGraphFamilyRegistryError, match="no executable graph definition"):
        resolve_astrology_graph_definition("transit_chart_v1")


def _copy_family(family: AstrologyGraphFamilyMetadata) -> AstrologyGraphFamilyMetadata:
    """Copie une famille pour prouver la detection de doublon."""
    return AstrologyGraphFamilyMetadata(
        code=family.code,
        status=family.status,
        target_owner=family.target_owner,
        required_inputs=family.required_inputs,
        expected_graph_type=family.expected_graph_type,
        required_objects=family.required_objects,
        authorized_public_surfaces=family.authorized_public_surfaces,
        internal_surfaces=family.internal_surfaces,
        trace_replay_needs=family.trace_replay_needs,
        cache_invalidation_boundary=family.cache_invalidation_boundary,
        blockers=family.blockers,
        user_decisions=family.user_decisions,
    )
