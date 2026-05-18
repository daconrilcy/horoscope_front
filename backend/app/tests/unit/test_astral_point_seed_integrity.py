"""Tests d'intégrité du seed des tables `astral_point_*`."""

from __future__ import annotations

from collections import Counter

from sqlalchemy import select

from app.infra.db.models.interpretation_reference import AstralPointInterpretationProfileModel
from app.infra.db.models.reference import (
    AstralPointAliasModel,
    AstralPointCalculationVariantModel,
    AstralPointFamilyModel,
    AstralPointInterpretationKeywordModel,
    AstralPointModel,
)
from app.services.reference_data_service import ReferenceDataService


def test_astral_point_seed_populates_expected_tables_and_defaults(db_session) -> None:
    """Le seed dédié alimente familles, points, variantes, alias et profils."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")

    assert db_session.query(AstralPointFamilyModel).count() == 3
    assert db_session.query(AstralPointModel).count() == 5
    assert db_session.query(AstralPointCalculationVariantModel).count() == 10
    assert db_session.query(AstralPointAliasModel).count() == 17
    assert db_session.query(AstralPointInterpretationKeywordModel).count() == 5
    assert db_session.query(AstralPointInterpretationProfileModel).count() == 5

    variants = db_session.scalars(select(AstralPointCalculationVariantModel)).all()
    default_counts = Counter(
        variant.astral_point_code for variant in variants if variant.is_default
    )
    assert default_counts == {
        "north_node": 1,
        "south_node": 1,
        "lunar_apogee": 1,
        "lunar_perigee": 1,
        "black_moon_lilith": 1,
    }


def test_astral_point_aliases_reference_existing_variants(db_session) -> None:
    """Les alias rattachés à une variante ciblent une variante existante."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")

    variant_keys = {
        (variant.astral_point_code, variant.variant_code)
        for variant in db_session.scalars(select(AstralPointCalculationVariantModel))
    }
    aliases = db_session.scalars(select(AstralPointAliasModel)).all()

    assert all(
        alias.variant_code is None or (alias.astral_point_code, alias.variant_code) in variant_keys
        for alias in aliases
    )


def test_astral_point_interpretation_profiles_reference_points_and_keyword_sets(
    db_session,
) -> None:
    """Les profils éditoriaux référencent uniquement des points et keywords seedés."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")

    point_codes = {row.code for row in db_session.scalars(select(AstralPointModel)).all()}
    keyword_ids = {
        row.id for row in db_session.scalars(select(AstralPointInterpretationKeywordModel)).all()
    }
    profiles = db_session.scalars(select(AstralPointInterpretationProfileModel)).all()

    assert profiles
    assert all(profile.astral_point_code in point_codes for profile in profiles)
    assert all(profile.keyword_set_id in keyword_ids for profile in profiles)


def test_each_astral_point_has_generic_interpretation_profile(db_session) -> None:
    """Chaque point astral seedé possède un profil générique sans variante."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")

    point_codes = {row.code for row in db_session.scalars(select(AstralPointModel)).all()}
    generic_profile_codes = {
        row.astral_point_code
        for row in db_session.scalars(select(AstralPointInterpretationProfileModel)).all()
        if row.variant_code is None
    }

    assert generic_profile_codes == point_codes
