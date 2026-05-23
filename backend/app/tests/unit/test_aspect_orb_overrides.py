"""Tests des règles d'orbes typées et de leur héritage."""

import pytest

from app.domain.astrology.calculators.aspects import (
    build_aspect_body_from_code,
    build_aspect_body_from_position,
    calculate_major_aspects,
    resolve_orb,
)
from app.domain.astrology.natal_calculation import NatalCalculationError, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectOrbRuleRuntimeData,
    AspectStructuralDefinitionRuntimeData,
)
from tests.factories.astrology_runtime_reference_factory import (
    complete_sign_payloads,
    runtime_reference_from_mapping,
)
from tests.factories.celestial_catalog_factory import make_celestial_catalog


def _definition(system_code: str = "modern") -> AspectStructuralDefinitionRuntimeData:
    """Construit la définition majeure de square pour un système."""
    return AspectStructuralDefinitionRuntimeData(
        code="square",
        name="Square",
        angle=90.0,
        family="major",
        default_orb_deg=6.0,
        is_enabled=True,
        is_major=True,
        is_minor=False,
        system_code=system_code,
    )


def _rule(
    *,
    system_code: str = "modern",
    source_body_type: str = "any",
    target_body_type: str = "any",
    orb_deg: float = 6.0,
    priority: int = 100,
) -> AspectOrbRuleRuntimeData:
    """Construit une règle d'orbe typée."""
    return AspectOrbRuleRuntimeData(
        aspect_code="square",
        system_code=system_code,
        calculation_context="natal",
        source_body_type=source_body_type,
        target_body_type=target_body_type,
        orb_deg=orb_deg,
        priority=priority,
        is_enabled=True,
    )


def _birth_input() -> BirthInput:
    """Construit une entrée natale minimale."""
    return BirthInput(
        birth_date="1985-03-21",
        birth_time="08:30",
        birth_place="Lyon",
        birth_timezone="Europe/Paris",
        birth_lat=45.75,
        birth_lon=4.85,
        place_resolved_id=2,
    )


def _positions_mock(*args: object, **kwargs: object) -> list[dict[str, object]]:
    """Retourne un square Soleil-Mars large pour tester les règles."""
    return [
        {"planet_code": "sun", "longitude": 0.0, "sign_code": "aries"},
        {"planet_code": "mars", "longitude": 97.0, "sign_code": "cancer"},
    ]


def _houses_mock(*args: object, **kwargs: object) -> tuple[list[dict[str, object]], str]:
    """Retourne douze cuspides normalisées."""
    return [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in range(1, 13)], "placidus"


def test_angle_rule_beats_luminary_rule_by_effective_priority() -> None:
    """Une règle angle plus spécifique gagne malgré une priorité brute inférieure."""
    definitions = [_definition()]
    rules = [
        _rule(source_body_type="luminary", orb_deg=8.0, priority=900),
        _rule(source_body_type="angle", orb_deg=5.0, priority=850),
    ]

    assert (
        resolve_orb(
            "square",
            "modern",
            "natal",
            build_aspect_body_from_code("moon", make_celestial_catalog()),
            build_aspect_body_from_code("asc", make_celestial_catalog()),
            definitions,
            rules,
            {"modern": None},
        )
        == 5.0
    )


def test_child_system_inherits_parent_orb_rules_without_copy() -> None:
    """Un système enfant hérite des règles du parent via la carte d'héritage."""
    definitions = [_definition("hellenistic")]
    rules = [_rule(system_code="traditional", source_body_type="luminary", orb_deg=8.0)]

    assert (
        resolve_orb(
            "square",
            "hellenistic",
            "natal",
            build_aspect_body_from_code("sun", make_celestial_catalog()),
            build_aspect_body_from_code("mars", make_celestial_catalog()),
            definitions,
            rules,
            {"hellenistic": "traditional", "traditional": None},
        )
        == 8.0
    )


def test_missing_inheritance_metadata_raises_explicit_error() -> None:
    """Un système sans règle locale ne tombe pas sur une valeur implicite."""
    with pytest.raises(ValueError, match="inheritance metadata missing"):
        resolve_orb(
            "square",
            "hellenistic",
            "natal",
            build_aspect_body_from_code("sun", make_celestial_catalog()),
            build_aspect_body_from_code("mars", make_celestial_catalog()),
            [_definition("hellenistic")],
            [_rule(system_code="traditional", source_body_type="luminary", orb_deg=8.0)],
            {},
        )


def test_calculate_major_aspects_requires_typed_rules() -> None:
    """Le calcul utilise exclusivement les règles typées pour résoudre l'orbe."""
    positions = [
        build_aspect_body_from_position(
            {"planet_code": "uranus", "longitude": 0.0},
            make_celestial_catalog(),
        ),
        build_aspect_body_from_position(
            {"planet_code": "neptune", "longitude": 94.0},
            make_celestial_catalog(),
        ),
    ]

    assert (
        calculate_major_aspects(
            positions,
            [_definition()],
            orb_rules=[
                _rule(
                    source_body_type="transpersonal_planet",
                    target_body_type="transpersonal_planet",
                    orb_deg=3.0,
                    priority=700,
                )
            ],
            system_inheritance={"modern": None},
        )
        == []
    )


def test_build_natal_result_rejects_legacy_orb_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le pipeline natal refuse les anciens champs de surcharge d'orbe."""
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_positions", _positions_mock
    )
    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation._build_swisseph_houses", _houses_mock
    )
    reference = {
        "version": "1.0.0",
        "planets": [{"code": "sun", "name": "Sun"}, {"code": "mars", "name": "Mars"}],
        "signs": complete_sign_payloads(),
        "houses": [{"number": n, "name": f"House {n}"} for n in range(1, 13)],
        "aspects": [
            {
                "code": "square",
                "name": "Square",
                "angle": 90.0,
                "family": "major",
                "is_enabled": True,
                "is_major": True,
                "is_minor": False,
                "default_orb_deg": 6.0,
                "default_valence": "negative",
                "interpretive_valence": "dynamic_challenging",
                "energy_type": "friction_activation",
                "orb_luminaries": 8.0,
            }
        ],
        "aspect_orb_rules": [],
        "astral_systems": [{"code": "modern", "name": "modern", "inherits_from_system_code": None}],
        "sign_rulerships": {
            "aries": "mars",
            "taurus": "venus",
            "gemini": "mercury",
            "cancer": "moon",
            "leo": "sun",
            "virgo": "mercury",
            "libra": "venus",
            "scorpio": "mars",
            "sagittarius": "jupiter",
            "capricorn": "saturn",
            "aquarius": "saturn",
            "pisces": "jupiter",
        },
    }

    with pytest.raises(NatalCalculationError, match="aspects reference data is invalid"):
        build_natal_result(
            birth_input=_birth_input(),
            runtime_reference=runtime_reference_from_mapping(reference),
            ruleset_version="1.0.0",
            engine="swisseph",
            birth_lat=45.75,
            birth_lon=4.85,
        )
