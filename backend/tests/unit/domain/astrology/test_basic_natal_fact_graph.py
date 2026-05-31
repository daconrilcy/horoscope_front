# Commentaire global: ces tests verrouillent le graphe factuel natal Basic riche.
"""Tests unitaires du graphe de faits natals Basic."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    AdvancedConditionInterpretationRuntimeData,
    AspectInterpretationRuntimeData,
    BirthContextInterpretationRuntimeData,
    ChartInterpretationInputRuntimeData,
    ChartInterpretationMetadataRuntimeData,
    ChartObjectInterpretationRuntimeData,
    DignityInterpretationRuntimeData,
    DominanceInterpretationRuntimeData,
    HousePositionInterpretationRuntimeData,
    RulershipInterpretationRuntimeData,
    SignProfileBalancesInterpretationRuntimeData,
    ZodiacInterpretationRuntimeData,
)
from app.domain.astrology.interpretation.natal_fact_graph import NatalFactFamily
from app.domain.astrology.interpretation.natal_fact_graph_builder import (
    build_basic_natal_fact_graph,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectSourceType,
    ChartObjectType,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
FACT_GRAPH_MODULES = (
    REPO_ROOT / "app/domain/astrology/interpretation/natal_fact_graph.py",
    REPO_ROOT / "app/domain/astrology/interpretation/natal_fact_graph_builder.py",
)


def test_fact_graph_emits_required_families_and_traceable_contract() -> None:
    """Le graphe riche expose toutes les familles minimales avec source."""
    graph = build_basic_natal_fact_graph(_rich_input(), _full_birth_time_context())
    families = {fact.family for fact in graph.facts}

    assert families == set(NatalFactFamily)
    assert graph.graph_id.startswith("graph:")
    assert all(fact.source_paths for fact in graph.facts)
    assert all(fact.confidence == "runtime_confirmed" for fact in graph.facts)
    assert all(set(fact.to_internal_payload()) == _required_fact_fields() for fact in graph.facts)


def test_fact_ids_are_deterministic_and_major_aspects_keep_pair_identity() -> None:
    """Les identifiants ne dependent pas de l'ordre entrant des aspects."""
    graph = build_basic_natal_fact_graph(_rich_input(), _full_birth_time_context())
    reordered = _rich_input(aspects_reversed=True)
    same_graph = build_basic_natal_fact_graph(reordered, _full_birth_time_context())

    assert [fact.fact_id for fact in graph.facts] == [fact.fact_id for fact in same_graph.facts]
    aspect_facts = [fact for fact in graph.facts if fact.family is NatalFactFamily.ASPECT]
    assert len(aspect_facts) == 1
    assert aspect_facts[0].objects == ("moon", "sun", "trine")


def test_internal_sources_do_not_leak_to_editorial_candidates() -> None:
    """Les candidats aval restent separes des chemins de source internes."""
    graph = build_basic_natal_fact_graph(_rich_input(), _full_birth_time_context())
    internal_payload = graph.to_internal_payload()
    candidate_payload = graph.to_editorial_candidate_payload()

    assert any("source_paths" in item for item in internal_payload["facts"])
    assert candidate_payload["facts"]
    assert all("source_paths" not in item for item in candidate_payload["facts"])
    assert len(candidate_payload["facts"]) < len(internal_payload["facts"])


def test_fact_graph_builder_uses_runtime_inputs_without_local_recalculation() -> None:
    """AST guard: le builder ne rappelle pas de moteur de calcul astrologique."""
    forbidden_calls = {
        "".join(
            (
                "calculate_",
                "aspect",
            )
        ),
        "".join(
            (
                "calculate_",
                "dignity",
            )
        ),
        "calculate_house",
        "calculate_rulership",
        "HouseRulerResolver",
        "Swiss" + "Eph",
        "s" + "we",
    }
    forbidden_import_prefixes = ("app.api", "app.infra", "app.services", "fastapi", "sqlalchemy")
    for module_path in FACT_GRAPH_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = _call_name(node.func)
                assert call_name not in forbidden_calls
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                assert not any(
                    node.module == prefix or node.module.startswith(f"{prefix}.")
                    for prefix in forbidden_import_prefixes
                )


