# Tests du runtime interne transit_chart_v1.
"""Verifie le runtime transit interne sans surface publique ni etoiles fixes."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import pytest

from app.domain.astrology.builders.chart_object_runtime_builder import (
    build_chart_object_runtime_data,
)
from app.domain.astrology.runtime.chart_object_runtime_data import ChartObjectRuntimeData
from app.domain.astrology.runtime.transit_chart_runtime import (
    TRANSIT_CHART_RUNTIME_PUBLIC_EXPOSURE,
    TRANSIT_CHART_RUNTIME_TRACE_KEYS,
    TransitChartRuntimePayload,
    build_internal_transit_chart_runtime,
    transit_chart_runtime_to_dict,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
RUNTIME_PATH = REPO_ROOT / "app/domain/astrology/runtime/transit_chart_runtime.py"


@dataclass(frozen=True, slots=True)
class PlanetSource:
    """Position planetaire minimale pour le builder runtime existant."""

    planet_code: str
    longitude: float
    sign_code: str
    house_number: int
    speed_longitude: float | None = None
    is_retrograde: bool | None = None


@dataclass(frozen=True, slots=True)
class HouseSource:
    """Maison minimale pour le builder runtime existant."""

    number: int
    cusp_longitude: float
    cusp_sign: str | None
    house_kind: str | None = None


@dataclass(frozen=True, slots=True)
class TransitAspectSource:
    """Aspect transit vers natal deja calcule par la couche amont."""

    transit_object_code: str
    natal_object_code: str
    aspect_code: str
    angle: float
    orb: float
    orb_used: float
    orb_max: float
    family: str
    is_major: bool
    is_minor: bool


def test_runtime_reuses_temporal_owner_and_existing_chart_object_builder() -> None:
    """Le runtime construit les objets transit sans modele transit parallele."""
    payload = _runtime_payload()

    assert payload.family_code == "transit_chart_v1"
    assert payload.public_exposure == TRANSIT_CHART_RUNTIME_PUBLIC_EXPOSURE
    assert {obj.code for obj in payload.transiting_chart_objects} >= {"sun", "moon"}
    assert all(isinstance(obj, ChartObjectRuntimeData) for obj in payload.transiting_chart_objects)
    assert all(
        not obj.capabilities.supports_fixed_star_conjunction
        for obj in payload.transiting_chart_objects
    )
    assert all(obj.payloads.fixed_star is None for obj in payload.transiting_chart_objects)
    assert all(not obj.payloads.fixed_star_conjunctions for obj in payload.transiting_chart_objects)


def test_runtime_relationships_are_structural_and_deterministic() -> None:
    """Les relations transit vers natal sont triees et non narratives."""
    payload = _runtime_payload()

    relationship_codes = tuple(
        relationship.relationship_code for relationship in payload.transit_to_natal_relationships
    )

    assert relationship_codes == ("moon:trine:sun", "sun:conjunction:moon")
    first = payload.transit_to_natal_relationships[0]
    assert first.transit_object_code == "moon"
    assert first.natal_object_code == "sun"
    assert first.aspect.aspect.code == "trine"
    assert first.aspect.participants.planet_a == "moon"
    assert first.aspect.participants.planet_b == "sun"
    assert first.source == "app.domain.astrology.builders.aspect_runtime_builder"


def test_runtime_emits_astronomical_proof_refs_and_doctrine_limits() -> None:
    """La preuve et les limites doctrinales citent les owners existants."""
    payload = _runtime_payload()

    assert "cs253-blocked-by-cs250-astronomical-proof" in payload.astronomical_proof_refs
    assert "mode:swisseph" in payload.astronomical_proof_refs
    assert any(ref.startswith("tolerance:") for ref in payload.astronomical_proof_refs)
    assert any(ref.startswith("golden:") for ref in payload.astronomical_proof_refs)
    doctrine_blob = " ".join(payload.doctrine_limits)
    assert "aspect_rules:" in doctrine_blob
    assert "interpretation_rules:" in doctrine_blob
    assert "public_copy:no-transit-text" in doctrine_blob
    assert "fixed_stars:not-exposed" in doctrine_blob


def test_runtime_trace_keys_are_bounded_and_serializable() -> None:
    """La trace interne expose seulement les cles diagnostiques autorisees."""
    payload = _runtime_payload()
    as_dict = transit_chart_runtime_to_dict(payload)

    assert payload.trace.keys == TRANSIT_CHART_RUNTIME_TRACE_KEYS
    assert payload.trace.run_id == "unit-run-001"
    assert payload.trace.public_exposure == "blocked"
    assert set(as_dict) == {
        "family_code",
        "transiting_chart_objects",
        "transit_to_natal_relationships",
        "astronomical_proof_refs",
        "doctrine_limits",
        "trace",
        "public_exposure",
    }
    assert as_dict["family_code"] == "transit_chart_v1"


def test_runtime_rejects_unknown_relationship_objects() -> None:
    """Une relation non rattachee aux objets fournis echoue explicitement."""
    aspects = (
        TransitAspectSource(
            transit_object_code="mars",
            natal_object_code="sun",
            aspect_code="square",
            angle=90.0,
            orb=1.0,
            orb_used=1.0,
            orb_max=6.0,
            family="major",
            is_major=True,
            is_minor=False,
        ),
    )

    with pytest.raises(ValueError, match="Unknown transiting object 'mars'"):
        build_internal_transit_chart_runtime(
            planet_positions=_transit_planets(),
            houses=_houses(),
            natal_chart_objects=_natal_objects(),
            transit_aspects=aspects,
            run_id="unit-run-unknown",
        )


def test_runtime_ast_guard_keeps_api_frontend_storage_and_fixed_star_out() -> None:
    """AST guard: le runtime reste domaine pur et ne publie pas les etoiles fixes."""
    tree = ast.parse(RUNTIME_PATH.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert not any(module.startswith("app.api") for module in imported_modules)
    assert not any(module.startswith("app.services") for module in imported_modules)
    assert not any(module.startswith("app.infra") for module in imported_modules)
    assert not any("frontend" in module for module in imported_modules)
    assert not any("fixed_stars" in module for module in imported_modules)


def _runtime_payload() -> TransitChartRuntimePayload:
    """Construit un payload runtime stable pour les tests."""
    return build_internal_transit_chart_runtime(
        planet_positions=_transit_planets(),
        houses=_houses(),
        natal_chart_objects=_natal_objects(),
        transit_aspects=(
            TransitAspectSource(
                transit_object_code="sun",
                natal_object_code="moon",
                aspect_code="conjunction",
                angle=0.0,
                orb=0.2,
                orb_used=0.2,
                orb_max=8.0,
                family="major",
                is_major=True,
                is_minor=False,
            ),
            TransitAspectSource(
                transit_object_code="moon",
                natal_object_code="sun",
                aspect_code="trine",
                angle=120.0,
                orb=1.25,
                orb_used=1.25,
                orb_max=7.0,
                family="major",
                is_major=True,
                is_minor=False,
            ),
        ),
        run_id="unit-run-001",
    )


def _natal_objects() -> tuple[ChartObjectRuntimeData, ...]:
    """Retourne des objets natals construits par le builder canonique."""
    return build_chart_object_runtime_data(
        planet_positions=(
            PlanetSource("sun", 83.5, "gemini", 10),
            PlanetSource("moon", 343.2, "pisces", 7),
        ),
        astral_points=(),
        houses=_houses(),
        fixed_stars=(),
    )


def _transit_planets() -> tuple[PlanetSource, ...]:
    """Retourne les positions transitantes minimales du test."""
    return (
        PlanetSource("sun", 84.1, "gemini", 10),
        PlanetSource("moon", 102.5, "cancer", 11),
    )


def _houses() -> tuple[HouseSource, ...]:
    """Retourne douze maisons factices suffisantes pour le runtime objet."""
    return tuple(
        HouseSource(number=number, cusp_longitude=float((number - 1) * 30), cusp_sign="aries")
        for number in range(1, 13)
    )
