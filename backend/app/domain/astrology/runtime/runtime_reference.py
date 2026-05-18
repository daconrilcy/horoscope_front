"""Contrats immutables du referentiel astrologique runtime.

Ce module definit la photographie typée que le domaine consomme pendant les
calculs astrologiques. Les payloads SQL/JSON libres restent confines a l'infra.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class PlanetReferenceData:
    """Definition runtime minimale d'une planete canonique."""

    code: str
    name: str
    swe_id: int = 0
    body_class: str | None = None
    is_luminary: bool = False


@dataclass(frozen=True, slots=True)
class PlanetReferenceSet:
    """Collection immutable des planetes disponibles pour le calcul."""

    items: tuple[PlanetReferenceData, ...]

    @property
    def codes(self) -> tuple[str, ...]:
        """Retourne les codes planetaires dans l'ordre runtime."""
        return tuple(item.code for item in self.items)


@dataclass(frozen=True, slots=True)
class SignReferenceData:
    """Definition runtime minimale d'un signe astrologique."""

    code: str
    name: str
    element: str
    modality: str
    polarity: str

    def __post_init__(self) -> None:
        """Valide que le profil structurel est explicitement source."""
        for field_name in ("code", "name", "element", "modality", "polarity"):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"sign reference requires {field_name}")
            if value.strip().lower() == "unknown":
                raise ValueError(f"sign reference rejects unknown {field_name}")


@dataclass(frozen=True, slots=True)
class SignReferenceSet:
    """Collection immutable des signes astrologiques."""

    items: tuple[SignReferenceData, ...]

    @property
    def codes(self) -> tuple[str, ...]:
        """Retourne les codes de signes dans l'ordre runtime."""
        return tuple(item.code for item in self.items)


@dataclass(frozen=True, slots=True)
class HouseReferenceData:
    """Definition runtime minimale d'une maison astrologique."""

    number: int
    name: str


@dataclass(frozen=True, slots=True)
class HouseReferenceSet:
    """Collection immutable des maisons astrologiques."""

    items: tuple[HouseReferenceData, ...]

    @property
    def numbers(self) -> tuple[int, ...]:
        """Retourne les numeros de maisons disponibles."""
        return tuple(item.number for item in self.items)


@dataclass(frozen=True, slots=True)
class HouseAxisReferenceData:
    """Axe maison opposee charge depuis le referentiel canonique."""

    house_number: int
    opposite_house: int
    theme: str


@dataclass(frozen=True, slots=True)
class AspectReferenceData:
    """Definition runtime d'un aspect active par le referentiel."""

    code: str
    name: str
    angle: float
    family: str
    is_enabled: bool
    is_major: bool
    is_minor: bool
    default_orb_deg: float | None
    default_valence: str
    interpretive_valence: str
    energy_type: str
    legacy_orb_fields: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AspectOrbRuleReferenceData:
    """Regle d'orbe d'aspect prete pour le calcul."""

    aspect_code: str
    system_code: str
    calculation_context: str
    source_body_type: str
    source_planet_code: str | None
    source_point_code: str | None
    target_body_type: str
    target_planet_code: str | None
    target_point_code: str | None
    orb_deg: float
    priority: int
    is_enabled: bool


@dataclass(frozen=True, slots=True)
class AspectReferenceSet:
    """Collection immutable des aspects et regles d'orbes."""

    items: tuple[AspectReferenceData, ...]
    orb_rules: tuple[AspectOrbRuleReferenceData, ...]


@dataclass(frozen=True, slots=True)
class DignityReferenceData:
    """Dignite d'une planete dans un signe pour un systeme."""

    sign_code: str
    planet_code: str
    dignity_type: str
    system: str
    weight: float
    is_primary: bool


@dataclass(frozen=True, slots=True)
class DignityReferenceSet:
    """Collection immutable des dignites et maitrises."""

    items: tuple[DignityReferenceData, ...]
    sign_rulerships: Mapping[str, str]

    def __post_init__(self) -> None:
        """Fige la vue signe vers maitre pour eviter les mutations runtime."""
        object.__setattr__(self, "sign_rulerships", MappingProxyType(dict(self.sign_rulerships)))


@dataclass(frozen=True, slots=True)
class AnglePointReferenceData:
    """Point d'angle structurel du theme."""

    code: str
    short_label: str
    full_name: str
    axis: str
    associated_house: int


@dataclass(frozen=True, slots=True)
class AnglePointReferenceSet:
    """Collection immutable des points d'angle."""

    items: tuple[AnglePointReferenceData, ...]


@dataclass(frozen=True, slots=True)
class AstralPointAliasRuntime:
    """Alias ou clé moteur attaché à un point astral canonique."""

    alias: str
    language_code: str
    source: str
    variant_code: str | None = None
    engine_key: str | None = None
    is_primary: bool = False


@dataclass(frozen=True, slots=True)
class AstralPointVariantRuntime:
    """Variante de calcul typée pour un point astral."""

    variant_code: str
    display_name: str
    calculation_mode: str
    engine_key: str | None
    is_default: bool


@dataclass(frozen=True, slots=True)
class AstralPointRuntime:
    """Point astral calculable issu des tables `astral_point_*`."""

    code: str
    display_name: str
    family_code: str
    astronomical_type: str
    is_physical_body: bool
    default_variant_code: str | None
    variants: tuple[AstralPointVariantRuntime, ...]
    aliases: tuple[AstralPointAliasRuntime, ...]


@dataclass(frozen=True, slots=True)
class AstralPointReferenceSet:
    """Collection immutable des points astraux disponibles au runtime natal."""

    items: tuple[AstralPointRuntime, ...]

    @property
    def codes(self) -> tuple[str, ...]:
        """Retourne les codes de points astraux dans l'ordre runtime."""
        return tuple(item.code for item in self.items)


@dataclass(frozen=True, slots=True)
class HouseSystemReferenceData:
    """Systeme de maisons disponible pour le calcul."""

    code: str
    name: str
    is_active: bool


@dataclass(frozen=True, slots=True)
class HouseSystemReferenceSet:
    """Collection immutable des systemes de maisons."""

    items: tuple[HouseSystemReferenceData, ...]


@dataclass(frozen=True, slots=True)
class AstrologySystemReferenceData:
    """Systeme astrologique et sa relation d'heritage."""

    code: str
    inherits_from_system_code: str | None


@dataclass(frozen=True, slots=True)
class AstrologySystemReferenceSet:
    """Collection immutable des systemes astrologiques."""

    items: tuple[AstrologySystemReferenceData, ...]

    @property
    def inheritance(self) -> Mapping[str, str | None]:
        """Retourne la carte d'heritage des systemes."""
        return MappingProxyType({item.code: item.inherits_from_system_code for item in self.items})


@dataclass(frozen=True, slots=True)
class AstrologyRuntimeReference:
    """Photographie runtime complete du referentiel astrologique."""

    reference_version_id: int
    reference_version: str
    planets: PlanetReferenceSet
    signs: SignReferenceSet
    aspects: AspectReferenceSet
    houses: HouseReferenceSet
    house_axes: tuple[HouseAxisReferenceData, ...]
    dignities: DignityReferenceSet
    angle_points: AnglePointReferenceSet
    astral_points: AstralPointReferenceSet
    house_systems: HouseSystemReferenceSet
    systems: AstrologySystemReferenceSet
