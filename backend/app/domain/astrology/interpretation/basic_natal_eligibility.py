# Commentaire global: ce module centralise l'eligibilite horaire des lectures natales Basic.
"""Construit le contexte canonique d'eligibilite des surfaces dependantes de l'heure."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from app.domain.astrology.projections.projection_hash import projection_value_to_jsonable

BirthTimeStatus = Literal["full_birth_time", "approximate_birth_time", "date_only"]

_DATE_ONLY_LIMITATION = (
    "Lecture sans heure de naissance: les maisons, les angles et leurs maitrises "
    "ne sont pas utilises."
)
_APPROXIMATE_TIME_LIMITATION = (
    "Lecture avec une heure de naissance incertaine: les maisons et les angles "
    "sont lus avec prudence."
)
_MISSING_TIMEZONE_LIMITATION = (
    "Lecture avec fuseau horaire incomplet: les informations liees aux maisons "
    "et aux angles restent prudentes."
)
_MISSING_BIRTH_TIME_VALUES = {"missing", "unknown", "no_time", "date_only", None}
_APPROXIMATE_BIRTH_TIME_VALUES = {
    "approximate",
    "approximate_birth_time",
    "uncertain",
    "estimated",
}
_APPROXIMATE_REASON_VALUES = {
    "approximate_birth_time",
    "uncertain_birth_time",
    "estimated_birth_time",
    "missing_timezone",
    "unknown_timezone",
}


@dataclass(frozen=True, slots=True)
class EligibilityContext:
    """Decrit les familles interpretatives autorisees pour une lecture Basic."""

    birth_time_status: BirthTimeStatus
    can_use_houses: bool
    can_use_angles: bool
    can_use_house_rulers: bool
    can_use_lunar_nodes_by_house: bool
    limitations: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        """Retourne une forme JSON stable du contexte d'eligibilite."""
        return {
            "birth_time_status": self.birth_time_status,
            "can_use_houses": self.can_use_houses,
            "can_use_angles": self.can_use_angles,
            "can_use_house_rulers": self.can_use_house_rulers,
            "can_use_lunar_nodes_by_house": self.can_use_lunar_nodes_by_house,
            "limitations": list(self.limitations),
        }


def build_basic_natal_eligibility_context(
    structured_facts_v1: Mapping[str, Any],
) -> EligibilityContext:
    """Classe l'usage horaire Basic depuis la projection factuelle canonique."""
    missing_data = _mapping(structured_facts_v1.get("missing_data"))
    structural_facts = _mapping(structured_facts_v1.get("structural_facts"))
    houses = _sequence(structural_facts.get("houses"))
    signals = _mapping(structured_facts_v1.get("interpretive_signals"))
    reasons = {str(reason) for reason in _sequence(missing_data.get("reasons"))}
    birth_time_state = missing_data.get("birth_time")
    timezone_state = missing_data.get("birth_timezone")

    if birth_time_state in _MISSING_BIRTH_TIME_VALUES or "no_time" in reasons:
        return EligibilityContext(
            birth_time_status="date_only",
            can_use_houses=False,
            can_use_angles=False,
            can_use_house_rulers=False,
            can_use_lunar_nodes_by_house=False,
            limitations=(_DATE_ONLY_LIMITATION,),
        )

    has_houses = bool(houses)
    has_house_rulers = bool(_sequence(signals.get("dispositor_codes")))
    limitations: list[str] = []
    birth_time_status: BirthTimeStatus = "full_birth_time"
    if (
        birth_time_state in _APPROXIMATE_BIRTH_TIME_VALUES
        or timezone_state in {"missing", "unknown", None}
        or reasons.intersection(_APPROXIMATE_REASON_VALUES)
    ):
        birth_time_status = "approximate_birth_time"
        limitations.append(
            _MISSING_TIMEZONE_LIMITATION
            if timezone_state in {"missing", "unknown", None}
            else _APPROXIMATE_TIME_LIMITATION
        )

    return EligibilityContext(
        birth_time_status=birth_time_status,
        can_use_houses=has_houses,
        can_use_angles=has_houses,
        can_use_house_rulers=has_houses and has_house_rulers,
        can_use_lunar_nodes_by_house=has_houses,
        limitations=tuple(limitations),
    )


def apply_basic_natal_eligibility_to_llm_blocks(
    *,
    facts: Mapping[str, Any],
    signals: Mapping[str, Any],
    structured_facts_v1: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], EligibilityContext]:
    """Filtre les blocs LLM pour que Basic ne lise pas de surfaces interdites."""
    context = build_basic_natal_eligibility_context(structured_facts_v1)
    filtered_facts = dict(facts)
    filtered_signals = dict(signals)

    if not context.can_use_houses:
        filtered_facts["houses"] = []
        filtered_facts["positions"] = [
            _without_house_number(item) for item in _sequence(filtered_facts.get("positions"))
        ]
        _replace_signal_codes(filtered_signals, "house_position_codes", ())

    if not context.can_use_angles:
        filtered_facts["dominants"] = [
            _without_angular_factors(item) for item in _sequence(filtered_facts.get("dominants"))
        ]

    if not context.can_use_house_rulers:
        _replace_signal_codes(filtered_signals, "dispositor_codes", ())

    return filtered_facts, filtered_signals, context


def _without_house_number(item: object) -> object:
    """Retire le numero de maison sans modifier les autres faits zodiacaux."""
    if not isinstance(item, Mapping):
        return projection_value_to_jsonable(item)
    payload = dict(item)
    payload["house_number"] = None
    return payload


def _without_angular_factors(item: object) -> object:
    """Retire l'angularite d'une dominante sans supprimer le fait non horaire."""
    if not isinstance(item, Mapping):
        return projection_value_to_jsonable(item)
    payload = dict(item)
    factors = payload.get("factors")
    if isinstance(factors, Sequence) and not isinstance(factors, (str, bytes)):
        payload["factors"] = [factor for factor in factors if "angular" not in str(factor).lower()]
    return payload


def _replace_signal_codes(signals: dict[str, Any], key: str, values: Sequence[str]) -> None:
    """Remplace une famille de signaux tout en conservant la forme du bloc."""
    codes = signals.get("interpretive_signal_codes")
    if isinstance(codes, Mapping):
        next_codes = dict(codes)
        next_codes[key] = list(values)
        signals["interpretive_signal_codes"] = next_codes


def _mapping(value: object) -> Mapping[str, Any]:
    """Normalise une valeur optionnelle en mapping lisible."""
    return value if isinstance(value, Mapping) else {}


def _sequence(value: object) -> Sequence[Any]:
    """Normalise une valeur optionnelle en sequence non textuelle."""
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return ()
