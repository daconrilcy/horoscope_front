"""Factories de tests pour le referentiel runtime astrologique.

Les tests construisent des contrats immutables complets au lieu de faire passer
des dictionnaires metier dans le domaine.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference
from app.infra.db.repositories.astrology_runtime_reference_mapper import (
    AstrologyRuntimeReferenceMapper,
)

_CANONICAL_SIGN_CODES = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)

_CANONICAL_SIGN_PROFILES = {
    "aries": {"element": "fire", "modality": "cardinal", "polarity": "yang"},
    "taurus": {"element": "earth", "modality": "fixed", "polarity": "yin"},
    "gemini": {"element": "air", "modality": "mutable", "polarity": "yang"},
    "cancer": {"element": "water", "modality": "cardinal", "polarity": "yin"},
    "leo": {"element": "fire", "modality": "fixed", "polarity": "yang"},
    "virgo": {"element": "earth", "modality": "mutable", "polarity": "yin"},
    "libra": {"element": "air", "modality": "cardinal", "polarity": "yang"},
    "scorpio": {"element": "water", "modality": "fixed", "polarity": "yin"},
    "sagittarius": {"element": "fire", "modality": "mutable", "polarity": "yang"},
    "capricorn": {"element": "earth", "modality": "cardinal", "polarity": "yin"},
    "aquarius": {"element": "air", "modality": "fixed", "polarity": "yang"},
    "pisces": {"element": "water", "modality": "mutable", "polarity": "yin"},
}


def complete_sign_payloads(codes: Iterable[str] = _CANONICAL_SIGN_CODES) -> list[dict[str, object]]:
    """Construit des signes de fixture avec profils structurels explicites."""
    signs: list[dict[str, object]] = []
    for raw_code in codes:
        code = raw_code.strip().lower()
        profile = _CANONICAL_SIGN_PROFILES.get(code)
        if profile is None:
            raise ValueError(f"unknown sign fixture code: {raw_code}")
        signs.append({"code": code, "name": code.title(), **profile})
    return signs


def runtime_reference_from_mapping(
    payload: Mapping[str, object],
    *,
    reference_version_id: int = 1,
) -> AstrologyRuntimeReference:
    """Convertit un ancien payload de fixture en runtime reference type."""
    payload = dict(payload)
    payload["signs"] = _complete_sign_payload(payload.get("signs"))
    sign_rulerships = payload.get("sign_rulerships")
    if not isinstance(sign_rulerships, Mapping):
        sign_rulerships = {
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
        }
    version = str(payload.get("version") or "test")
    if not payload.get("aspect_orb_rules"):
        payload["aspect_orb_rules"] = list(_default_aspect_orb_rules(payload))
    if not payload.get("house_axes"):
        payload["house_axes"] = [
            {
                "house_number": number,
                "opposite_house": number + 6 if number <= 6 else number - 6,
                "theme": f"axis_{number}",
            }
            for number in range(1, 13)
        ]
    return AstrologyRuntimeReferenceMapper().map_payload(
        reference_version_id=reference_version_id,
        reference_version=version,
        payload=payload,
        dignities=tuple(
            {
                "sign_code": sign,
                "planet_code": planet,
                "dignity_type": "domicile",
                "system": "traditional",
                "weight": 1.0,
                "is_primary": True,
            }
            for sign, planet in sign_rulerships.items()
        ),
        sign_rulerships={str(sign): str(planet) for sign, planet in sign_rulerships.items()},
        planet_definitions={
            "sun": {"body_class": "luminary", "is_luminary": True},
            "moon": {"body_class": "luminary", "is_luminary": True},
            "mercury": {"body_class": "personal_planet", "is_luminary": False},
            "venus": {"body_class": "personal_planet", "is_luminary": False},
            "mars": {"body_class": "personal_planet", "is_luminary": False},
            "jupiter": {"body_class": "social_planet", "is_luminary": False},
            "saturn": {"body_class": "social_planet", "is_luminary": False},
            "uranus": {"body_class": "transpersonal_planet", "is_luminary": False},
            "neptune": {"body_class": "transpersonal_planet", "is_luminary": False},
            "pluto": {"body_class": "transpersonal_planet", "is_luminary": False},
        },
        angle_points=(
            {
                "code": "asc",
                "short_label": "ASC",
                "full_name": "Ascendant",
                "axis": "horizontal",
                "associated_house": 1,
            },
            {
                "code": "dsc",
                "short_label": "DSC",
                "full_name": "Descendant",
                "axis": "horizontal",
                "associated_house": 7,
            },
            {
                "code": "mc",
                "short_label": "MC",
                "full_name": "Midheaven",
                "axis": "vertical",
                "associated_house": 10,
            },
            {
                "code": "ic",
                "short_label": "IC",
                "full_name": "Imum Coeli",
                "axis": "vertical",
                "associated_house": 4,
            },
        ),
        house_systems=(
            {"code": "placidus", "name": "Placidus", "is_active": True},
            {"code": "whole_sign", "name": "Whole Sign", "is_active": True},
            {"code": "equal", "name": "Equal", "is_active": True},
            {"code": "porphyry", "name": "Porphyry", "is_active": True},
        ),
    )


def _default_aspect_orb_rules(payload: Mapping[str, object]) -> tuple[dict[str, object], ...]:
    """Crée des règles d'orbe neutres pour les anciennes fixtures sans table dédiée."""
    aspects = payload.get("aspects")
    if not isinstance(aspects, list):
        return ()

    rules: list[dict[str, object]] = []
    for item in aspects:
        if not isinstance(item, Mapping):
            continue
        code = item.get("code")
        orb = item.get("default_orb_deg")
        if code is None or orb is None:
            continue
        rules.append(
            {
                "aspect_code": str(code),
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "any",
                "source_planet_code": None,
                "source_point_code": None,
                "target_body_type": "any",
                "target_planet_code": None,
                "target_point_code": None,
                "orb_deg": max(float(orb), 0.1),
                "priority": 1,
                "is_enabled": True,
            }
        )
    return tuple(rules)


