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
class DignityScoreProfileReferenceData:
    """Profil de scoring de dignites disponible au runtime."""

    code: str
    tradition: str
    is_default: bool


@dataclass(frozen=True, slots=True)
class DignityTypeReferenceData:
    """Type de dignite canonique disponible dans le referentiel runtime."""

    code: str
    label: str
    description: str
    sort_order: int


@dataclass(frozen=True, slots=True)
class DignitySystemReferenceData:
    """Systeme de termes, faces ou decans disponible au runtime."""

    code: str
    label: str
    description: str | None
    sort_order: int


@dataclass(frozen=True, slots=True)
class DignityScoreWeightReferenceData:
    """Poids factuel applique a un type de dignite par profil."""

    dignity_type_code: str
    score_value: float
    functional_weight: float
    expression_weight: float
    intensity_weight: float
    condition_visibility: float
    condition_stability: float
    condition_coherence: float
    condition_support: float
    condition_constraint: float


@dataclass(frozen=True, slots=True)
class PlanetConditionSignalProfileReferenceData:
    """Profil runtime versionne d'un signal de condition planetaire."""

    condition_axis: str
    level_min: float
    level_max: float
    signal_code: str
    signal_label: str
    signal_level: str
    interpretation_use: str
    priority_weight: float
    prompt_hint: str
    reference_version: str


@dataclass(frozen=True, slots=True)
class DominanceFactorTypeReferenceData:
    """Type runtime d'un facteur de dominance planetaire."""

    code: str
    label: str
    category: str
    default_weight: float
    sort_order: int
    is_active: bool
    description: str
    reference_version: str

    def __post_init__(self) -> None:
        """Valide le contrat minimal d'un facteur charge depuis le runtime."""
        for field_name in ("code", "label", "category", "description", "reference_version"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"dominance factor requires {field_name}")
        if self.default_weight < 0.0:
            raise ValueError("dominance factor default_weight must be positive")
        if self.sort_order < 1:
            raise ValueError("dominance factor sort_order must be positive")


@dataclass(frozen=True, slots=True)
class DominanceScoreProfileReferenceData:
    """Profil versionne de scoring des dominantes planetaires."""

    code: str
    label: str
    tradition_code: str
    description: str
    reference_version_code: str
    is_active: bool

    def __post_init__(self) -> None:
        """Valide les champs stables du profil de scoring."""
        for field_name in (
            "code",
            "label",
            "tradition_code",
            "description",
            "reference_version_code",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"dominance score profile requires {field_name}")


@dataclass(frozen=True, slots=True)
class DominanceScoreWeightReferenceData:
    """Ponderation runtime d'un facteur pour un profil de dominance."""

    score_profile_code: str
    factor_type_code: str
    weight: float
    min_value: float
    max_value: float
    normalization_method: str
    notes: str

    def __post_init__(self) -> None:
        """Valide les bornes et la ponderation d'un facteur."""
        for field_name in ("score_profile_code", "factor_type_code", "normalization_method"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"dominance score weight requires {field_name}")
        if self.weight < 0.0:
            raise ValueError("dominance score weight must be positive")
        if self.max_value <= self.min_value:
            raise ValueError("dominance score weight max_value must exceed min_value")


@dataclass(frozen=True, slots=True)
class DominanceReferenceSet:
    """Referentiel complet des facteurs et profils de dominance."""

    factor_types: tuple[DominanceFactorTypeReferenceData, ...]
    score_profiles: tuple[DominanceScoreProfileReferenceData, ...]
    score_weights: tuple[DominanceScoreWeightReferenceData, ...]

    @property
    def default_score_profile(self) -> DominanceScoreProfileReferenceData:
        """Retourne le profil actif par defaut pour la v1."""
        for profile in self.score_profiles:
            if profile.is_active:
                return profile
        raise ValueError("dominance reference requires an active score profile")

    def weights_for_profile(
        self, score_profile_code: str
    ) -> tuple[DominanceScoreWeightReferenceData, ...]:
        """Retourne les poids d'un profil dans l'ordre des facteurs actifs."""
        factor_order = {factor.code: factor.sort_order for factor in self.factor_types}
        weights = tuple(
            weight
            for weight in self.score_weights
            if weight.score_profile_code == score_profile_code
        )
        return tuple(sorted(weights, key=lambda item: factor_order.get(item.factor_type_code, 0)))


