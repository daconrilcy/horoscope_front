"""Test d'integration du materiau interpretatif dans l'input theme astral."""

from __future__ import annotations

from app.domain.astrology.dominance.contracts import DominantPlanetsResult
from app.domain.astrology.interpretation.chart_interpretation_input_builder import (
    ChartInterpretationInputBuilder,
)
from app.domain.astrology.interpretation.interpretation_material_contracts import (
    INTERPRETATION_MATERIAL_KEYS,
    InterpretationMaterialSource,
)
from app.domain.astrology.interpretation.theme_astral_llm_input_v1_builder import (
    ThemeAstralLLMInputV1Builder,
)
from app.domain.astrology.natal_calculation import AspectResult
from app.domain.llm.configuration.theme_astral_contracts import THEME_ASTRAL_INPUT_CONTRACT_ID
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object


class _NatalSource:
    """Source runtime minimale pour verifier le handoff LLM sans provider."""

    chart_objects = (interpretable_chart_object("mars"),)
    aspects = (
        AspectResult(
            aspect_code="trine",
            planet_a="sun",
            planet_b="moon",
            angle=120.0,
            orb=1.0,
            orb_used=1.0,
            orb_max=6.0,
            family="major",
            is_major=True,
            is_minor=False,
        ),
    )
    dominant_planets = DominantPlanetsResult(
        score_profile_code="fixture.profile",
        tradition_code="fixture",
        reference_version_code="v1",
        planets=(),
        top_planet_code=None,
        chart_ruler_code=None,
        most_elevated_planet_code=None,
    )
    advanced_condition_facts = ()
    chart_balance = None


def test_theme_astral_llm_input_receives_interpretation_material_without_provider_call() -> None:
    """Le carrier theme astral embarque le bloc source sous input_data."""
    chart_input = ChartInterpretationInputBuilder().build(_NatalSource(), chart_id="chart-1")
    payload = ThemeAstralLLMInputV1Builder().build(
        chart_input=chart_input,
        delivery_profile="premium",
        interpretation_sources=(
            InterpretationMaterialSource(
                section="planet_sign_interpretations",
                source_owner="astral_planet_interpretation_profiles",
                source_id="mars-aries",
                source_version="v1",
                theme="Mars en Belier",
                keywords=("elan",),
                interpretive_text="Texte source Mars Belier",
                risk="impulsivite",
                resource="initiative",
                base_weight=0.5,
                planet_code="mars",
                sign_code="aries",
            ),
            InterpretationMaterialSource(
                section="aspect_interpretations",
                source_owner="astral_aspect_interpretation_profiles",
                source_id="trine",
                source_version="v1",
                theme="Trigone",
                keywords=("fluidite",),
                writing_hint="Presenter le trigone comme une circulation.",
                risk="facilite passive",
                resource="cooperation",
                base_weight=0.5,
                aspect_code="trine",
            ),
        ),
    )

    material = payload["input_data"]["interpretation_material"]

    assert payload["runtime_contract"]["contract_id"] == THEME_ASTRAL_INPUT_CONTRACT_ID
    assert payload["delivery_profile"]["selection_owner"] == "InterpretationMaterialBuilder"
    assert tuple(material) == INTERPRETATION_MATERIAL_KEYS
    assert material["planet_sign_interpretations"][0]["source_ref"]
    assert material["planet_sign_interpretations"][0]["fact_ref"] == "object:mars:sign:aries"
    assert material["aspect_interpretations"][0]["writing_hint"]
