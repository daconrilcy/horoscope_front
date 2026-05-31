# Commentaire global: helpers de tests pour assembler des plans natals Basic inspectables.
"""Fabriques partagees par les tests du BasicNatalReadingPlan."""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.basic_natal_reading_plan import (
    BasicNatalReadingPlan,
    BasicNatalReadingPlanBuilder,
)
from app.domain.astrology.interpretation.natal_fact_graph import (
    NatalFact,
    NatalFactFamily,
    NatalFactGraph,
)
from app.domain.astrology.interpretation.natal_salience_model import NatalSalienceModel
from app.domain.astrology.interpretation.natal_synthesis_resolver import SynthesisResolver
from app.domain.astrology.interpretation.natal_theme_taxonomy import BasicThemeCode, ThemeModel


def build_plan(
    facts: Sequence[NatalFact],
    themes: Sequence[ThemeModel],
    eligibility_context: EligibilityContext | None = None,
    *,
    max_sections: int = 8,
) -> BasicNatalReadingPlan:
    """Construit un plan depuis des fixtures deja explicites."""
    context = eligibility_context or full_birth_time_context()
    return BasicNatalReadingPlanBuilder(max_sections=max_sections).build(
        eligibility_context=context,
        fact_graph=NatalFactGraph(graph_id="graph:reading-plan-test", facts=tuple(facts)),
        salience_model=NatalSalienceModel(),
        themes=tuple(themes),
        synthesis_resolver=SynthesisResolver(),
    )


def fact(
    fact_id: str,
    family: NatalFactFamily,
    objects: tuple[str, ...],
    *,
    requires_birth_time: bool = False,
    editorial_candidate: bool = True,
) -> NatalFact:
    """Cree un fait minimal compatible avec les owners Basic existants."""
    return NatalFact(
        fact_id=fact_id,
        family=family,
        objects=objects,
        confidence="runtime_confirmed",
        requires_birth_time=requires_birth_time,
        source_paths=("runtime.fact",),
        editorial_candidate=editorial_candidate,
    )


def theme(
    theme_code: BasicThemeCode,
    fact_ids: tuple[str, ...],
    *,
    activation_score: float = 120.0,
    do_not_mention: tuple[str, ...] = (),
    objects: tuple[str, ...] = (),
) -> ThemeModel:
    """Cree un ThemeModel sans rappeler la taxonomie d'activation."""
    return ThemeModel(
        taxonomy_version="basic-natal-theme-taxonomy-v1",
        theme_code=theme_code,
        activation_score=activation_score,
        priority_level=10,
        resources=fact_ids,
        constraints=(),
        tensions=(),
        must_mention=fact_ids,
        may_mention=(),
        do_not_mention=do_not_mention,
        availability=("full_birth_time", "approximate_birth_time", "date_only"),
        compatible_sections=("fixture",),
        advised_vocabulary=("nuance",),
        forbidden_formulations=("fatalisme",),
        activation_metadata={"matched_objects": tuple(objects)},
    )


def full_birth_time_context() -> EligibilityContext:
    """Autorise les surfaces dependantes de l'heure pour les plans complets."""
    return EligibilityContext(
        birth_time_status="full_birth_time",
        can_use_houses=True,
        can_use_angles=True,
        can_use_house_rulers=True,
        can_use_lunar_nodes_by_house=True,
    )


def date_only_context() -> EligibilityContext:
    """Bloque les maisons, angles et maitrises pour les plans date-only."""
    return EligibilityContext(
        birth_time_status="date_only",
        can_use_houses=False,
        can_use_angles=False,
        can_use_house_rulers=False,
        can_use_lunar_nodes_by_house=False,
        limitations=("Lecture sans heure de naissance: surfaces horaires exclues.",),
    )
