# Builder canonique de la projection client beginner_summary_v1.
"""Construit un resume debutant deterministe depuis structured_facts_v1."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    STRUCTURED_FACTS_V1_PROJECTION_ID,
    birth_time_missing_from_structured_facts,
)

BEGINNER_SUMMARY_V1_PROJECTION_ID = "beginner_summary_v1"
BEGINNER_SUMMARY_V1_SOURCE_PROJECTION_ID = STRUCTURED_FACTS_V1_PROJECTION_ID
BEGINNER_SUMMARY_V1_AUDIENCE = ("basic", "beginner", "free", "public-user")
BEGINNER_SUMMARY_V1_ALLOWED_FIELDS = (
    "ascendant",
    "dominant_house",
    "dominant_themes",
    "main_signs",
)
BEGINNER_SUMMARY_V1_DISCLAIMER_CODES = ("ASTROLOGY_GENERAL_LIMITATION",)
BEGINNER_SUMMARY_V1_NO_TIME_DISCLAIMER_CODES = (
    "ASTROLOGY_GENERAL_LIMITATION",
    "ASTROLOGY_MISSING_BIRTH_TIME",
)


class BeginnerSummaryV1State(StrEnum):
    """Etats publics controles de la projection debutante."""

    NORMAL = "normal"
    EMPTY = "empty"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class BeginnerSummaryV1MessageCode(StrEnum):
    """Codes stables que le client peut traduire sans texte LLM."""

    NORMAL = "BGS_NORMAL"
    EMPTY = "BGS_EMPTY"
    DEGRADED_NO_TIME = "BGS_DEGRADED_NO_TIME"
    UNAVAILABLE = "BGS_UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class BeginnerSummaryV1Builder:
    """Projette les faits structures vers un payload B2C court et stable."""

    def build(self, structured_facts_v1: Mapping[str, Any] | None) -> dict[str, Any]:
        """Construit le resume debutant depuis la projection factuelle amont."""
        if structured_facts_v1 is None:
            return _base_payload(
                state=BeginnerSummaryV1State.UNAVAILABLE,
                message_code=BeginnerSummaryV1MessageCode.UNAVAILABLE,
                disclaimer_codes=BEGINNER_SUMMARY_V1_DISCLAIMER_CODES,
                missing_data=("source_unavailable",),
            )

        _ensure_structured_facts_source(structured_facts_v1)
        positions = _positions(structured_facts_v1)
        houses = _houses(structured_facts_v1)
        dominants = _dominants(structured_facts_v1)
        no_time = birth_time_missing_from_structured_facts(structured_facts_v1, houses)

        main_signs = _main_signs(positions)
        dominant_themes = _dominant_themes(dominants, no_time=no_time)
        summary_items = _summary_items(main_signs, dominant_themes)

        if not summary_items:
            return _base_payload(
                state=BeginnerSummaryV1State.EMPTY,
                message_code=BeginnerSummaryV1MessageCode.EMPTY,
                disclaimer_codes=BEGINNER_SUMMARY_V1_DISCLAIMER_CODES,
            )

        if no_time:
            payload = _base_payload(
                state=BeginnerSummaryV1State.DEGRADED,
                message_code=BeginnerSummaryV1MessageCode.DEGRADED_NO_TIME,
                disclaimer_codes=BEGINNER_SUMMARY_V1_NO_TIME_DISCLAIMER_CODES,
                missing_data=("no_time",),
            )
            payload["degraded_reason"] = "no_time"
        else:
            payload = _base_payload(
                state=BeginnerSummaryV1State.NORMAL,
                message_code=BeginnerSummaryV1MessageCode.NORMAL,
                disclaimer_codes=BEGINNER_SUMMARY_V1_DISCLAIMER_CODES,
            )
            ascendant = _ascendant(positions)
            if ascendant is not None:
                payload["ascendant"] = ascendant
            dominant_house = _dominant_house(houses)
            if dominant_house is not None:
                payload["dominant_house"] = dominant_house

        payload["main_signs"] = main_signs
        payload["dominant_themes"] = dominant_themes
        payload["summary_items"] = summary_items
        return payload

    def canonical_json(self, payload: Mapping[str, Any]) -> str:
        """Retourne la representation JSON stable du resume."""
        return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _ensure_structured_facts_source(structured_facts_v1: Mapping[str, Any]) -> None:
    """Refuse toute entree qui ne vient pas de structured_facts_v1."""
    if structured_facts_v1.get("projection_id") != BEGINNER_SUMMARY_V1_SOURCE_PROJECTION_ID:
        raise ValueError("beginner_summary_v1 requires structured_facts_v1 source")


def _base_payload(
    *,
    state: BeginnerSummaryV1State,
    message_code: BeginnerSummaryV1MessageCode,
    disclaimer_codes: Sequence[str],
    missing_data: Sequence[str] = (),
) -> dict[str, Any]:
    """Cree le squelette public commun sans surface technique."""
    payload: dict[str, Any] = {
        "projection_id": BEGINNER_SUMMARY_V1_PROJECTION_ID,
        "audience": list(BEGINNER_SUMMARY_V1_AUDIENCE),
        "source_projection": BEGINNER_SUMMARY_V1_SOURCE_PROJECTION_ID,
        "source_projection_id": BEGINNER_SUMMARY_V1_SOURCE_PROJECTION_ID,
        "allowed_fields": list(BEGINNER_SUMMARY_V1_ALLOWED_FIELDS),
        "state": state.value,
        "summary_items": [],
        "main_signs": [],
        "dominant_themes": [],
        "message_code": message_code.value,
        "display_messages": [_display_message(message_code)],
        "disclaimer_codes": sorted(disclaimer_codes),
        "excluded_surfaces": [
            "audit_details",
            "debug_traces",
            "evidence_refs",
            "full_structured_facts",
            "internal_payloads",
            "technical_scores",
        ],
    }
    if missing_data:
        payload["missing_data"] = sorted(set(missing_data))
    return payload


def _display_message(message_code: BeginnerSummaryV1MessageCode) -> dict[str, str]:
    """Associe chaque code public a une copie applicative stable."""
    messages = {
        BeginnerSummaryV1MessageCode.NORMAL: "Votre resume debutant est disponible.",
        BeginnerSummaryV1MessageCode.EMPTY: (
            "Aucun resume debutant n'est disponible pour ces donnees."
        ),
        BeginnerSummaryV1MessageCode.DEGRADED_NO_TIME: (
            "Votre resume est affiche sans ascendant ni maisons detaillees car l'heure de "
            "naissance manque."
        ),
        BeginnerSummaryV1MessageCode.UNAVAILABLE: (
            "Le resume debutant est temporairement indisponible."
        ),
    }
    return {"code": message_code.value, "message": messages[message_code]}


def _positions(structured_facts_v1: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    """Lit les positions publiques candidates depuis les faits structures."""
    structural_facts = structured_facts_v1.get("structural_facts")
    if not isinstance(structural_facts, Mapping):
        return ()
    positions = structural_facts.get("positions")
    if not isinstance(positions, Sequence) or isinstance(positions, str):
        return ()
    return tuple(item for item in positions if isinstance(item, Mapping))


def _houses(structured_facts_v1: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    """Lit les maisons uniquement quand la source amont les fournit."""
    structural_facts = structured_facts_v1.get("structural_facts")
    if not isinstance(structural_facts, Mapping):
        return ()
    houses = structural_facts.get("houses")
    if not isinstance(houses, Sequence) or isinstance(houses, str):
        return ()
    return tuple(item for item in houses if isinstance(item, Mapping))


def _dominants(structured_facts_v1: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    """Lit les dominantes deja calculees par structured_facts_v1."""
    dominants = structured_facts_v1.get("dominants")
    if not isinstance(dominants, Sequence) or isinstance(dominants, str):
        return ()
    return tuple(item for item in dominants if isinstance(item, Mapping))


def _main_signs(positions: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Selectionne les signes principaux lisibles par un debutant."""
    allowed_codes = {"sun": "sun_sign", "moon": "moon_sign"}
    signs: list[dict[str, str]] = []
    for position in sorted(positions, key=lambda item: str(item.get("code", ""))):
        code = str(position.get("code", "")).lower()
        sign = position.get("zodiac_sign")
        if code in allowed_codes and isinstance(sign, str) and sign:
            signs.append({"code": allowed_codes[code], "value": sign})
    return signs