def _complete_sign_payload(raw_signs: object) -> list[dict[str, object]]:
    """Complete les anciennes fixtures partielles avec le catalogue zodiacal canonique."""
    existing: dict[str, dict[str, object]] = {}
    if isinstance(raw_signs, list):
        for item in raw_signs:
            if not isinstance(item, Mapping):
                continue
            code = str(item.get("code") or "").strip().lower()
            if code:
                existing[code] = dict(item)

    signs: list[dict[str, object]] = []
    for code in _CANONICAL_SIGN_CODES:
        payload = dict(existing.get(code) or {})
        payload.setdefault("code", code)
        payload.setdefault("name", code.title())
        missing_profile_fields = {
            field_name
            for field_name in ("element", "modality", "polarity")
            if not str(payload.get(field_name) or "").strip()
        }
        if missing_profile_fields:
            raise ValueError(
                f"sign fixture {code} requires profile fields: "
                + ",".join(sorted(missing_profile_fields))
            )
        signs.append(payload)
    return signs


def complete_reference() -> AstrologyRuntimeReference:
    """Retourne une reference minimale complete pour les tests de garde."""
    planets = (
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    )
    return runtime_reference_from_mapping(
        {
            "version": "test",
            "planets": [{"code": code, "name": code.title()} for code in planets],
            "signs": complete_sign_payloads(),
            "houses": [{"number": number, "name": f"House {number}"} for number in range(1, 13)],
            "house_axes": [
                {
                    "house_number": number,
                    "opposite_house": number + 6 if number <= 6 else number - 6,
                    "theme": f"axis_{number}",
                }
                for number in range(1, 13)
            ],
            "astral_systems": [
                {"code": "traditional", "inherits_from_system_code": None},
                {"code": "modern", "inherits_from_system_code": "traditional"},
            ],
            "aspects": [
                {
                    "code": "conjunction",
                    "name": "Conjunction",
                    "angle": 0.0,
                    "family": "major",
                    "is_enabled": True,
                    "is_major": True,
                    "is_minor": False,
                    "default_orb_deg": 8.0,
                    "default_valence": "contextual",
                    "interpretive_valence": "fusion",
                    "energy_type": "fusion",
                }
            ],
            "aspect_orb_rules": [
                {
                    "aspect_code": "conjunction",
                    "system_code": "modern",
                    "calculation_context": "natal",
                    "source_body_type": "any",
                    "source_planet_code": None,
                    "source_point_code": None,
                    "target_body_type": "any",
                    "target_planet_code": None,
                    "target_point_code": None,
                    "orb_deg": 8.0,
                    "priority": 1,
                    "is_enabled": True,
                }
            ],
        }
    )


