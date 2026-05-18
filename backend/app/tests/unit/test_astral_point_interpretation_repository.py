"""Tests du branchement interprétatif des points astraux."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.domain.astrology.interpretation.astral_point_interpretation import (
    AstralPointInterpretationEnricher,
)
from app.domain.astrology.natal_calculation import NatalAstralPointPosition
from app.infra.db.models.interpretation_reference import AstralPointInterpretationProfileModel
from app.infra.db.models.reference import AstralPointInterpretationKeywordModel, LanguageModel
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

    assert interpretation.code == "north_node"
    assert interpretation.house == 8
    assert interpretation.title == "North Node"
    assert interpretation.core_keywords == profile.keywords.core


def test_repository_falls_back_from_locale_and_tradition_to_default_profile(db_session) -> None:
    """La cascade résout le profil par défaut quand la locale demandée est absente."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")

    profile = AstralPointInterpretationRepository(db_session).load_profile_for_position(
        _north_node_position(),
        language_code="fr-FR",
        tradition="traditional",
    )

    assert profile is not None
    assert profile.variant_code is None
    assert profile.language_code == "en"
    assert profile.tradition == "modern_western"


def test_repository_prefers_requested_tradition_with_default_language(db_session) -> None:
    """La langue par défaut ne doit pas écraser la tradition explicitement demandée."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")
    english = db_session.scalars(select(LanguageModel).where(LanguageModel.code == "en")).one()
    keyword_set = db_session.scalars(select(AstralPointInterpretationKeywordModel)).first()
    assert keyword_set is not None
    db_session.add(
        AstralPointInterpretationProfileModel(
            astral_point_code="north_node",
            variant_code=None,
            keyword_set_id=keyword_set.id,
            language_id=english.id,
            tradition="traditional",
            title="North Node Traditional",
            summary="Traditional reading.",
            micro_note=None,
        )
    )
    db_session.flush()

    profile = AstralPointInterpretationRepository(db_session).load_profile_for_position(
        _north_node_position(),
        language_code="fr-FR",
        tradition="traditional",
    )

    assert profile is not None
    assert profile.language_code == "en"
    assert profile.tradition == "traditional"
    assert profile.title == "North Node Traditional"


def test_repository_returns_none_when_no_profile_exists_for_point(db_session) -> None:
    """Une absence de profil reste contrôlée au lieu de produire un texte inventé."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")
    unknown_position = NatalAstralPointPosition(
        code="unsupported_point",
        variant_code="true",
        longitude=12.0,
        sign="aries",
        degree_in_sign=12.0,
        house=None,
        is_physical_body=False,
    )

    profile = AstralPointInterpretationRepository(db_session).load_profile_for_position(
        unknown_position
    )

    assert profile is None


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