def _ascendant(positions: Sequence[Mapping[str, Any]]) -> dict[str, str] | None:
    """Retourne l'ascendant seulement lorsque la source l'autorise."""
    for position in positions:
        code = str(position.get("code", "")).lower()
        sign = position.get("zodiac_sign")
        if code in {"asc", "ascendant"} and isinstance(sign, str) and sign:
            return {"code": "ascendant", "value": sign}
    return None


def _dominant_house(houses: Sequence[Mapping[str, Any]]) -> dict[str, int] | None:
    """Selectionne une maison stable sans recalculer le runtime."""
    candidates = [
        item.get("house_number")
        for item in sorted(houses, key=lambda item: str(item.get("code", "")))
        if isinstance(item.get("house_number"), int)
    ]
    if not candidates:
        return None
    return {"code": "dominant_house", "value": candidates[0]}


def _dominant_themes(
    dominants: Sequence[Mapping[str, Any]],
    *,
    no_time: bool,
) -> list[dict[str, str]]:
    """Expose les dominantes non techniques et compatibles avec le mode degrade."""
    themes: list[dict[str, str]] = []
    for dominant in sorted(
        dominants,
        key=lambda item: (
            item.get("rank") if isinstance(item.get("rank"), int) else 9999,
            str(item.get("code", "")),
        ),
    ):
        code = dominant.get("code")
        if not isinstance(code, str) or not code:
            continue
        normalized = code.lower()
        if no_time and ("house" in normalized or "asc" in normalized):
            continue
        themes.append({"code": normalized, "label": normalized.replace("_", " ")})
    return themes


def _summary_items(
    main_signs: Sequence[Mapping[str, str]],
    dominant_themes: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Transforme les champs autorises en items courts et deterministes."""
    items = [
        {"code": item["code"], "value": item["value"]}
        for item in main_signs
        if item.get("code") and item.get("value")
    ]
    items.extend(
        {"code": f"dominant_theme:{item['code']}", "value": item["label"]}
        for item in dominant_themes
        if item.get("code") and item.get("label")
    )
    return items
