# Builder canonique de la projection client interpretee client_interpretation_projection_v1.
"""Construit une projection B2C par plan depuis structured_facts_v1."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.domain.astrology.interpretation.beginner_summary_v1_builder import (
    BEGINNER_SUMMARY_V1_DISCLAIMER_CODES,
    BEGINNER_SUMMARY_V1_NO_TIME_DISCLAIMER_CODES,
)
from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    STRUCTURED_FACTS_V1_PROJECTION_ID,
    birth_time_missing_from_structured_facts,
)

CLIENT_INTERPRETATION_PROJECTION_V1_ID = "client_interpretation_projection_v1"
CLIENT_INTERPRETATION_PROJECTION_V1_SOURCE_ID = STRUCTURED_FACTS_V1_PROJECTION_ID
CLIENT_INTERPRETATION_PROJECTION_V1_DISCLAIMER_CODES = BEGINNER_SUMMARY_V1_DISCLAIMER_CODES
CLIENT_INTERPRETATION_PROJECTION_V1_NO_TIME_DISCLAIMER_CODES = (
    BEGINNER_SUMMARY_V1_NO_TIME_DISCLAIMER_CODES
)

_PLAN_RANK = {"free": 0, "basic": 1, "premium": 2}
_PLAN_SECTIONS = {
    "free": (
        "orientation_generale",
        "points_forts",
        "limite_de_lecture",
        "upgrade_hint",
    ),
    "basic": (
        "orientation_generale",
        "points_forts",
        "limite_de_lecture",
        "upgrade_hint",
        "themes_personnels",
        "relations_aux_autres",
        "rythme_actuel",
        "conseil_pratique",
    ),
    "premium": (
        "orientation_generale",
        "points_forts",
        "limite_de_lecture",
        "upgrade_hint",
        "themes_personnels",
        "relations_aux_autres",
        "rythme_actuel",
        "conseil_pratique",
        "analyse_approfondie",
        "tensions_et_ressources",
        "fenetres_de_prediction",
        "plan_d_action",
        "nuances_et_arbitrages",
    ),
}
_SECTION_DEPTH = {"free": "free_short", "basic": "basic_contextual", "premium": "premium_deep"}
_PLAN_SHAPING = {
    "free": {
        "llm_input_selection": {
            "contract": "LLMInputSelection",
            "allowed_fact_groups": [
                "dominant_themes",
                "core_strengths",
                "reading_limits",
                "upgrade_context",
            ],
            "evidence_labels": [
                "position principale",
                "theme dominant",
            ],
        },
        "editorial_depth_profile": {
            "contract": "EditorialDepthProfile",
            "depth_code": "free_short",
            "section_budget": "short",
            "prediction_detail_level": "orientation_only",
        },
        "precision_level": "orientation",
        "frontend_visibility_rules": {
            "contract": "FrontendVisibilityRules",
            "visible_section_codes": list(_PLAN_SECTIONS["free"]),
            "summarized_section_codes": [],
            "masked_section_codes": [
                "themes_personnels",
                "relations_aux_autres",
                "rythme_actuel",
                "conseil_pratique",
                "analyse_approfondie",
                "tensions_et_ressources",
                "fenetres_de_prediction",
                "plan_d_action",
                "nuances_et_arbitrages",
            ],
            "display_hints": ["short", "upgrade"],
        },
    },
    "basic": {
        "llm_input_selection": {
            "contract": "LLMInputSelection",
            "allowed_fact_groups": [
                "dominant_themes",
                "core_strengths",
                "reading_limits",
                "upgrade_context",
                "personal_themes",
                "relationship_patterns",
                "current_rhythm",
                "practical_guidance",
            ],
            "evidence_labels": [
                "position principale",
                "theme dominant",
                "relation entre deux themes",
                "contexte de maison",
            ],
        },
        "editorial_depth_profile": {
            "contract": "EditorialDepthProfile",
            "depth_code": "basic_contextual",
            "section_budget": "contextual",
            "prediction_detail_level": "simple_trends",
        },
        "precision_level": "contextual",
        "frontend_visibility_rules": {
            "contract": "FrontendVisibilityRules",
            "visible_section_codes": list(_PLAN_SECTIONS["basic"]),
            "summarized_section_codes": [
                "analyse_approfondie",
                "tensions_et_ressources",
                "fenetres_de_prediction",
                "plan_d_action",
                "nuances_et_arbitrages",
            ],
            "masked_section_codes": [],
            "display_hints": ["short", "detailed", "upgrade"],
        },
    },
    "premium": {
        "llm_input_selection": {
            "contract": "LLMInputSelection",
            "allowed_fact_groups": [
                "dominant_themes",
                "core_strengths",
                "reading_limits",
                "upgrade_context",
                "personal_themes",
                "relationship_patterns",
                "current_rhythm",
                "practical_guidance",
                "tensions_resources",
                "prediction_windows",
                "nuance_arbitration",
                "action_priorities",
            ],
            "evidence_labels": [
                "position principale",
                "theme dominant",
                "relation entre deux themes",
                "contexte de maison",
                "signal recurrent",
            ],
        },
        "editorial_depth_profile": {
            "contract": "EditorialDepthProfile",
            "depth_code": "premium_deep",
            "section_budget": "extended",
            "prediction_detail_level": "controlled_windows",
        },
        "precision_level": "detailed",
        "frontend_visibility_rules": {
            "contract": "FrontendVisibilityRules",
            "visible_section_codes": list(_PLAN_SECTIONS["premium"]),
            "summarized_section_codes": [],
            "masked_section_codes": [],
            "display_hints": ["short", "detailed", "degraded"],
        },
    },
}
_EXCLUDED_SURFACES = (
    "audit_internals",
    "debug_traces",
    "expert_technical_projection_v1",
    "full_structured_facts",
    "provider_responses",
    "raw_runtime_objects",
    "technical_scores",
    "prompt_payloads",
)


class ClientInterpretationProjectionV1State(StrEnum):
    """Etats publics controles de la projection interpretee."""

    NORMAL = "normal"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    PLAN_INSUFFICIENT = "plan_insufficient"


@dataclass(frozen=True, slots=True)
class ClientInterpretationProjectionV1Builder:
    """Projette les faits structures vers une interpretation client par plan."""

    def build(
        self,
        structured_facts_v1: Mapping[str, Any] | None,
        *,
        requested_plan: str,
        current_plan: str,
    ) -> dict[str, Any]:
        """Construit la projection demandee ou un refus plan_insufficient."""
        plan = _normalize_plan(requested_plan)
        current = _normalize_plan(current_plan)

        if _PLAN_RANK[current] < _PLAN_RANK[plan]:
            return _plan_insufficient_payload(plan=plan, current_plan=current)

        if structured_facts_v1 is None:
            return _base_payload(
                plan=plan,
                state=ClientInterpretationProjectionV1State.UNAVAILABLE,
                disclaimer_codes=CLIENT_INTERPRETATION_PROJECTION_V1_DISCLAIMER_CODES,
                missing_data=("source_unavailable",),
            )

        _ensure_structured_facts_source(structured_facts_v1)
        facts = _facts(structured_facts_v1)
        positions = _sequence(facts.get("positions"))
        houses = _sequence(facts.get("houses"))
        aspects = _sequence(facts.get("major_aspects"))
        dominants = _sequence(structured_facts_v1.get("dominants"))
        source_signals = _signals(structured_facts_v1)
        no_time = birth_time_missing_from_structured_facts(structured_facts_v1, houses)

        state = (
            ClientInterpretationProjectionV1State.DEGRADED
            if no_time
            else ClientInterpretationProjectionV1State.NORMAL
        )
        disclaimer_codes = (
            CLIENT_INTERPRETATION_PROJECTION_V1_NO_TIME_DISCLAIMER_CODES
            if no_time
            else CLIENT_INTERPRETATION_PROJECTION_V1_DISCLAIMER_CODES
        )
        payload = _base_payload(
            plan=plan,
            state=state,
            disclaimer_codes=disclaimer_codes,
            missing_data=("no_time",) if no_time else (),
        )
        payload["sections"] = _sections(
            plan=plan,
            positions=positions,
            houses=houses,
            aspects=aspects,
            dominants=dominants,
            no_time=no_time,
        )
        payload["support_elements"] = _support_elements(
            plan=plan,
            positions=positions,
            aspects=aspects,
            dominants=dominants,
            no_time=no_time,
        )
        payload["interpretive_signals"] = _authorized_signals(plan, source_signals)
        if plan in {"basic", "premium"}:
            payload["audit_input"] = _audit_input(
                plan=plan,
                sections=payload["sections"],
                support_elements=payload["support_elements"],
                interpretive_signals=payload["interpretive_signals"],
            )
        return payload

    def canonical_json(self, payload: Mapping[str, Any]) -> str:
        """Retourne une representation stable de la projection."""
        return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _normalize_plan(plan: str) -> str:
    """Valide et normalise un plan B2C supporte."""
    normalized = plan.strip().lower()
    if normalized not in _PLAN_RANK:
        raise ValueError("unsupported client_interpretation_projection_v1 plan")
    return normalized


def _ensure_structured_facts_source(structured_facts_v1: Mapping[str, Any]) -> None:
    """Refuse toute entree qui ne vient pas de structured_facts_v1."""
    if structured_facts_v1.get("projection_id") != CLIENT_INTERPRETATION_PROJECTION_V1_SOURCE_ID:
        raise ValueError("client_interpretation_projection_v1 requires structured_facts_v1 source")


def _base_payload(
    *,
    plan: str,
    state: ClientInterpretationProjectionV1State,
    disclaimer_codes: Sequence[str],
    missing_data: Sequence[str] = (),
) -> dict[str, Any]:
    """Cree le squelette commun sans contenu technique interne."""
    payload: dict[str, Any] = {
        "projection_id": CLIENT_INTERPRETATION_PROJECTION_V1_ID,
        "source_projection_id": CLIENT_INTERPRETATION_PROJECTION_V1_SOURCE_ID,
        "source_projection": CLIENT_INTERPRETATION_PROJECTION_V1_SOURCE_ID,
        "plan": plan,
        "plan_variant": plan,
        "state": state.value,
        "llm_input_selection": dict(_PLAN_SHAPING[plan]["llm_input_selection"]),
        "editorial_depth_profile": dict(_PLAN_SHAPING[plan]["editorial_depth_profile"]),
        "precision_level": _PLAN_SHAPING[plan]["precision_level"],
        "frontend_visibility_rules": dict(_PLAN_SHAPING[plan]["frontend_visibility_rules"]),
        "sections": [],
        "support_elements": [],
        "calculation_scope": "full_projection_available_before_shaping",
        "disclaimer_codes": sorted(set(disclaimer_codes)),
        "excluded_surfaces": sorted(_EXCLUDED_SURFACES),
    }
    if missing_data:
        payload["missing_data"] = sorted(set(missing_data))
    return payload


def _plan_insufficient_payload(*, plan: str, current_plan: str) -> dict[str, Any]:
    """Retourne le refus controle sans fuite de payload interne."""
    payload = _base_payload(
        plan=plan,
        state=ClientInterpretationProjectionV1State.PLAN_INSUFFICIENT,
        disclaimer_codes=CLIENT_INTERPRETATION_PROJECTION_V1_DISCLAIMER_CODES,
    )
    payload["error"] = {
        "code": "plan_insufficient",
        "message": "Votre plan actuel ne permet pas cette profondeur d'interpretation.",
        "current_plan": current_plan,
        "required_plan": plan,
        "projection_id": CLIENT_INTERPRETATION_PROJECTION_V1_ID,
        "upgrade_hint": f"Passez au plan {plan} pour debloquer cette lecture.",
    }
    return payload


def _facts(structured_facts_v1: Mapping[str, Any]) -> Mapping[str, Any]:
    """Lit le bloc factuel autorise depuis la projection amont."""
    structural_facts = structured_facts_v1.get("structural_facts")
    if not isinstance(structural_facts, Mapping):
        return {}
    return structural_facts


def _sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    """Normalise une collection de mappings publics."""
    if not isinstance(value, Sequence) or isinstance(value, str):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _signals(structured_facts_v1: Mapping[str, Any]) -> Mapping[str, Any]:
    """Lit les signaux pre-narratifs deja autorises par structured_facts_v1."""
    signals = structured_facts_v1.get("interpretive_signals")
    if not isinstance(signals, Mapping):
        return {}
    return signals


def _sections(
    *,
    plan: str,
    positions: Sequence[Mapping[str, Any]],
    houses: Sequence[Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    dominants: Sequence[Mapping[str, Any]],
    no_time: bool,
) -> list[dict[str, Any]]:
    """Assemble les sections autorisees avec une profondeur par plan."""
    return [
        {
            "code": code,
            "depth": _SECTION_DEPTH[plan],
            "source_labels": _source_labels(
                code=code,
                positions=positions,
                houses=houses,
                aspects=aspects,
                dominants=dominants,
                no_time=no_time,
            ),
            "display_hint": _display_hint(code=code, no_time=no_time),
        }
        for code in _PLAN_SECTIONS[plan]
    ]


def _source_labels(
    *,
    code: str,
    positions: Sequence[Mapping[str, Any]],
    houses: Sequence[Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    dominants: Sequence[Mapping[str, Any]],
    no_time: bool,
) -> list[str]:
    """Produit des labels lisibles sans copier les faits techniques."""
    labels: list[str] = []
    if positions:
        labels.extend(_position_labels(positions))
    if dominants and code not in {"upgrade_hint", "limite_de_lecture"}:
        labels.extend(_dominant_labels(dominants))
    if aspects and code in {
        "relations_aux_autres",
        "rythme_actuel",
        "tensions_et_ressources",
        "nuances_et_arbitrages",
    }:
        labels.append("relation entre deux themes")
    if houses and not no_time and code in {"themes_personnels", "analyse_approfondie"}:
        labels.append("contexte de maison")
    return sorted(set(labels))[:4]


def _position_labels(positions: Sequence[Mapping[str, Any]]) -> list[str]:
    """Retourne des labels de positions principales."""
    allowed = {"sun": "position principale", "moon": "ressenti personnel", "asc": "ascendant"}
    labels: list[str] = []
    for position in positions:
        code = str(position.get("code", "")).lower()
        if code in allowed:
            labels.append(allowed[code])
    return labels


def _dominant_labels(dominants: Sequence[Mapping[str, Any]]) -> list[str]:
    """Retourne des labels de themes dominants."""
    labels: list[str] = []
    for dominant in dominants[:3]:
        code = dominant.get("code")
        if isinstance(code, str) and code:
            labels.append(f"theme dominant {code.lower()}")
    return labels


def _display_hint(*, code: str, no_time: bool) -> str:
    """Classe l'affichage client attendu pour une section."""
    if code == "upgrade_hint":
        return "upgrade"
    if no_time and code in {"themes_personnels", "analyse_approfondie"}:
        return "degraded"
    if code in {"orientation_generale", "points_forts", "limite_de_lecture"}:
        return "short"
    return "detailed"


