# Registre canonique des familles de graphes astrologiques runtime.
"""Expose les metadonnees internes des familles de graphes astrologiques."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum

from app.domain.astrology.runtime.calculation_graph_contracts import CalculationGraphDefinition
from app.domain.astrology.runtime.natal_calculation_graph import (
    NATAL_GRAPH_CODE,
    build_natal_calculation_graph_definition,
)


class AstrologyGraphFamilyRegistryError(ValueError):
    """Erreur explicite pour les declarations de familles invalides."""


class AstrologyGraphFamilyStatus(StrEnum):
    """Statuts de gouvernance autorises pour une famille de graphe."""

    ACTIVE = "active"
    BLOCKED_BY_ASTRONOMICAL_PROOF = "blocked-by-astronomical-proof"
    BLOCKED_BY_PRODUCT_DECISION = "blocked-by-product-decision"
    BLOCKED_BY_DOCTRINE_DECISION = "blocked-by-doctrine-decision"
    BLOCKED_BY_MULTI_CHART_DECISION = "blocked-by-multi-chart-decision"
    BLOCKED_BY_TRACE_DECISION = "blocked-by-trace-decision"
    BLOCKED_BY_CACHE_DECISION = "blocked-by-cache-decision"
    MISSING = "missing"


class AstrologyGraphFamilyOwner(StrEnum):
    """Owners runtime cibles des familles astrologiques."""

    NATAL_RUNTIME = "astrology-runtime-natal"
    TEMPORAL_RUNTIME = "astrology-runtime-temporal"
    RELATIONSHIP_RUNTIME = "astrology-runtime-relationship"
    FORECASTING_RUNTIME = "astrology-runtime-forecasting"
    AI_SCORING_RUNTIME = "astrology-runtime-ai-scoring"
    TEXT_GENERATION_RUNTIME = "astrology-runtime-text-generation"


@dataclass(frozen=True, slots=True)
class AstrologyGraphFamilyMetadata:
    """Contrat interne d'une famille de graphe astrologique."""

    code: str
    status: AstrologyGraphFamilyStatus
    target_owner: AstrologyGraphFamilyOwner
    required_inputs: tuple[str, ...]
    expected_graph_type: str
    required_objects: tuple[str, ...]
    authorized_public_surfaces: tuple[str, ...]
    internal_surfaces: tuple[str, ...]
    trace_replay_needs: tuple[str, ...]
    cache_invalidation_boundary: str
    blockers: tuple[str, ...]
    user_decisions: tuple[str, ...]


GraphDefinitionFactory = Callable[[], CalculationGraphDefinition]

MANDATORY_ASTROLOGY_GRAPH_FAMILY_CODES = (
    "natal_chart_v1",
    "transit_chart_v1",
    "synastry_chart_v1",
    "solar_return_v1",
    "lunar_return_v1",
    "progressed_chart_v1",
    "composite_chart_v1",
    "profection_v1",
    "forecasting_v1",
    "ai_scoring_v1",
    "narrative_generation_v1",
)

ASTRONOMICAL_PROOF_BLOCKER = "CS-250 astronomical proof required"
CACHE_POLICY_BLOCKER = "cache policy approval required"

_NATAL_PUBLIC_SURFACES = ("NatalResult public projection",)
_NATAL_INTERNAL_SURFACES = (
    "backend/app/domain/astrology/runtime/natal_calculation_graph.py",
    "backend/app/domain/astrology/runtime/calculation_graph_runner.py",
)
_NATAL_REQUIRED_INPUTS = (
    "birth_datetime",
    "timezone",
    "coordinates",
    "house_system",
    "zodiac_mode",
    "runtime_reference",
    "locale",
    "calculation_options",
)
_NATAL_REQUIRED_OBJECTS = (
    "planet_positions",
    "astral_points",
    "houses_runtime",
    "chart_objects",
    "aspects_runtime",
)
_NATAL_TRACE_NEEDS = (
    "input snapshot",
    "calculation graph version",
    "node output provenance",
)
_NATAL_CACHE_BOUNDARY = "birth data, coordinates, house system, zodiac mode, runtime reference"