@dataclass(frozen=True, slots=True)
class EssentialDignityRuleReferenceData:
    """Regle essentielle reliant une planete, un signe et une plage de degres."""

    planet_code: str
    sign_code: str
    dignity_type_code: str
    degree_start: float
    degree_end: float
    system_code: str


@dataclass(frozen=True, slots=True)
class TriplicityRulerReferenceData:
    """Attribution de maitre de triplicite par element, secte et role."""

    element_code: str
    sect_code: str
    planet_code: str
    role_code: str
    system_code: str


@dataclass(frozen=True, slots=True)
class TermBoundReferenceData:
    """Borne de terme pour un signe et un systeme de termes."""

    term_system_code: str
    sign_code: str
    planet_code: str
    degree_start: float
    degree_end: float
    order_index: int


@dataclass(frozen=True, slots=True)
class FaceDecanReferenceData:
    """Face ou decan pour un signe et une tranche de degres."""

    decan_system_code: str
    sign_code: str
    planet_code: str
    decan_index: int
    degree_start: float
    degree_end: float


@dataclass(frozen=True, slots=True)
class DignityConditionValue:
    """Valeur de condition accidentelle normalisee sans dictionnaire libre."""

    key: str
    value: str | int | float | tuple[str | int | float, ...]


@dataclass(frozen=True, slots=True)
class AccidentalDignityRuleReferenceData:
    """Regle accidentelle normalisee depuis la DB pour le calcul pur."""

    dignity_type_code: str
    planet_code: str | None
    condition_schema_code: str
    conditions: tuple[DignityConditionValue, ...]
    system_code: str


@dataclass(frozen=True, slots=True)
class PlanetDignityReferenceSet:
    """Referentiel avance de dignites planetaires consomme par les calculateurs."""

    essential_types: tuple[DignityTypeReferenceData, ...]
    accidental_types: tuple[DignityTypeReferenceData, ...]
    term_systems: tuple[DignitySystemReferenceData, ...]
    decan_systems: tuple[DignitySystemReferenceData, ...]
    score_profiles: tuple[DignityScoreProfileReferenceData, ...]
    essential_weights: Mapping[str, tuple[DignityScoreWeightReferenceData, ...]]
    accidental_weights: Mapping[str, tuple[DignityScoreWeightReferenceData, ...]]
    essential_rules: tuple[EssentialDignityRuleReferenceData, ...]
    triplicity_rulers: tuple[TriplicityRulerReferenceData, ...]
    term_bounds: tuple[TermBoundReferenceData, ...]
    face_decans: tuple[FaceDecanReferenceData, ...]
    accidental_rules: tuple[AccidentalDignityRuleReferenceData, ...]

    def __post_init__(self) -> None:
        """Fige les index de poids pour eviter toute mutation par les calculateurs."""
        object.__setattr__(
            self,
            "essential_weights",
            MappingProxyType(
                {
                    str(profile): tuple(weights)
                    for profile, weights in self.essential_weights.items()
                }
            ),
        )
        object.__setattr__(
            self,
            "accidental_weights",
            MappingProxyType(
                {
                    str(profile): tuple(weights)
                    for profile, weights in self.accidental_weights.items()
                }
            ),
        )

    @property
    def default_score_profile(self) -> str:
        """Retourne le profil par defaut declare par le referentiel."""
        for profile in self.score_profiles:
            if profile.is_default:
                return profile.code
        raise ValueError("dignity reference requires a default score profile")


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
    dignity_reference: PlanetDignityReferenceSet
    condition_signal_profiles: tuple[PlanetConditionSignalProfileReferenceData, ...]
    dominance_factor_types: tuple[DominanceFactorTypeReferenceData, ...]
    dominance_reference: DominanceReferenceSet
    angle_points: AnglePointReferenceSet
    astral_points: AstralPointReferenceSet
    house_systems: HouseSystemReferenceSet
    systems: AstrologySystemReferenceSet
