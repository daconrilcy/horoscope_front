# Commentaire global: ces tests verrouillent la degradation date-only du graphe factuel natal Basic.
"""Tests date-only du graphe de faits natals Basic."""

from __future__ import annotations

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    AspectInterpretationRuntimeData,
    ChartInterpretationInputRuntimeData,
    ChartInterpretationMetadataRuntimeData,
    ChartObjectInterpretationRuntimeData,
    HousePositionInterpretationRuntimeData,
    RulershipInterpretationRuntimeData,
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


def test_date_only_gates_time_dependent_facts() -> None:
    """Les maisons, angles et maitrises horaires sont absents sans heure."""
    graph = build_basic_natal_fact_graph(_date_only_input(), _date_only_context())
    families = {fact.family for fact in graph.facts}

    assert NatalFactFamily.ANGLE not in families
    assert NatalFactFamily.HOUSE_EMPHASIS not in families
    assert NatalFactFamily.RULERSHIP not in families
    assert not any(fact.requires_birth_time for fact in graph.facts)


def test_date_only_keeps_non_time_dependent_families() -> None:
    """Les positions, luminaires, signes et aspects majeurs restent disponibles."""
    graph = build_basic_natal_fact_graph(_date_only_input(), _date_only_context())
    families = {fact.family for fact in graph.facts}

    assert {
        NatalFactFamily.LUMINARY,
        NatalFactFamily.PLANET_POSITION,
        NatalFactFamily.SIGN_EMPHASIS,
        NatalFactFamily.ASPECT,
        NatalFactFamily.NODE,
    } <= families


def _date_only_input() -> ChartInterpretationInputRuntimeData:
    """Construit une projection avec surfaces horaires presentes mais interdites."""
    return ChartInterpretationInputRuntimeData(
        chart_id="date-only-411",
        chart_type="natal",
        locale="fr",
        objects=(
            _object("sun", ChartObjectType.LUMINARY, "leo", ("luminary",)),
            _object("venus", ChartObjectType.PLANET, "gemini", ("planet",)),
            _object("asc", ChartObjectType.ANGLE, "libra", ("angle",)),
            _object("north_node", ChartObjectType.ASTRAL_POINT, "taurus", ("astral_point",)),
        ),
        aspects=(
            AspectInterpretationRuntimeData(
                code="conjunction",
                participant_codes=("sun", "venus"),
                family="major",
                angle=0.0,
                orb=0.5,
                orb_max=8.0,
                strength_level="strong",
                is_major=True,
                source="aspect_runtime",
            ),
        ),
        dignities=(),
        house_positions=(
            HousePositionInterpretationRuntimeData(
                code="venus",
                house_number=7,
                house_modality="angular",
                source="house_position_runtime",
            ),
        ),
        rulerships=(
            RulershipInterpretationRuntimeData(
                code="venus",
                rules_houses=(7,),
                is_house_ruler=True,
                is_ascendant_ruler=False,
                is_midheaven_ruler=False,
                source="house_rulers.sign_rulerships",
                dispositor_code=None,
            ),
        ),
        dominance=(),
        fixed_star_contacts=(),
        metadata=ChartInterpretationMetadataRuntimeData(
            source_codes=("chart_objects", "aspect_runtime"),
            object_count=4,
            aspect_count=1,
        ),
    )


def _object(
    code: str,
    object_type: ChartObjectType,
    sign_code: str,
    classifications: tuple[str, ...],
) -> ChartObjectInterpretationRuntimeData:
    """Construit un objet interpretable minimal."""
    return ChartObjectInterpretationRuntimeData(
        code=code,
        display_name=code.title(),
        object_type=object_type,
        classifications=classifications,
        source_type=ChartObjectSourceType.EPHEMERIS,
        source_key=code,
        longitude=3.0,
        latitude=None,
        zodiac_position=ZodiacInterpretationRuntimeData(sign_code=sign_code, degree_in_sign=3.0),
        house_number=1,
        house_modality="angular",
        dignity=None,
        motion=None,
        visibility=None,
        dominance=None,
        rulership=None,
        source_codes=(f"chart_objects.{code}",),
    )


def _date_only_context() -> EligibilityContext:
    """Interdit les surfaces qui dependent de l'heure de naissance."""
    return EligibilityContext(
        birth_time_status="date_only",
        can_use_houses=False,
        can_use_angles=False,
        can_use_house_rulers=False,
        can_use_lunar_nodes_by_house=False,
    )
