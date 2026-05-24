# Matrice canonique des capacites et familles d'objets astrologiques runtime.
"""Expose la taxonomie interne des familles d'objets du theme."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from enum import StrEnum

from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectCapabilities,
    ChartObjectSourceType,
    ChartObjectType,
)


class ChartObjectCapabilityTaxonomyError(ValueError):
    """Erreur explicite pour les declarations de taxonomie invalides."""


class ChartObjectFamily(StrEnum):
    """Familles d'objets astrologiques gouvernees par la matrice."""

    SUN = "sun"
    MOON = "moon"
    CLASSICAL_PLANET = "classical_planet"
    MODERN_PLANET = "modern_planet"
    ANGLE = "angle"
    LUNAR_NODE = "lunar_node"
    LILITH = "lilith"
    APSIDE = "apside"
    LOT = "lot"
    ASTEROID = "asteroid"
    CHIRON = "chiron"
    MIDPOINT = "midpoint"
    FIXED_STAR = "fixed_star"


class ChartObjectDecisionStatus(StrEnum):
    """Statuts de decision autorises pour une famille d'objet."""

    ACTIVE = "active"
    NEEDS_USER_DECISION = "needs-user-decision"


@dataclass(frozen=True, slots=True)
class ChartObjectCapabilityTaxonomyEntry:
    """Ligne canonique de la matrice de capacites d'une famille d'objet."""

    object_family: ChartObjectFamily
    canonical_type: ChartObjectType
    source_kind: ChartObjectSourceType
    positionable: bool
    aspectable: bool
    interpretable: bool
    scorable: bool
    dignity_eligible: bool
    dominance_eligible: bool
    public_projection: bool
    decision_status: ChartObjectDecisionStatus
    motion_visibility: bool
    house_rulership: bool
    fixed_star_contact: bool

    @property
    def runtime_capabilities(self) -> ChartObjectCapabilities:
        """Projette la ligne vers les capacites runtime existantes."""
        return ChartObjectCapabilities(
            supports_aspects=self.aspectable,
            supports_dignities=self.dignity_eligible,
            supports_house_position=self.positionable,
            supports_visibility=self.motion_visibility,
            supports_motion=self.motion_visibility,
            supports_interpretation=self.interpretable,
            supports_dominance=self.dominance_eligible,
            supports_rulership=self.house_rulership,
            supports_fixed_star_conjunction=self.fixed_star_contact,
        )

    def to_jsonable_dict(self) -> dict[str, str | bool]:
        """Retourne une representation stable pour les preuves persistantes."""
        raw = asdict(self)
        return {
            key: value.value if isinstance(value, StrEnum) else value for key, value in raw.items()
        }


MANDATORY_CHART_OBJECT_FAMILIES = tuple(ChartObjectFamily)


def _entry(
    *,
    object_family: ChartObjectFamily,
    canonical_type: ChartObjectType,
    source_kind: ChartObjectSourceType,
    positionable: bool,
    aspectable: bool,
    interpretable: bool,
    scorable: bool = False,
    dignity_eligible: bool = False,
    dominance_eligible: bool = False,
    public_projection: bool = False,
    decision_status: ChartObjectDecisionStatus = ChartObjectDecisionStatus.ACTIVE,
    motion_visibility: bool = False,
    house_rulership: bool = False,
    fixed_star_contact: bool = False,
) -> ChartObjectCapabilityTaxonomyEntry:
    """Construit une ligne de matrice en gardant les noms explicites."""
    return ChartObjectCapabilityTaxonomyEntry(
        object_family=object_family,
        canonical_type=canonical_type,
        source_kind=source_kind,
        positionable=positionable,
        aspectable=aspectable,
        interpretable=interpretable,
        scorable=scorable,
        dignity_eligible=dignity_eligible,
        dominance_eligible=dominance_eligible,
        public_projection=public_projection,
        decision_status=decision_status,
        motion_visibility=motion_visibility,
        house_rulership=house_rulership,
        fixed_star_contact=fixed_star_contact,
    )


_PLANET_CAPABILITY_FIELDS = {
    "positionable": True,
    "aspectable": True,
    "interpretable": True,
    "scorable": True,
    "dignity_eligible": True,
    "dominance_eligible": True,
    "public_projection": True,
    "motion_visibility": True,
    "house_rulership": True,
    "fixed_star_contact": True,
}


