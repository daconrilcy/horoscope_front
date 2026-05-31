# Builder canonique du payload provider theme_astral.
"""Assemble le payload provider stable de theme astral sans appel LLM."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

from app.domain.astrology.interpretation.basic_natal_reading_plan import (
    BasicNatalPublicEvidence,
    BasicNatalReadingPlan,
    build_basic_natal_editorial_briefs,
)
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
BASIC_NATAL_PROMPT_PAYLOAD_KEY = "basic_natal_prompt_payload"
_BASIC_INPUT_DATA_KEYS = (BASIC_NATAL_PROMPT_PAYLOAD_KEY,)
_BASIC_NATAL_PROMPT_PAYLOAD_KEYS = (
    "report_arc",
    "sections",
    "resolved_syntheses",
    "section_editorial_briefs",
    "plain_language_glossary",
    "forbidden_template_phrases",
    "source_usage_policy",
    "editorial_evidence",
    "limitations",
    "disclaimers",
    "style_constraints",
)
_BASIC_STYLE_CONSTRAINTS = {
    "word_count": {"minimum": 900, "maximum": 1300},
    "section_count": {"minimum": 6, "maximum": 8},
    "tone": "vous",
    "prediction_policy": "no_firm_prediction",
    "advice_policy": "no_prescriptive_advice",
}
_BASIC_FORBIDDEN_TEMPLATE_PHRASES = (
    "cette lecture s'appuie uniquement sur",
    "Ce repere retient",
    "avec une confiance editoriale controlee",
    "Luminaire: moon",
    "Position planetaire:",
)
_BASIC_SOURCE_USAGE_POLICY = (
    "Les sources publiques servent d'annexe courte. Le corps de chaque section "
    "doit expliquer le sens humain, la manifestation possible et la nuance, "
    "sans lister les sources comme contenu principal."
)
_NARRATIVE_SOURCE_FAMILY_SECTIONS: dict[str, tuple[str, ...]] = {
    "personnalite": ("planet_sign_interpretations", "dominant_themes"),
    "emotions": ("planet_sign_interpretations", "resources"),
    "relations": ("aspect_interpretations", "resources"),
    "vocation": ("planet_house_interpretations", "dominant_themes"),
    "evolution": ("tensions", "integration_levers", "warnings"),
}


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
        basic_reading_plan: BasicNatalReadingPlan | None = None,
    ) -> dict[str, Any]:
        """Assemble le squelette provider sans exposer le libelle commercial."""
        delivery_profile = resolve_theme_astral_provider_delivery_profile(commercial_plan)
        if commercial_plan == "basic":
            if basic_reading_plan is None:
                raise ValueError("Basic provider payload requires BasicNatalReadingPlan")
            payload = {
                "runtime_contract": _runtime_contract(),
                "safety_contract": _safety_contract(),
                "astrologer_voice": dict(astrologer_voice or {}),
                "feature_context": _feature_context(chart_input),
                "delivery_profile": delivery_profile,
                "input_data": {
                    "basic_natal_prompt_payload": _basic_natal_prompt_payload(basic_reading_plan),
                },
                "output_contract": _output_contract(delivery_profile),
            }
            _assert_payload_skeleton(payload, commercial_plan=commercial_plan)
            return payload

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
        _assert_payload_skeleton(payload, commercial_plan=commercial_plan)
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
    birth_context = chart_input.birth_context
    birth_place = birth_context.birth_place
    precision = birth_context.precision
    return {
        "chart_id": chart_input.chart_id,
        "birth_date": birth_context.birth_date,
        "birth_time_local": birth_context.birth_time_local,
        "birth_place": {
            "city": birth_place.city,
            "country": birth_place.country,
            "timezone": birth_place.timezone,
            "latitude": birth_place.latitude,
            "longitude": birth_place.longitude,
        },
        "precision": {
            "birth_time_known": precision.birth_time_known,
            "coordinates_known": precision.coordinates_known,
        },
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
    material_budget = cast(Mapping[str, int], delivery_profile["material_budget"])
    sections = [key for key in INTERPRETATION_MATERIAL_KEYS if material_payload.get(key)]
    return {
        "selection_owner": "InterpretationMaterialBuilder",
        "section_keys": sections[:max_sections],
        "max_sections": max_sections,
        "selected_source_count": _selected_source_count(material_payload),
        "max_source_items": material_budget["max_source_items"],
        "narrative_source_families": _narrative_source_family_metrics(material_payload),
    }


def _selected_source_count(material_payload: Mapping[str, list[dict[str, object]]]) -> int:
    """Compte les sources retenues sans inspecter de carrier technique legacy."""
    return sum(len(material_payload.get(key, [])) for key in INTERPRETATION_MATERIAL_KEYS)


def _narrative_source_family_metrics(
    material_payload: Mapping[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    """Expose des metriques privees pour les cinq familles narratives publiques."""
    metrics: list[dict[str, object]] = []
    for family, sections in _NARRATIVE_SOURCE_FAMILY_SECTIONS.items():
        section_counts = {
            section: len(material_payload.get(section, []))
            for section in sections
            if material_payload.get(section)
        }
        source_refs = sorted(
            {
                str(item["source_ref"])
                for section in sections
                for item in material_payload.get(section, [])
                if item.get("source_ref")
            }
        )
        metrics.append(
            {
                "family": family,
                "covered": bool(section_counts),
                "material_sections": list(section_counts),
                "source_count": sum(section_counts.values()),
                "public_source_count": len(source_refs),
            }
        )
    return metrics


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
    missing_birth_context = []
    birth_context = chart_input.birth_context
    if birth_context.birth_date is None:
        missing_birth_context.append("birth_date")
    if birth_context.birth_time_local is None:
        missing_birth_context.append("birth_time_local")
    if birth_context.birth_place.city is None:
        missing_birth_context.append("birth_place.city")
    if birth_context.birth_place.country is None:
        missing_birth_context.append("birth_place.country")
    if birth_context.birth_place.timezone is None:
        missing_birth_context.append("birth_place.timezone")
    return {
        "missing_data": {
            "empty_fact_groups": empty_facts,
            "birth_context": missing_birth_context,
        },
        "unavailable_sections": missing_sections,
        "uncertainty_policy": "state_limits_without_inventing_sources",
    }


def _basic_natal_prompt_payload(reading_plan: BasicNatalReadingPlan) -> dict[str, object]:
    """Projette le plan Basic en payload prompt sans carriers bruts ni identifiants."""
    evidence_by_section = _editorial_evidence_by_section(reading_plan.public_evidence)
    section_briefs = build_basic_natal_editorial_briefs(reading_plan)
    payload: dict[str, object] = {
        "report_arc": _basic_report_arc(reading_plan),
        "sections": [
            {
                "section_code": section.section_code,
                "heading_intent": section.heading_intent,
                "target_length_words": section.target_length_words,
                "theme_codes": list(section.theme_codes),
                "editorial_evidence_labels": evidence_by_section.get(section.section_code, []),
            }
            for section in reading_plan.sections
        ],
        "resolved_syntheses": [
            {
                "section_code": section.section_code,
                "heading_intent": section.heading_intent,
                "theme_codes": list(section.theme_codes),
            }
            for section in reading_plan.sections
        ],
        "section_editorial_briefs": [brief.to_payload() for brief in section_briefs],
        "plain_language_glossary": _plain_language_glossary(reading_plan),
        "forbidden_template_phrases": list(_BASIC_FORBIDDEN_TEMPLATE_PHRASES),
        "source_usage_policy": _BASIC_SOURCE_USAGE_POLICY,
        "editorial_evidence": [
            _provider_editorial_evidence(evidence) for evidence in reading_plan.public_evidence
        ],
        "limitations": list(reading_plan.limitations),
        "disclaimers": list(reading_plan.disclaimers),
        "style_constraints": {
            **_BASIC_STYLE_CONSTRAINTS,
            "plan_constraints": list(reading_plan.style_constraints),
        },
    }
    if tuple(payload) != _BASIC_NATAL_PROMPT_PAYLOAD_KEYS:
        raise ValueError("Basic natal prompt payload skeleton drift")
    return payload


def build_basic_natal_prompt_payload(reading_plan: BasicNatalReadingPlan) -> dict[str, object]:
    """Expose le payload prompt Basic canonique sans dupliquer le builder provider."""
    return _basic_natal_prompt_payload(reading_plan)


def _provider_editorial_evidence(evidence: BasicNatalPublicEvidence) -> dict[str, object]:
    """Expose une preuve editoriale lisible sans ID brut ni chemin interne."""
    return {
        "label": evidence.label,
        "explanation": evidence.explanation,
        "section_codes": list(evidence.source_section_codes),
    }


def _editorial_evidence_by_section(
    evidence_items: Iterable[BasicNatalPublicEvidence],
) -> dict[str, list[str]]:
    """Indexe les libelles de preuves publiques par section du plan."""
    by_section: dict[str, list[str]] = {}
    for evidence in evidence_items:
        for section_code in evidence.source_section_codes:
            by_section.setdefault(section_code, []).append(evidence.label)
    return by_section


def _basic_report_arc(reading_plan: BasicNatalReadingPlan) -> str:
    """Resume le fil narratif autorise depuis les sections du plan."""
    labels = [section.heading_intent for section in reading_plan.sections[:4]]
    if not labels:
        return "Relier les repères disponibles en une lecture courte, nuancée et non prescriptive."
    return (
        "Relier "
        + ", ".join(label.lower() for label in labels)
        + " en une lecture progressive: introduction, thèmes explicatifs, conclusion "
        "et annexes sources."
    )


def _plain_language_glossary(reading_plan: BasicNatalReadingPlan) -> list[dict[str, str]]:
    """Expose le vocabulaire public deja derive du plan, sans table astrologique locale."""
    terms = dict.fromkeys(
        (
            *(section.heading_intent for section in reading_plan.sections),
            *(evidence.label for evidence in reading_plan.public_evidence),
        )
    )
    return [
        {
            "term": term,
            "meaning": (
                "Vocabulaire public dérivé du plan Basic canonique pour guider la rédaction."
            ),
            "usage_limit": "Employer comme repère explicatif, jamais comme liste brute de sources.",
        }
        for term in terms
        if term
    ]


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


def _assert_payload_skeleton(
    payload: Mapping[str, object], *, commercial_plan: CommercialPlan
) -> None:
    """Verifie localement le squelette avant handoff provider."""
    if tuple(payload) != _TOP_LEVEL_KEYS:
        raise ValueError("theme_astral provider payload top-level skeleton drift")
    input_data = payload.get("input_data")
    expected_input_keys = _BASIC_INPUT_DATA_KEYS if commercial_plan == "basic" else _INPUT_DATA_KEYS
    if not isinstance(input_data, dict) or tuple(input_data) != expected_input_keys:
        raise ValueError("theme_astral provider payload input_data skeleton drift")


__all__ = [
    "BASIC_NATAL_PROMPT_PAYLOAD_KEY",
    "CommercialPlan",
    "ThemeAstralProviderPayloadBuilder",
    "build_basic_natal_prompt_payload",
]
