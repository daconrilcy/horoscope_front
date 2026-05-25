# Runtime interne canonique du chemin temporel transit_chart_v1.
"""Construit le payload runtime transit sans exposition API ni interpretation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
from typing import Protocol

from app.domain.astrology.builders.aspect_runtime_builder import (
    build_aspect_structural_runtime_data,
)
from app.domain.astrology.builders.chart_object_runtime_builder import (
    AstralPointChartObjectSource,
    HouseChartObjectSource,
    PlanetChartObjectSource,
    build_chart_object_runtime_data,
)
from app.domain.astrology.runtime.aspect_runtime_data import AspectStructuralRuntimeData
from app.domain.astrology.runtime.astrology_doctrine_governance import (
    get_astrology_doctrine_governance,
)
from app.domain.astrology.runtime.astrology_graph_family_registry import (
    AstrologyGraphFamilyOwner,
    get_astrology_graph_family,
)
from app.domain.astrology.runtime.astronomical_proof import (
    CS253_GATE_MARKER,
    PRODUCTION_ASTRONOMY_MODE,
    PRODUCTION_TOLERANCE,
    SENSITIVE_GOLDEN_CASES,
)
from app.domain.astrology.runtime.chart_object_runtime_data import ChartObjectRuntimeData
from app.domain.astrology.runtime.temporal_technique_selection import (
    SELECTED_TEMPORAL_FAMILY_CODE,
)

TRANSIT_CHART_RUNTIME_CONTRACT_VERSION = "transit-chart-runtime-v1"
TRANSIT_CHART_RUNTIME_PUBLIC_EXPOSURE = "blocked"
TRANSIT_CHART_RUNTIME_TRACE_KEYS = (
    "run_id",
    "family_code",
    "contract_version",
    "transiting_object_codes",
    "relationship_codes",
    "proof_ref_keys",
    "doctrine_limit_keys",
    "public_exposure",
)


class TransitAspectRuntimeSource(Protocol):
    """Contrat minimal d'une relation transit vers natal deja calculee."""

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


@dataclass(frozen=True, slots=True)
class TransitToNatalRelationshipRuntimeData:
    """Relation structurelle entre un objet transitant et un objet natal."""

    relationship_code: str
    transit_object_code: str
    natal_object_code: str
    aspect: AspectStructuralRuntimeData
    source: str


@dataclass(frozen=True, slots=True)
class TransitChartRuntimeTrace:
    """Trace diagnostique interne sans inputs bruts ni texte narratif."""

    keys: tuple[str, ...]
    run_id: str
    family_code: str
    contract_version: str
    transiting_object_codes: tuple[str, ...]
    relationship_codes: tuple[str, ...]
    proof_ref_keys: tuple[str, ...]
    doctrine_limit_keys: tuple[str, ...]
    public_exposure: str


@dataclass(frozen=True, slots=True)
class TransitChartRuntimePayload:
    """Payload interne complet du runtime transit_chart_v1."""

    family_code: str
    transiting_chart_objects: tuple[ChartObjectRuntimeData, ...]
    transit_to_natal_relationships: tuple[TransitToNatalRelationshipRuntimeData, ...]
    astronomical_proof_refs: tuple[str, ...]
    doctrine_limits: tuple[str, ...]
    trace: TransitChartRuntimeTrace
    public_exposure: str


