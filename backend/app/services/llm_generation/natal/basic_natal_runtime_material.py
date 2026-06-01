# Commentaire global: construction partagee de la matiere Basic pour les runtimes natals.
"""Fabrique le BasicNatalReadingPlan depuis les owners astrologiques canoniques."""

from __future__ import annotations

from app.domain.astrology.interpretation.basic_natal_eligibility import (
    build_basic_natal_eligibility_context,
)
from app.domain.astrology.interpretation.basic_natal_reading_plan import (
    BasicNatalReadingPlan,
    BasicNatalReadingPlanBuilder,
)
from app.domain.astrology.interpretation.chart_interpretation_input_builder import (
    ChartInterpretationInputBuilder,
)
from app.domain.astrology.interpretation.natal_fact_graph_builder import (
    build_basic_natal_fact_graph,
)
from app.domain.astrology.interpretation.natal_salience_model import NatalSalienceModel
from app.domain.astrology.interpretation.natal_synthesis_resolver import SynthesisResolver
from app.domain.astrology.interpretation.natal_theme_taxonomy import NatalNarrativeThemeTaxonomy
from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    StructuredFactsV1Builder,
)
from app.domain.astrology.natal_calculation import NatalResult


def build_basic_natal_reading_plan_for_runtime(
    *,
    natal_result: NatalResult,
    chart_id: str,
    locale: str,
) -> BasicNatalReadingPlan:
    """Reconstruit le plan Basic canonique utilise par les runtimes de lecture."""
    chart_input = ChartInterpretationInputBuilder().build(
        natal_result,
        chart_id=chart_id,
        locale=locale,
    )
    structured_facts = StructuredFactsV1Builder().build(
        natal_result,
        chart_id=chart_id,
        locale=locale,
    )
    eligibility_context = build_basic_natal_eligibility_context(structured_facts)
    fact_graph = build_basic_natal_fact_graph(chart_input, eligibility_context)
    salience_model = NatalSalienceModel()
    salience_audit = salience_model.score(fact_graph, eligibility_context)
    themes = NatalNarrativeThemeTaxonomy().activate(
        graph=fact_graph,
        salience_audit=salience_audit,
        eligibility_context=eligibility_context,
    )
    return BasicNatalReadingPlanBuilder().build(
        eligibility_context=eligibility_context,
        fact_graph=fact_graph,
        salience_model=salience_model,
        themes=themes,
        synthesis_resolver=SynthesisResolver(),
        locale=locale,
    )


__all__ = ["build_basic_natal_reading_plan_for_runtime"]
