# Builder du contrat interne theme_astral_llm_input_v1.
"""Assemble l'input theme astral avec materiau interpretatif source."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_INPUT_CONTRACT_ID,
    THEME_ASTRAL_PROMPT_CONTRACT_ID,
    THEME_ASTRAL_RESPONSE_CONTRACT_ID,
)

from .chart_interpretation_input_contracts import ChartInterpretationInputRuntimeData
from .interpretation_material_builder import InterpretationMaterialBuilder
from .interpretation_material_contracts import DeliveryProfile, InterpretationMaterialSource


class ThemeAstralLLMInputV1Builder:
    """Construit le carrier interne `theme_astral_llm_input_v1` sans appel provider."""

    def __init__(self, material_builder: InterpretationMaterialBuilder | None = None) -> None:
        """Injecte le builder de materiau pour faciliter les tests."""
        self.material_builder = material_builder or InterpretationMaterialBuilder()

    def build(
        self,
        *,
        chart_input: ChartInterpretationInputRuntimeData,
        interpretation_sources: Iterable[InterpretationMaterialSource],
        delivery_profile: DeliveryProfile,
        astrologer_voice: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Assemble le contrat interne attendu par le template theme astral."""
        material = self.material_builder.build(
            chart_input,
            sources=interpretation_sources,
            delivery_profile=delivery_profile,
        )
        return {
            "runtime_contract": {
                "contract_id": THEME_ASTRAL_INPUT_CONTRACT_ID,
                "contract_version": "v1",
                "prompt_contract_id": THEME_ASTRAL_PROMPT_CONTRACT_ID,
            },
            "safety_contract": {
                "source_policy": "interpretation_material_requires_source_ref_and_fact_ref",
                "provider_calls": "out_of_scope",
            },
            "astrologer_voice": dict(astrologer_voice or {}),
            "feature_context": {
                "feature": "theme_astral",
                "subfeature": "prompt_contract",
                "locale": chart_input.locale,
                "chart_type": chart_input.chart_type,
            },
            "delivery_profile": {
                "depth": delivery_profile,
                "selection_owner": "InterpretationMaterialBuilder",
            },
            "input_data": {
                "chart_id": chart_input.chart_id,
                "interpretation_material": material.to_payload(),
            },
            "output_contract": {
                "response_contract_id": THEME_ASTRAL_RESPONSE_CONTRACT_ID,
            },
        }