def _blocked_family(
    *,
    code: str,
    owner: AstrologyGraphFamilyOwner,
    required_inputs: tuple[str, ...],
    required_objects: tuple[str, ...],
    status: AstrologyGraphFamilyStatus = AstrologyGraphFamilyStatus.BLOCKED_BY_ASTRONOMICAL_PROOF,
    blockers: tuple[str, ...] = (ASTRONOMICAL_PROOF_BLOCKER,),
    user_decisions: tuple[str, ...] = (),
) -> AstrologyGraphFamilyMetadata:
    """Declare une famille non executable sans inventer son implementation."""
    family_blockers = blockers
    if CACHE_POLICY_BLOCKER not in family_blockers:
        family_blockers = (*family_blockers, CACHE_POLICY_BLOCKER)
    return AstrologyGraphFamilyMetadata(
        code=code,
        status=status,
        target_owner=owner,
        required_inputs=required_inputs,
        expected_graph_type="CalculationGraphDefinition",
        required_objects=required_objects,
        authorized_public_surfaces=(),
        internal_surfaces=(
            "backend/app/domain/astrology/runtime/astrology_graph_family_registry.py",
        ),
        trace_replay_needs=("graph family decision trace", "input contract trace"),
        cache_invalidation_boundary="blocked until cache policy is approved",
        blockers=family_blockers,
        user_decisions=user_decisions,
    )


ASTROLOGY_GRAPH_FAMILY_DECLARATIONS: tuple[AstrologyGraphFamilyMetadata, ...] = (
    AstrologyGraphFamilyMetadata(
        code=NATAL_GRAPH_CODE,
        status=AstrologyGraphFamilyStatus.ACTIVE,
        target_owner=AstrologyGraphFamilyOwner.NATAL_RUNTIME,
        required_inputs=_NATAL_REQUIRED_INPUTS,
        expected_graph_type="CalculationGraphDefinition",
        required_objects=_NATAL_REQUIRED_OBJECTS,
        authorized_public_surfaces=_NATAL_PUBLIC_SURFACES,
        internal_surfaces=_NATAL_INTERNAL_SURFACES,
        trace_replay_needs=_NATAL_TRACE_NEEDS,
        cache_invalidation_boundary=_NATAL_CACHE_BOUNDARY,
        blockers=(),
        user_decisions=(),
    ),
    _blocked_family(
        code="transit_chart_v1",
        owner=AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME,
        required_inputs=("birth_chart", "transit_datetime", "timezone", "coordinates"),
        required_objects=("natal_chart_v1", "transiting_chart_objects", "transit_aspects"),
        user_decisions=("select first temporal technique in CS-253",),
    ),
    _blocked_family(
        code="synastry_chart_v1",
        owner=AstrologyGraphFamilyOwner.RELATIONSHIP_RUNTIME,
        required_inputs=("primary_birth_data", "secondary_birth_data"),
        required_objects=("primary_chart_objects", "secondary_chart_objects", "interchart_aspects"),
        status=AstrologyGraphFamilyStatus.BLOCKED_BY_MULTI_CHART_DECISION,
        blockers=("multi-chart ownership decision required",),
        user_decisions=("define relationship-chart product boundary",),
    ),
    _blocked_family(
        code="solar_return_v1",
        owner=AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME,
        required_inputs=("birth_chart", "return_year", "return_location"),
        required_objects=("solar_return_chart_objects", "return_aspects"),
        user_decisions=("select first temporal technique in CS-253",),
    ),
    _blocked_family(
        code="lunar_return_v1",
        owner=AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME,
        required_inputs=("birth_chart", "return_month", "return_location"),
        required_objects=("lunar_return_chart_objects", "return_aspects"),
        user_decisions=("select first temporal technique in CS-253",),
    ),
    _blocked_family(
        code="progressed_chart_v1",
        owner=AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME,
        required_inputs=("birth_chart", "progression_date", "progression_method"),
        required_objects=("progressed_chart_objects", "progressed_aspects"),
        user_decisions=("select first temporal technique in CS-253",),
    ),
    _blocked_family(
        code="composite_chart_v1",
        owner=AstrologyGraphFamilyOwner.RELATIONSHIP_RUNTIME,
        required_inputs=("primary_birth_data", "secondary_birth_data", "composition_method"),
        required_objects=("composite_chart_objects", "composite_aspects"),
        status=AstrologyGraphFamilyStatus.BLOCKED_BY_MULTI_CHART_DECISION,
        blockers=("multi-chart ownership decision required",),
        user_decisions=("define relationship-chart product boundary",),
    ),
    _blocked_family(
        code="profection_v1",
        owner=AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME,
        required_inputs=("birth_chart", "profection_age", "doctrine_school"),
        required_objects=("annual_profection_house", "lord_of_year"),
        blockers=(ASTRONOMICAL_PROOF_BLOCKER, "doctrine school governance required"),
        user_decisions=("choose profection doctrine school",),
    ),
    _blocked_family(
        code="forecasting_v1",
        owner=AstrologyGraphFamilyOwner.FORECASTING_RUNTIME,
        required_inputs=("birth_chart", "forecast_window", "enabled_techniques"),
        required_objects=("forecast_events", "technique_trace"),
        status=AstrologyGraphFamilyStatus.BLOCKED_BY_PRODUCT_DECISION,
        blockers=("forecasting product primitive decision required", ASTRONOMICAL_PROOF_BLOCKER),
        user_decisions=("define public forecasting product primitive",),
    ),
    _blocked_family(
        code="ai_scoring_v1",
        owner=AstrologyGraphFamilyOwner.AI_SCORING_RUNTIME,
        required_inputs=("chart_runtime_snapshot", "scoring_policy"),
        required_objects=("scoring_features", "score_trace"),
        status=AstrologyGraphFamilyStatus.BLOCKED_BY_TRACE_DECISION,
        blockers=("AI scoring trace contract required",),
        user_decisions=("define scoring policy and explainability boundary",),
    ),
    _blocked_family(
        code="narrative_generation_v1",
        owner=AstrologyGraphFamilyOwner.TEXT_GENERATION_RUNTIME,
        required_inputs=("chart_runtime_snapshot", "text_generation_policy", "locale"),
        required_objects=("text_generation_inputs", "text_generation_trace"),
        status=AstrologyGraphFamilyStatus.BLOCKED_BY_PRODUCT_DECISION,
        blockers=("text generation product boundary required",),
        user_decisions=("define public text generation contract",),
    ),
)

