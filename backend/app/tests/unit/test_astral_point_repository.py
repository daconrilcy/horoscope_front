"""Tests du chargement runtime typé des points astraux."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.domain.astrology.runtime.runtime_reference import AstralPointRuntime
from app.infra.db.repositories.astrology_runtime_reference_repository import (
    AstrologyRuntimeReferenceRepository,
)
from app.services.reference_data_service import ReferenceDataService


def test_repository_loads_astral_points_as_immutable_contracts(db_session) -> None:
    """Le runtime expose les points astraux sous dataclasses immutables."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")

    reference = AstrologyRuntimeReferenceRepository(db_session).load("1.0.0")

    assert all(isinstance(point, AstralPointRuntime) for point in reference.astral_points.items)
    by_code = {point.code: point for point in reference.astral_points.items}
    assert set(by_code) == {
        "north_node",
        "south_node",
        "lunar_apogee",
        "lunar_perigee",
        "black_moon_lilith",
    }
    assert by_code["north_node"].default_variant_code == "true"
    assert by_code["black_moon_lilith"].variants[0].engine_key == "SE_MEAN_APOG"
    with pytest.raises(FrozenInstanceError):
        by_code["north_node"].display_name = "Changed"


def test_repository_loads_astral_points_directly_as_typed_contracts(db_session) -> None:
    """Le chargement dédié des points astraux ne sort pas de dict brut."""
    ReferenceDataService.seed_reference_version(db_session, version="1.0.0")

    astral_points = AstrologyRuntimeReferenceRepository(db_session).load_astral_points()

    assert all(isinstance(point, AstralPointRuntime) for point in astral_points.items)
    assert not any(isinstance(point, dict) for point in astral_points.items)
    assert "lunar_perigee" in {point.code for point in astral_points.items}