def build_internal_transit_chart_runtime(
    *,
    planet_positions: Sequence[PlanetChartObjectSource],
    houses: Sequence[HouseChartObjectSource],
    natal_chart_objects: Sequence[ChartObjectRuntimeData],
    transit_aspects: Sequence[TransitAspectRuntimeSource],
    run_id: str,
    astral_points: Sequence[AstralPointChartObjectSource] = (),
) -> TransitChartRuntimePayload:
    """Construit le runtime transit interne depuis les primitives existantes."""
    _validate_temporal_runtime_owner()
    if not run_id.strip():
        raise ValueError("transit runtime requires an internal run_id")

    transiting_objects = build_chart_object_runtime_data(
        planet_positions=planet_positions,
        astral_points=astral_points,
        houses=houses,
        fixed_stars=(),
    )
    transiting_objects = _block_fixed_star_output(transiting_objects)
    relationships = _build_relationships(transit_aspects)
    _validate_relationship_objects(
        relationships=relationships,
        transiting_objects=transiting_objects,
        natal_chart_objects=natal_chart_objects,
    )
    proof_refs = _astronomical_proof_refs()
    doctrine_limits = _doctrine_limits()
    trace = TransitChartRuntimeTrace(
        keys=TRANSIT_CHART_RUNTIME_TRACE_KEYS,
        run_id=run_id,
        family_code=SELECTED_TEMPORAL_FAMILY_CODE,
        contract_version=TRANSIT_CHART_RUNTIME_CONTRACT_VERSION,
        transiting_object_codes=tuple(obj.code for obj in transiting_objects),
        relationship_codes=tuple(rel.relationship_code for rel in relationships),
        proof_ref_keys=proof_refs,
        doctrine_limit_keys=tuple(limit.split(":", maxsplit=1)[0] for limit in doctrine_limits),
        public_exposure=TRANSIT_CHART_RUNTIME_PUBLIC_EXPOSURE,
    )
    return TransitChartRuntimePayload(
        family_code=SELECTED_TEMPORAL_FAMILY_CODE,
        transiting_chart_objects=transiting_objects,
        transit_to_natal_relationships=relationships,
        astronomical_proof_refs=proof_refs,
        doctrine_limits=doctrine_limits,
        trace=trace,
        public_exposure=TRANSIT_CHART_RUNTIME_PUBLIC_EXPOSURE,
    )


def transit_chart_runtime_to_dict(payload: TransitChartRuntimePayload) -> dict[str, object]:
    """Serialise le payload runtime en dictionnaire stable pour les preuves."""
    return asdict(payload)


def _validate_temporal_runtime_owner() -> None:
    """Verifie que transit_chart_v1 reste rattache au runtime temporel."""
    family = get_astrology_graph_family(SELECTED_TEMPORAL_FAMILY_CODE)
    if family.target_owner is not AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME:
        raise ValueError("transit_chart_v1 must stay owned by temporal runtime")


def _block_fixed_star_output(
    chart_objects: tuple[ChartObjectRuntimeData, ...],
) -> tuple[ChartObjectRuntimeData, ...]:
    """Retire la capacite fixed-star du runtime transit non public."""
    return tuple(
        replace(
            chart_object,
            capabilities=replace(
                chart_object.capabilities,
                supports_fixed_star_conjunction=False,
            ),
            payloads=replace(
                chart_object.payloads,
                fixed_star=None,
                fixed_star_conjunctions=(),
            ),
        )
        for chart_object in chart_objects
    )


def _build_relationships(
    transit_aspects: Sequence[TransitAspectRuntimeSource],
) -> tuple[TransitToNatalRelationshipRuntimeData, ...]:
    """Projette et trie les aspects transit vers natal de facon deterministe."""
    relationships = tuple(_relationship_from_source(source) for source in transit_aspects)
    return tuple(
        sorted(
            relationships,
            key=lambda item: (
                item.transit_object_code,
                item.natal_object_code,
                item.aspect.aspect.code,
                item.aspect.orb.exact,
            ),
        )
    )


def _relationship_from_source(
    source: TransitAspectRuntimeSource,
) -> TransitToNatalRelationshipRuntimeData:
    """Convertit une source aspect en relation structurelle interne."""
    transit_code = source.transit_object_code.strip().lower()
    natal_code = source.natal_object_code.strip().lower()
    if not transit_code or not natal_code:
        raise ValueError("transit relationship requires transit and natal object codes")
    structural = build_aspect_structural_runtime_data(_TransitAspectAdapter(source))
    return TransitToNatalRelationshipRuntimeData(
        relationship_code=f"{transit_code}:{structural.aspect.code}:{natal_code}",
        transit_object_code=transit_code,
        natal_object_code=natal_code,
        aspect=structural,
        source="app.domain.astrology.builders.aspect_runtime_builder",
    )


