"""Résolution runtime des aspects utilisés par le domaine prediction."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from app.domain.prediction.context import LoadedPredictionContext
from app.domain.prediction.exceptions import PredictionContextError

DEFAULT_ASPECT_SYSTEM = "modern"


def major_aspect_angles(prediction_context: object) -> tuple[tuple[float, str], ...]:
    """Retourne les aspects majeurs depuis le contexte de référence chargé."""
    profiles = getattr(prediction_context, "aspect_profiles", None)
    if not isinstance(profiles, Mapping) or not profiles:
        raise PredictionContextError("Prediction context does not expose aspect profiles")

    aspects = tuple(_iter_major_aspects(profiles.values()))
    if not aspects:
        raise PredictionContextError("Prediction context does not expose major aspect angles")
    return aspects


def aspect_orbs_by_code(
    loaded_context: LoadedPredictionContext,
    *,
    calculation_context: str,
    aspect_codes: tuple[str, ...],
) -> dict[str, float]:
    """Résout les orbes d'aspects depuis les règles runtime chargées."""
    prediction_context = loaded_context.prediction_context
    rules = getattr(prediction_context, "aspect_orb_rules", ())
    if not isinstance(rules, tuple):
        rules = tuple(rules or ())
    system_rank = _active_aspect_system_rank(loaded_context)
    resolved: dict[str, float] = {}
    for aspect_code in aspect_codes:
        candidates = [
            rule
            for rule in rules
            if str(getattr(rule, "aspect_code", "")).lower() == aspect_code
            and bool(getattr(rule, "is_enabled", True))
            and str(getattr(rule, "calculation_context", "")).lower()
            in {calculation_context, "any"}
            and str(getattr(rule, "source_body_type", "any")).lower() == "any"
            and str(getattr(rule, "target_body_type", "any")).lower() == "any"
            and not getattr(rule, "source_planet_code", None)
            and not getattr(rule, "target_planet_code", None)
            and str(getattr(rule, "system_code", "")).lower() in system_rank
        ]
        if not candidates:
            raise PredictionContextError(
                "Missing aspect orb rule for "
                f"aspect={aspect_code!r} context={calculation_context!r}"
            )
        selected = sorted(
            candidates,
            key=lambda rule: (
                system_rank[str(getattr(rule, "system_code", "")).lower()],
                -int(getattr(rule, "priority", 0)),
            ),
        )[0]
        resolved[aspect_code] = float(getattr(selected, "orb_deg"))
    return resolved


def _iter_major_aspects(profiles: Iterable[object]) -> Iterable[tuple[float, str]]:
    """Filtre les profils d'aspects issus du référentiel canonique."""
    rows: list[tuple[float, str]] = []
    for profile in profiles:
        code = str(getattr(profile, "code", "") or "").strip().lower()
        raw_angle = getattr(profile, "angle", None)
        family_code = str(getattr(profile, "family_code", "") or "").strip().lower()
        if not code or not isinstance(raw_angle, (int, float)):
            continue
        if family_code != "major":
            continue
        rows.append((float(raw_angle), code))
    yield from sorted(rows, key=lambda item: (item[0], item[1]))


def _active_aspect_system_rank(loaded_context: LoadedPredictionContext) -> dict[str, int]:
    """Classe le système d'aspects daily actif et ses parents."""
    parameters = getattr(loaded_context.ruleset_context, "parameters", {})
    configured = DEFAULT_ASPECT_SYSTEM
    if isinstance(parameters, Mapping):
        configured = str(
            parameters.get("aspect_system")
            or parameters.get("aspect_school")
            or DEFAULT_ASPECT_SYSTEM
        )
    prediction_context = loaded_context.prediction_context
    inheritance = getattr(prediction_context, "aspect_system_inheritance", None)
    chain: list[str] = []
    seen: set[str] = set()
    current: str | None = configured
    while current:
        normalized = current.strip().lower()
        if not normalized or normalized in seen:
            break
        chain.append(normalized)
        seen.add(normalized)
        if not isinstance(inheritance, Mapping):
            break
        parent = inheritance.get(normalized)
        current = None if parent is None else str(parent)
    return {system_code: index for index, system_code in enumerate(chain or [configured])}