def _support_elements(
    *,
    plan: str,
    positions: Sequence[Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    dominants: Sequence[Mapping[str, Any]],
    no_time: bool,
) -> list[dict[str, str]]:
    """Construit les appuis vulgarises autorises par le plan."""
    elements = [
        {
            "code": "confidence_wording",
            "value": "lecture limitee par les donnees disponibles" if no_time else "lecture forte",
        }
    ]
    for label in _position_labels(positions)[:2]:
        elements.append({"code": "source_label", "value": label})
    for label in _dominant_labels(dominants)[: 1 if plan == "free" else 3]:
        elements.append({"code": "highlight", "value": label})
    if plan == "premium" and aspects:
        elements.append({"code": "personalization_note", "value": "liens entre themes disponibles"})
    return elements


def _authorized_signals(plan: str, signals: Mapping[str, Any]) -> list[str]:
    """Expose seulement des identifiants de signaux pre-narratifs."""
    signal_ids: list[str] = []
    for key in sorted(signals):
        values = signals.get(key)
        if not isinstance(values, Sequence) or isinstance(values, str):
            continue
        for value in values:
            signal_ids.append(f"{key}:{value}")
    limit = {"free": 2, "basic": 6, "premium": 12}[plan]
    return sorted(set(signal_ids))[:limit]


def _audit_input(
    *,
    plan: str,
    sections: Sequence[Mapping[str, Any]],
    support_elements: Sequence[Mapping[str, str]],
    interpretive_signals: Sequence[str],
) -> dict[str, Any]:
    """Prepare une entree d'audit sans exposer les details internes d'audit."""
    return {
        "audit_contract": "narrative_answer_audit_v1",
        "plan": plan,
        "section_codes": [str(section["code"]) for section in sections],
        "support_element_codes": [item["code"] for item in support_elements],
        "interpretive_signal_ids": list(interpretive_signals),
        "excluded_audit_surfaces": [
            "audit_rows",
            "provider_payloads",
            "prompt_payloads",
            "review_internals",
        ],
    }