def _validate_relationship_objects(
    *,
    relationships: tuple[TransitToNatalRelationshipRuntimeData, ...],
    transiting_objects: tuple[ChartObjectRuntimeData, ...],
    natal_chart_objects: Sequence[ChartObjectRuntimeData],
) -> None:
    """Refuse une relation qui ne correspond pas aux objets runtime fournis."""
    transiting_codes = {obj.code for obj in transiting_objects}
    natal_codes = {obj.code for obj in natal_chart_objects}
    for relationship in relationships:
        if relationship.transit_object_code not in transiting_codes:
            raise ValueError(
                f"Unknown transiting object '{relationship.transit_object_code}' in relationship."
            )
        if relationship.natal_object_code not in natal_codes:
            raise ValueError(
                f"Unknown natal object '{relationship.natal_object_code}' in relationship."
            )


def _astronomical_proof_refs() -> tuple[str, ...]:
    """Reference les preuves existantes sans dupliquer les tables SwissEph."""
    golden_case_ids = tuple(case.golden_case_id for case in SENSITIVE_GOLDEN_CASES[:3])
    return (
        CS253_GATE_MARKER,
        f"mode:{PRODUCTION_ASTRONOMY_MODE}",
        f"tolerance:{PRODUCTION_TOLERANCE.name}",
        *tuple(f"golden:{case_id}" for case_id in golden_case_ids),
    )


def _doctrine_limits() -> tuple[str, ...]:
    """Documente les limites doctrinales sans interpretation de transit."""
    aspect_rules = get_astrology_doctrine_governance("aspect_rules")
    interpretation_rules = get_astrology_doctrine_governance("interpretation_rules")
    return (
        (
            "aspect_rules:"
            f"{aspect_rules.school_policy.value}:{aspect_rules.doctrine_decision_status.value}"
        ),
        (
            "interpretation_rules:"
            f"{interpretation_rules.school_policy.value}:"
            f"{interpretation_rules.doctrine_decision_status.value}"
        ),
        "public_copy:no-transit-text",
        "fixed_stars:not-exposed",
        "public_projection:blocked",
    )


@dataclass(frozen=True, slots=True)
class _TransitAspectAdapter:
    """Adapte une relation transit vers natal au builder canonique d'aspects."""

    source: TransitAspectRuntimeSource

    @property
    def aspect_code(self) -> str:
        """Expose le code aspect canonique attendu par le builder."""
        return self.source.aspect_code

    @property
    def planet_a(self) -> str:
        """Expose le participant transitant pour le builder aspect."""
        return self.source.transit_object_code

    @property
    def planet_b(self) -> str:
        """Expose le participant natal pour le builder aspect."""
        return self.source.natal_object_code

    @property
    def angle(self) -> float:
        """Expose l'angle exact de l'aspect deja calcule."""
        return self.source.angle

    @property
    def orb(self) -> float:
        """Expose l'orbe brute deja calculee."""
        return self.source.orb

    @property
    def orb_used(self) -> float:
        """Expose l'orbe utilisee par le calculateur amont."""
        return self.source.orb_used

    @property
    def orb_max(self) -> float:
        """Expose l'orbe maximale retenue par le calculateur amont."""
        return self.source.orb_max

    @property
    def family(self) -> str:
        """Expose la famille d'aspect structurelle."""
        return self.source.family

    @property
    def is_major(self) -> bool:
        """Indique si l'aspect est majeur selon la source calculee."""
        return self.source.is_major

    @property
    def is_minor(self) -> bool:
        """Indique si l'aspect est mineur selon la source calculee."""
        return self.source.is_minor