def missing_planet_definition() -> AstrologyRuntimeReference:
    """Retourne une reference invalide sans planete requise."""
    reference = complete_reference()
    return type(reference)(
        reference_version_id=reference.reference_version_id,
        reference_version=reference.reference_version,
        planets=type(reference.planets)(items=reference.planets.items[1:]),
        signs=reference.signs,
        aspects=reference.aspects,
        houses=reference.houses,
        house_axes=reference.house_axes,
        dignities=reference.dignities,
        angle_points=reference.angle_points,
        house_systems=reference.house_systems,
        systems=reference.systems,
    )


def missing_dignity() -> AstrologyRuntimeReference:
    """Retourne une reference complete avec dignites absentes pour tests negatifs."""
    reference = complete_reference()
    return type(reference)(
        reference_version_id=reference.reference_version_id,
        reference_version=reference.reference_version,
        planets=reference.planets,
        signs=reference.signs,
        aspects=reference.aspects,
        houses=reference.houses,
        house_axes=reference.house_axes,
        dignities=type(reference.dignities)(items=(), sign_rulerships={}),
        angle_points=reference.angle_points,
        house_systems=reference.house_systems,
        systems=reference.systems,
    )


def invalid_orphan_aspect_rule() -> AstrologyRuntimeReference:
    """Retourne une reference minimale destinee aux tests d'orbe orpheline."""
    reference = complete_reference()
    orphan_rule = type(reference.aspects.orb_rules[0])(
        aspect_code="nonexistent",
        system_code=reference.aspects.orb_rules[0].system_code,
        calculation_context=reference.aspects.orb_rules[0].calculation_context,
        source_body_type=reference.aspects.orb_rules[0].source_body_type,
        source_planet_code=reference.aspects.orb_rules[0].source_planet_code,
        source_point_code=reference.aspects.orb_rules[0].source_point_code,
        target_body_type=reference.aspects.orb_rules[0].target_body_type,
        target_planet_code=reference.aspects.orb_rules[0].target_planet_code,
        target_point_code=reference.aspects.orb_rules[0].target_point_code,
        orb_deg=reference.aspects.orb_rules[0].orb_deg,
        priority=reference.aspects.orb_rules[0].priority,
        is_enabled=reference.aspects.orb_rules[0].is_enabled,
    )
    return type(reference)(
        reference_version_id=reference.reference_version_id,
        reference_version=reference.reference_version,
        planets=reference.planets,
        signs=reference.signs,
        aspects=type(reference.aspects)(items=reference.aspects.items, orb_rules=(orphan_rule,)),
        houses=reference.houses,
        house_axes=reference.house_axes,
        dignities=reference.dignities,
        angle_points=reference.angle_points,
        house_systems=reference.house_systems,
        systems=reference.systems,
    )


def minimal_valid_natal_reference() -> AstrologyRuntimeReference:
    """Retourne la reference minimale valide pour le calcul natal."""
    return complete_reference()
