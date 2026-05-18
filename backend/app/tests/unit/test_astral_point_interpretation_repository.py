"""Tests du branchement interprétatif des points astraux."""

from __future__ import annotations

import pytest

from app.domain.astrology.interpretation.astral_point_interpretation import (
    AstralPointInterpretationEnricher,
)
from app.domain.astrology.natal_calculation import NatalAstralPointPosition
from app.infra.db.repositories.astral_point_interpretation_repository import (
    AstralPointInterpretationRepository,
)
from app.services.reference_data_service import ReferenceDataService


def _north_node_position() -> NatalAstralPointPosition:
    """Construit une position brute semblable au résultat natal."""
    return NatalAstralPointPosition(
        code="north_node",
        variant_code="true",
        longitude=123.45,
        sign="leo",
        degree_in_sign=3.45,
        house=8,
        is_physical_body=False,
    )


def test_repository_loads_profile_and_keywords_for_point_position(db_session) -> None:
    """Le repository fournit profil et keywords typés pour une position calculée."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")

    profile = AstralPointInterpretationRepository(db_session).load_profile_for_position(
        _north_node_position()
    )

    assert profile is not None
    assert profile.point_code == "north_node"
    assert profile.variant_code is None
    assert profile.language_code == "en"
    assert "growth" in profile.keywords.core


def test_enricher_combines_position_profile_and_keywords_without_recalculation(db_session) -> None:
    """L'enrichissement éditorial conserve la position brute et ajoute le profil."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")
    position = _north_node_position()
    profile = AstralPointInterpretationRepository(db_session).load_profile_for_position(position)
    assert profile is not None

    interpretation = AstralPointInterpretationEnricher().enrich(
        point_position=position,
        interpretation_profile=profile,
    )

    assert interpretation.point_code == "north_node"
    assert interpretation.longitude == 123.45
    assert interpretation.house == 8
    assert interpretation.title == "North Node"
    assert interpretation.keywords.core == profile.keywords.core


def test_enricher_rejects_profile_for_another_point(db_session) -> None:
    """Un profil éditorial d'un autre point ne peut pas enrichir la position."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")
    profile = AstralPointInterpretationRepository(db_session).load_profile_for_position(
        _north_node_position()
    )
    assert profile is not None
    south_node_position = NatalAstralPointPosition(
        code="south_node",
        variant_code="true",
        longitude=303.45,
        sign="aquarius",
        degree_in_sign=3.45,
        house=2,
        is_physical_body=False,
    )

    with pytest.raises(ValueError, match="does not match position"):
        AstralPointInterpretationEnricher().enrich(
            point_position=south_node_position,
            interpretation_profile=profile,
        )
