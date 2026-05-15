"""Contrats typés pour le calcul runtime des aspects astrologiques."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog

PLANET_BODY_TYPES = frozenset(
    {"luminary", "personal_planet", "social_planet", "transpersonal_planet"}
)


def _required_text(value: object, field_name: str) -> str:
    """Normalise une valeur textuelle obligatoire."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip().lower()


def _required_float(value: object, field_name: str) -> float:
    """Normalise une valeur flottante obligatoire et finie."""
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be numeric") from error
    if not isfinite(parsed):
        raise ValueError(f"{field_name} must be finite")
    return parsed


def _optional_text(value: object, field_name: str) -> str | None:
    """Normalise une valeur textuelle optionnelle."""
    if value is None:
        return None
    return _required_text(value, field_name)


@dataclass(frozen=True, slots=True)
class AspectDefinitionRuntimeData:
    """Définition d'aspect issue du référentiel canonique."""

    code: str
    angle: float
    family: str
    default_orb_deg: float
    is_enabled: bool
    is_major: bool
    is_minor: bool
    default_valence: str
    interpretive_valence: str
    energy_type: str
    system_code: str = "modern"

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> AspectDefinitionRuntimeData:
        """Valide et convertit un payload référentiel en contrat runtime."""
        forbidden_fields = {
            "orb_" + "luminaries_override_deg",
            "orb_" + "pair_overrides",
            "orb_" + "luminaries",
            "orb_" + "pairs",
            "orb_" + "overrides",
        }
        present_forbidden_fields = forbidden_fields & set(payload)
        if present_forbidden_fields:
            raise ValueError(
                "legacy aspect orb fields are forbidden: "
                + ", ".join(sorted(present_forbidden_fields))
            )
        family = _required_text(payload.get("family"), "family")
        default_orb = _required_float(payload.get("default_orb_deg"), "default_orb_deg")
        is_major = bool(payload.get("is_major", family == "major"))
        is_minor = bool(payload.get("is_minor", family == "minor"))
        return cls(
            code=_required_text(payload.get("code"), "code"),
            angle=_required_float(payload.get("angle"), "angle"),
            family=family,
            default_orb_deg=default_orb,
            is_enabled=bool(payload.get("is_enabled", True)),
            is_major=is_major,
            is_minor=is_minor,
            default_valence=_required_text(payload.get("default_valence"), "default_valence"),
            interpretive_valence=_required_text(
                payload.get("interpretive_valence"), "interpretive_valence"
            ),
            energy_type=_required_text(payload.get("energy_type"), "energy_type"),
            system_code=_required_text(payload.get("system_code", "modern"), "system_code"),
        )


@dataclass(frozen=True, slots=True)
class AspectOrbRuleRuntimeData:
    """Règle d'orbe ciblée issue de `astral_aspect_orb_rules`."""

    aspect_code: str
    system_code: str
    calculation_context: str
    source_body_type: str
    target_body_type: str
    orb_deg: float
    priority: int
    is_enabled: bool
    source_planet_code: str | None = None
    source_point_code: str | None = None
    target_planet_code: str | None = None
    target_point_code: str | None = None

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> AspectOrbRuleRuntimeData:
        """Valide et convertit une règle d'orbe en contrat runtime."""
        priority_raw = payload.get("priority", 0)
        if isinstance(priority_raw, bool):
            raise ValueError("priority must be numeric")
        try:
            priority = int(priority_raw)
        except (TypeError, ValueError) as error:
            raise ValueError("priority must be numeric") from error
        return cls(
            aspect_code=_required_text(payload.get("aspect_code"), "aspect_code"),
            system_code=_required_text(payload.get("system_code"), "system_code"),
            calculation_context=_required_text(
                payload.get("calculation_context"), "calculation_context"
            ),
            source_body_type=_required_text(
                payload.get("source_body_type", "any"), "source_body_type"
            ),
            target_body_type=_required_text(
                payload.get("target_body_type", "any"), "target_body_type"
            ),
            source_planet_code=_optional_text(
                payload.get("source_planet_code"), "source_planet_code"
            ),
            source_point_code=_optional_text(payload.get("source_point_code"), "source_point_code"),
            target_planet_code=_optional_text(
                payload.get("target_planet_code"), "target_planet_code"
            ),
            target_point_code=_optional_text(payload.get("target_point_code"), "target_point_code"),
            orb_deg=_required_float(payload.get("orb_deg"), "orb_deg"),
            priority=priority,
            is_enabled=bool(payload.get("is_enabled", True)),
        )


@dataclass(frozen=True, slots=True)
class AspectBodyRuntimeData:
    """Corps ou point astrologique normalisé pour une règle d'aspect."""

    code: str
    body_type: str
    longitude: float | None = None

    @classmethod
    def from_position(
        cls,
        payload: dict[str, object],
        celestial_catalog: CelestialRuntimeCatalog,
    ) -> AspectBodyRuntimeData:
        """Valide une position planétaire d'entrée."""
        code = _required_text(payload.get("planet_code"), "planet_code")
        return cls(
            code=code,
            body_type=celestial_catalog.body_type_for_code(code),
            longitude=_required_float(payload.get("longitude"), "longitude"),
        )

    @classmethod
    def from_code(
        cls,
        code: str,
        celestial_catalog: CelestialRuntimeCatalog,
    ) -> AspectBodyRuntimeData:
        """Construit un participant depuis son code canonique."""
        normalized_code = _required_text(code, "body_code")
        return cls(
            code=normalized_code,
            body_type=celestial_catalog.body_type_for_code(normalized_code),
        )


@dataclass(frozen=True, slots=True)
class AspectCalculationResult:
    """Résultat calculé avec métadonnées référentielles transportées."""

    aspect_code: str
    planet_a: str
    planet_b: str
    angle: float
    orb: float
    orb_used: float
    orb_max: float
    family: str
    is_major: bool
    is_minor: bool
    default_valence: str
    interpretive_valence: str
    energy_type: str
    chart_a: str | None = None
    chart_b: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Projette le contrat vers le payload historique contrôlé."""
        payload: dict[str, Any] = {
            "aspect_code": self.aspect_code,
            "planet_a": self.planet_a,
            "planet_b": self.planet_b,
            "angle": self.angle,
            "orb": self.orb,
            "orb_used": self.orb_used,
            "orb_max": self.orb_max,
            "family": self.family,
            "is_major": self.is_major,
            "is_minor": self.is_minor,
            "default_valence": self.default_valence,
            "interpretive_valence": self.interpretive_valence,
            "energy_type": self.energy_type,
        }
        if self.chart_a is not None:
            payload["chart_a"] = self.chart_a
        if self.chart_b is not None:
            payload["chart_b"] = self.chart_b
        return payload