_GRAPH_DEFINITION_FACTORIES: dict[str, GraphDefinitionFactory] = {
    NATAL_GRAPH_CODE: build_natal_calculation_graph_definition,
}


def get_astrology_graph_family(code: str) -> AstrologyGraphFamilyMetadata:
    """Retourne une famille connue ou echoue sans fallback silencieux."""
    try:
        return ASTROLOGY_GRAPH_FAMILY_REGISTRY[code]
    except KeyError as exc:
        raise AstrologyGraphFamilyRegistryError(
            f"Unknown astrology graph family code '{code}'."
        ) from exc


def list_astrology_graph_families() -> tuple[AstrologyGraphFamilyMetadata, ...]:
    """Expose un snapshot stable des familles declarees."""
    return tuple(
        ASTROLOGY_GRAPH_FAMILY_REGISTRY[code] for code in MANDATORY_ASTROLOGY_GRAPH_FAMILY_CODES
    )


def list_astrology_graph_families_by_status(
    status: AstrologyGraphFamilyStatus,
) -> tuple[AstrologyGraphFamilyMetadata, ...]:
    """Filtre les familles par statut de gouvernance."""
    return tuple(family for family in list_astrology_graph_families() if family.status == status)


def resolve_astrology_graph_definition(code: str) -> CalculationGraphDefinition:
    """Retourne la definition runtime liee a une famille executable."""
    get_astrology_graph_family(code)
    try:
        return _GRAPH_DEFINITION_FACTORIES[code]()
    except KeyError as exc:
        raise AstrologyGraphFamilyRegistryError(
            f"Astrology graph family '{code}' has no executable graph definition."
        ) from exc


def build_astrology_graph_family_registry(
    declarations: Iterable[AstrologyGraphFamilyMetadata],
) -> dict[str, AstrologyGraphFamilyMetadata]:
    """Construit un registre valide pour les tests et futurs enrichissements."""
    return _build_registry(tuple(declarations))


def _build_registry(
    declarations: tuple[AstrologyGraphFamilyMetadata, ...],
) -> dict[str, AstrologyGraphFamilyMetadata]:
    """Valide les codes uniques et l'ensemble obligatoire du registre."""
    registry: dict[str, AstrologyGraphFamilyMetadata] = {}
    duplicates: set[str] = set()
    for family in declarations:
        if family.code in registry:
            duplicates.add(family.code)
            continue
        registry[family.code] = family
    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise AstrologyGraphFamilyRegistryError(
            f"Duplicate astrology graph family code(s): {duplicate_list}."
        )

    missing = set(MANDATORY_ASTROLOGY_GRAPH_FAMILY_CODES) - set(registry)
    unknown = set(registry) - set(MANDATORY_ASTROLOGY_GRAPH_FAMILY_CODES)
    if missing or unknown:
        raise AstrologyGraphFamilyRegistryError(
            "Astrology graph family declarations do not match mandatory codes."
        )
    return registry


ASTROLOGY_GRAPH_FAMILY_REGISTRY = _build_registry(ASTROLOGY_GRAPH_FAMILY_DECLARATIONS)