CHART_OBJECT_CAPABILITY_TAXONOMY_DECLARATIONS: tuple[ChartObjectCapabilityTaxonomyEntry, ...] = (
    _entry(
        object_family=ChartObjectFamily.SUN,
        canonical_type=ChartObjectType.LUMINARY,
        source_kind=ChartObjectSourceType.EPHEMERIS,
        **_PLANET_CAPABILITY_FIELDS,
    ),
    _entry(
        object_family=ChartObjectFamily.MOON,
        canonical_type=ChartObjectType.LUMINARY,
        source_kind=ChartObjectSourceType.EPHEMERIS,
        **_PLANET_CAPABILITY_FIELDS,
    ),
    _entry(
        object_family=ChartObjectFamily.CLASSICAL_PLANET,
        canonical_type=ChartObjectType.PLANET,
        source_kind=ChartObjectSourceType.EPHEMERIS,
        **_PLANET_CAPABILITY_FIELDS,
    ),
    _entry(
        object_family=ChartObjectFamily.MODERN_PLANET,
        canonical_type=ChartObjectType.PLANET,
        source_kind=ChartObjectSourceType.EPHEMERIS,
        **_PLANET_CAPABILITY_FIELDS,
    ),
    _entry(
        object_family=ChartObjectFamily.ANGLE,
        canonical_type=ChartObjectType.ANGLE,
        source_kind=ChartObjectSourceType.HOUSE_SYSTEM,
        positionable=True,
        aspectable=True,
        interpretable=True,
        public_projection=True,
    ),
    _entry(
        object_family=ChartObjectFamily.LUNAR_NODE,
        canonical_type=ChartObjectType.ASTRAL_POINT,
        source_kind=ChartObjectSourceType.EPHEMERIS,
        positionable=True,
        aspectable=True,
        interpretable=True,
        public_projection=True,
    ),
    _entry(
        object_family=ChartObjectFamily.LILITH,
        canonical_type=ChartObjectType.ASTRAL_POINT,
        source_kind=ChartObjectSourceType.EPHEMERIS,
        positionable=True,
        aspectable=True,
        interpretable=True,
        decision_status=ChartObjectDecisionStatus.NEEDS_USER_DECISION,
    ),
    _entry(
        object_family=ChartObjectFamily.APSIDE,
        canonical_type=ChartObjectType.ASTRAL_POINT,
        source_kind=ChartObjectSourceType.EPHEMERIS,
        positionable=True,
        aspectable=True,
        interpretable=True,
        decision_status=ChartObjectDecisionStatus.NEEDS_USER_DECISION,
    ),
    _entry(
        object_family=ChartObjectFamily.LOT,
        canonical_type=ChartObjectType.ARABIC_PART,
        source_kind=ChartObjectSourceType.DERIVED,
        positionable=True,
        aspectable=False,
        interpretable=False,
        decision_status=ChartObjectDecisionStatus.NEEDS_USER_DECISION,
    ),
    _entry(
        object_family=ChartObjectFamily.ASTEROID,
        canonical_type=ChartObjectType.ASTRAL_POINT,
        source_kind=ChartObjectSourceType.EPHEMERIS,
        positionable=True,
        aspectable=False,
        interpretable=False,
        decision_status=ChartObjectDecisionStatus.NEEDS_USER_DECISION,
    ),
    _entry(
        object_family=ChartObjectFamily.CHIRON,
        canonical_type=ChartObjectType.ASTRAL_POINT,
        source_kind=ChartObjectSourceType.EPHEMERIS,
        positionable=True,
        aspectable=False,
        interpretable=False,
        decision_status=ChartObjectDecisionStatus.NEEDS_USER_DECISION,
    ),
    _entry(
        object_family=ChartObjectFamily.MIDPOINT,
        canonical_type=ChartObjectType.CALCULATED_POINT,
        source_kind=ChartObjectSourceType.DERIVED,
        positionable=True,
        aspectable=False,
        interpretable=False,
        decision_status=ChartObjectDecisionStatus.NEEDS_USER_DECISION,
    ),
    _entry(
        object_family=ChartObjectFamily.FIXED_STAR,
        canonical_type=ChartObjectType.FIXED_STAR,
        source_kind=ChartObjectSourceType.CATALOG,
        positionable=False,
        aspectable=False,
        interpretable=False,
    ),
)


def get_chart_object_capability_taxonomy(
    family: ChartObjectFamily | str,
) -> ChartObjectCapabilityTaxonomyEntry:
    """Retourne une famille connue ou echoue sans fallback silencieux."""
    try:
        normalized_family = ChartObjectFamily(family)
    except ValueError as exc:
        raise ChartObjectCapabilityTaxonomyError(
            f"Unknown chart object family '{family}'."
        ) from exc
    return CHART_OBJECT_CAPABILITY_TAXONOMY[normalized_family]


def list_chart_object_capability_taxonomy() -> tuple[ChartObjectCapabilityTaxonomyEntry, ...]:
    """Expose un snapshot stable de la matrice dans l'ordre obligatoire."""
    return tuple(
        CHART_OBJECT_CAPABILITY_TAXONOMY[family] for family in MANDATORY_CHART_OBJECT_FAMILIES
    )


def build_chart_object_capability_taxonomy(
    declarations: Iterable[ChartObjectCapabilityTaxonomyEntry],
) -> dict[ChartObjectFamily, ChartObjectCapabilityTaxonomyEntry]:
    """Construit une matrice valide pour les tests et futurs enrichissements."""
    return _build_taxonomy(tuple(declarations))


def _build_taxonomy(
    declarations: tuple[ChartObjectCapabilityTaxonomyEntry, ...],
) -> dict[ChartObjectFamily, ChartObjectCapabilityTaxonomyEntry]:
    """Valide les familles uniques et l'ensemble obligatoire de la matrice."""
    taxonomy: dict[ChartObjectFamily, ChartObjectCapabilityTaxonomyEntry] = {}
    duplicates: set[ChartObjectFamily] = set()
    for entry in declarations:
        if entry.object_family in taxonomy:
            duplicates.add(entry.object_family)
            continue
        taxonomy[entry.object_family] = entry
    if duplicates:
        duplicate_list = ", ".join(sorted(family.value for family in duplicates))
        raise ChartObjectCapabilityTaxonomyError(
            f"Duplicate chart object family declaration(s): {duplicate_list}."
        )

    missing = set(MANDATORY_CHART_OBJECT_FAMILIES) - set(taxonomy)
    unknown = set(taxonomy) - set(MANDATORY_CHART_OBJECT_FAMILIES)
    if missing or unknown:
        raise ChartObjectCapabilityTaxonomyError(
            "Chart object capability declarations do not match mandatory families."
        )
    return taxonomy


CHART_OBJECT_CAPABILITY_TAXONOMY = _build_taxonomy(CHART_OBJECT_CAPABILITY_TAXONOMY_DECLARATIONS)