def _rich_input(*, aspects_reversed: bool = False) -> ChartInterpretationInputRuntimeData:
    """Construit une projection interpretative complete et courte."""
    aspects = (
        AspectInterpretationRuntimeData(
            code="trine",
            participant_codes=("sun", "moon"),
            family="harmonic",
            angle=120.0,
            orb=1.2,
            orb_max=8.0,
            strength_level="strong",
            is_major=True,
            source="aspect_runtime",
        ),
        AspectInterpretationRuntimeData(
            code="quincunx",
            participant_codes=("mars", "venus"),
            family="minor",
            angle=150.0,
            orb=2.0,
            orb_max=3.0,
            strength_level="medium",
            is_major=False,
            source="aspect_runtime",
        ),
    )
    return ChartInterpretationInputRuntimeData(
        chart_id="chart-411",
        chart_type="natal",
        locale="fr",
        objects=_objects(),
        aspects=tuple(reversed(aspects)) if aspects_reversed else aspects,
        dignities=(
            DignityInterpretationRuntimeData(
                code="mars",
                essential_score=2.0,
                accidental_score=1.0,
                total_score=3.0,
                source="dignity_runtime",
                functional_strength_score=None,
                expression_quality_score=None,
                intensity_score=None,
                condition_codes=("domicile",),
            ),
        ),
        house_positions=(
            HousePositionInterpretationRuntimeData(
                code="mars",
                house_number=1,
                house_modality="angular",
                source="house_position_runtime",
            ),
        ),
        rulerships=(
            RulershipInterpretationRuntimeData(
                code="mars",
                rules_houses=(1, 8),
                is_house_ruler=True,
                is_ascendant_ruler=True,
                is_midheaven_ruler=False,
                source="house_rulers.sign_rulerships",
                dispositor_code="venus",
                rules_signs=("aries", "scorpio"),
                rulership_sources=("runtime_reference.sign_rulerships",),
            ),
        ),
        dominance=(),
        fixed_star_contacts=(),
        sign_profile_balances=SignProfileBalancesInterpretationRuntimeData(
            elements=(_dominance("fire", "chart_balance.elements"),),
            modalities=(_dominance("cardinal", "chart_balance.modalities"),),
            polarities=(),
            seasonal_quadrants=(),
            fertility=(),
            voices=(),
            forms=(),
        ),
        advanced_condition_facts=(
            AdvancedConditionInterpretationRuntimeData(
                condition_code="swift_motion",
                condition_type_code="motion",
                source_planet_code="mars",
                target_planet_code=None,
                score_profile="basic",
                reference_version="runtime_reference.v1",
                score_impact=0.2,
                ranking_weight=1.0,
            ),
        ),
        birth_context=BirthContextInterpretationRuntimeData(),
        metadata=ChartInterpretationMetadataRuntimeData(
            source_codes=("chart_objects", "aspect_runtime"),
            object_count=4,
            aspect_count=2,
        ),
    )


def _objects() -> tuple[ChartObjectInterpretationRuntimeData, ...]:
    """Retourne les objets minimaux pour toutes les familles."""
    return (
        _object("sun", ChartObjectType.LUMINARY, "leo", ("luminary",)),
        _object("moon", ChartObjectType.LUMINARY, "aries", ("luminary",)),
        _object("mars", ChartObjectType.PLANET, "aries", ("planet",)),
        _object("asc", ChartObjectType.ANGLE, "libra", ("angle",)),
        _object("north_node", ChartObjectType.ASTRAL_POINT, "taurus", ("astral_point",)),
    )


def _object(
    code: str,
    object_type: ChartObjectType,
    sign_code: str,
    classifications: tuple[str, ...],
) -> ChartObjectInterpretationRuntimeData:
    """Construit un objet interpretatif source par le runtime."""
    return ChartObjectInterpretationRuntimeData(
        code=code,
        display_name=code.title(),
        object_type=object_type,
        classifications=classifications,
        source_type=ChartObjectSourceType.EPHEMERIS,
        source_key=code,
        longitude=12.0,
        latitude=None,
        zodiac_position=ZodiacInterpretationRuntimeData(sign_code=sign_code, degree_in_sign=12.0),
        house_number=1,
        house_modality="angular",
        dignity=None,
        motion=None,
        visibility=None,
        dominance=None,
        rulership=None,
        source_codes=(f"chart_objects.{code}",),
    )


def _dominance(code: str, source: str) -> DominanceInterpretationRuntimeData:
    """Construit une balance runtime minimale."""
    return DominanceInterpretationRuntimeData(code=code, score=0.7, source=source, rank=1)


def _full_birth_time_context() -> EligibilityContext:
    """Autorise les surfaces dependantes de l'heure pour le cas riche."""
    return EligibilityContext(
        birth_time_status="full_birth_time",
        can_use_houses=True,
        can_use_angles=True,
        can_use_house_rulers=True,
        can_use_lunar_nodes_by_house=True,
    )


def _required_fact_fields() -> set[str]:
    """Retourne les champs obligatoires du contrat factuel."""
    return {
        "fact_id",
        "family",
        "objects",
        "confidence",
        "requires_birth_time",
        "source_paths",
        "editorial_candidate",
    }


def _call_name(node: ast.AST) -> str:
    """Retourne le nom simple appele par un noeud AST."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""
