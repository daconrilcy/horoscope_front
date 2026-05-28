# Builder canonique du payload provider theme_astral.
"""Assemble le payload provider stable de theme astral sans appel LLM."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    ChartInterpretationInputRuntimeData,
)
from app.domain.astrology.interpretation.interpretation_material_builder import (
    InterpretationMaterialBuilder,
)
from app.domain.astrology.interpretation.interpretation_material_contracts import (
    INTERPRETATION_MATERIAL_KEYS,
    DeliveryProfile,
    InterpretationMaterialSource,
)
from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_INPUT_CONTRACT_ID,
    THEME_ASTRAL_PROMPT_CONTRACT_ID,
    THEME_ASTRAL_RESPONSE_CONTRACT_ID,
    ThemeAstralCommercialPlan,
    resolve_theme_astral_provider_delivery_profile,
)

CommercialPlan = ThemeAstralCommercialPlan

_TOP_LEVEL_KEYS = (
    "runtime_contract",
    "safety_contract",
    "astrologer_voice",
    "feature_context",
    "delivery_profile",
    "input_data",
    "output_contract",
)
_INPUT_DATA_KEYS = (
    "birth_context",
    "astrological_facts",
    "interpretation_material",
    "selected_themes",
    "limits",
)


class ThemeAstralProviderPayloadBuilder:
    """Construit l'unique payload provider stable pour theme_astral."""

    def __init__(self, material_builder: InterpretationMaterialBuilder | None = None) -> None:
        """Injecte le builder de materiau source pour garder une responsabilite unique."""
        self.material_builder = material_builder or InterpretationMaterialBuilder()

    def build(
        self,
        *,
        chart_input: ChartInterpretationInputRuntimeData,
        interpretation_sources: Iterable[InterpretationMaterialSource],
        commercial_plan: CommercialPlan,
        astrologer_voice: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Assemble le squelette provider sans exposer le libelle commercial."""
        delivery_profile = resolve_theme_astral_provider_delivery_profile(commercial_plan)
        material = self.material_builder.build(
            chart_input,
            sources=interpretation_sources,
            delivery_profile=cast(DeliveryProfile, commercial_plan),
        )
        material_payload = material.to_payload()
        payload = {
            "runtime_contract": _runtime_contract(),
            "safety_contract": _safety_contract(),
            "astrologer_voice": dict(astrologer_voice or {}),
            "feature_context": _feature_context(chart_input),
            "delivery_profile": delivery_profile,
            "input_data": {
                "birth_context": _birth_context(chart_input),
                "astrological_facts": _astrological_facts(chart_input, delivery_profile),
                "interpretation_material": material_payload,
                "selected_themes": _selected_themes(material_payload, delivery_profile),
                "limits": _limits(chart_input, material_payload),
            },
            "output_contract": _output_contract(delivery_profile),
        }
        _assert_payload_skeleton(payload)
        return payload


def _runtime_contract() -> dict[str, object]:
    """Declare les references de contrat sans trace backend ni plan."""
    return {
        "contract_id": THEME_ASTRAL_INPUT_CONTRACT_ID,
        "contract_version": "v1",
        "prompt_contract_id": THEME_ASTRAL_PROMPT_CONTRACT_ID,
        "builder_owner": "ThemeAstralProviderPayloadBuilder",
    }


def _safety_contract() -> dict[str, object]:
    """Fixe les regles de non-invention applicables au provider."""
    return {
        "source_policy": "interpretation_material_requires_source_ref_and_fact_ref",
        "truth_policy": "astrological_facts_are_engine_owned",
        "voice_policy": "style_only_no_fact_mutation",
        "commercial_label_policy": "backend_only",
    }


def _feature_context(chart_input: ChartInterpretationInputRuntimeData) -> dict[str, object]:
    """Expose le contexte fonctionnel stable sans segmentation commerciale."""
    return {
        "feature": "theme_astral",
        "subfeature": "prompt_contract",
        "locale": chart_input.locale,
        "chart_type": chart_input.chart_type,
    }


def _birth_context(chart_input: ChartInterpretationInputRuntimeData) -> dict[str, object]:
    """Normalise le contexte de naissance utile au LLM."""
    return {
        "chart_id": chart_input.chart_id,
        "locale": chart_input.locale,
        "chart_type": chart_input.chart_type,
    }


def _astrological_facts(
    chart_input: ChartInterpretationInputRuntimeData, delivery_profile: Mapping[str, object]
) -> dict[str, object]:
    """Projette uniquement les faits calcules par les builders astrologiques."""
    budget = cast(Mapping[str, int], delivery_profile["astrological_facts_budget"])
    return {
        "source_owner": "ChartInterpretationInputBuilder",
        "objects": [
            {
                "code": item.code,
                "display_name": item.display_name,
                "sign_code": item.zodiac_position.sign_code,
                "degree_in_sign": item.zodiac_position.degree_in_sign,
            }
            for item in chart_input.objects[: budget["max_objects"]]
        ],
        "houses": [
            {"code": item.code, "house_number": item.house_number}
            for item in chart_input.house_positions[: budget["max_objects"]]
        ],
        "aspects": [
            {"code": item.code, "participant_codes": list(item.participant_codes)}
            for item in chart_input.aspects[: budget["max_aspects"]]
        ],
        "dominance": [
            {"code": item.code, "score": item.score}
            for item in chart_input.dominance[: budget["max_dominants"]]
        ],
    }


def _selected_themes(
    material_payload: Mapping[str, list[dict[str, object]]], delivery_profile: Mapping[str, object]
) -> dict[str, object]:
    """Derive les themes retenus depuis le materiau source deja selectionne."""
    max_sections = cast(Mapping[str, int], delivery_profile["section_budget"])["max_sections"]
    sections = [key for key in INTERPRETATION_MATERIAL_KEYS if material_payload.get(key)]
    return {
        "selection_owner": "InterpretationMaterialBuilder",
        "section_keys": sections[:max_sections],
        "max_sections": max_sections,
    }


def _limits(
    chart_input: ChartInterpretationInputRuntimeData,
    material_payload: Mapping[str, list[dict[str, object]]],
) -> dict[str, object]:
    """Rend explicites les absences sans retirer de cles du contrat."""
    missing_sections = [
        key for key in INTERPRETATION_MATERIAL_KEYS if not material_payload.get(key)
    ]
    empty_facts = []
    if not chart_input.objects:
        empty_facts.append("objects")
    if not chart_input.aspects:
        empty_facts.append("aspects")
    if not chart_input.dominance:
        empty_facts.append("dominance")
    return {
        "missing_data": {"empty_fact_groups": empty_facts},
        "unavailable_sections": missing_sections,
        "uncertainty_policy": "state_limits_without_inventing_sources",
    }


def _output_contract(delivery_profile: Mapping[str, object]) -> dict[str, object]:
    """Reference le contrat de sortie versionne et ses obligations."""
    max_sections = cast(Mapping[str, int], delivery_profile["section_budget"])["max_sections"]
    return {
        "response_contract_id": THEME_ASTRAL_RESPONSE_CONTRACT_ID,
        "response_contract_version": "v1",
        "schema_ref": THEME_ASTRAL_RESPONSE_CONTRACT_ID,
        "required_sections": ["title", "summary", "sections", "evidence", "contract_trace"],
        "max_sections": max_sections,
    }


def _assert_payload_skeleton(payload: Mapping[str, object]) -> None:
    """Verifie localement le squelette avant handoff provider."""
    if tuple(payload) != _TOP_LEVEL_KEYS:
        raise ValueError("theme_astral provider payload top-level skeleton drift")
    input_data = payload.get("input_data")
    if not isinstance(input_data, dict) or tuple(input_data) != _INPUT_DATA_KEYS:
        raise ValueError("theme_astral provider payload input_data skeleton drift")


__all__ = [
    "CommercialPlan",
    "ThemeAstralProviderPayloadBuilder",
]
