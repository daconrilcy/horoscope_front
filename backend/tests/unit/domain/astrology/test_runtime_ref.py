"""Tests des contrats immutables du referentiel astrologique runtime."""

from dataclasses import FrozenInstanceError, is_dataclass
from types import MappingProxyType

import pytest

from app.domain.astrology.runtime.runtime_reference import (
    AstrologyRuntimeReference,
    DignityReferenceSet,
    PlanetReferenceData,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_runtime_reference_contracts_are_frozen_dataclasses() -> None:
    """Les contrats runtime sont des dataclasses figees et non mutables."""
    reference = complete_reference()

    assert isinstance(reference, AstrologyRuntimeReference)
    assert is_dataclass(reference)
    assert is_dataclass(reference.planets.items[0])

    with pytest.raises(FrozenInstanceError):
        reference.reference_version = "mutated"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        reference.planets.items[0].code = "mutated"  # type: ignore[misc]


def test_runtime_reference_collections_are_tuple_based() -> None:
    """Les collections metier runtime exposent des tuples immutables."""
    reference = complete_reference()

    assert isinstance(reference.planets.items, tuple)
    assert isinstance(reference.signs.items, tuple)
    assert isinstance(reference.houses.items, tuple)
    assert isinstance(reference.aspects.items, tuple)
    assert isinstance(reference.aspects.orb_rules, tuple)

    with pytest.raises(FrozenInstanceError):
        reference.planets.items += (PlanetReferenceData(code="x", name="X"),)  # type: ignore[misc]


def test_dignity_rulership_mapping_is_read_only() -> None:
    """La carte signe vers maitre est exposee en lecture seule."""
    dignities = DignityReferenceSet(items=(), sign_rulerships={"aries": "mars"})

    assert isinstance(dignities.sign_rulerships, MappingProxyType)
    with pytest.raises(TypeError):
        dignities.sign_rulerships["aries"] = "venus"  # type: ignore[index]
