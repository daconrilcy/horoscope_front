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


def aspect_orb_for_bodies(
    loaded_context: LoadedPredictionContext,
    *,
    calculation_context: str,
    aspect_code: str,
    source_code: str,
    target_code: str,
) -> float:
    """Résout l'orbe d'un aspect pour une paire de corps astrologiques."""
    prediction_context = loaded_context.prediction_context
    rules = getattr(prediction_context, "aspect_orb_rules", ())
    if not isinstance(rules, tuple):
        rules = tuple(rules or ())
    system_rank = _active_aspect_system_rank(loaded_context)
    candidates = [
        candidate
        for rule in rules
        for candidate in _iter_oriented_rule_candidates(
            rule,
            aspect_code=aspect_code,
            calculation_context=calculation_context,
            source_code=source_code,
            target_code=target_code,
            prediction_context=prediction_context,
            system_rank=system_rank,
        )
    ]
    if not candidates:
        default_orb = _aspect_default_orb(prediction_context, aspect_code)
        if default_orb is None:
            raise PredictionContextError(
                "Missing aspect orb rule or default definition for "
                f"aspect={aspect_code!r} context={calculation_context!r}"
            )
        return default_orb
    selected_rule, _specificity = sorted(
        candidates,
        key=lambda item: (
            system_rank[str(getattr(item[0], "system_code", "")).lower()],
            -int(getattr(item[0], "priority", 0)),
            -item[1],
        ),
    )[0]
    return float(getattr(selected_rule, "orb_deg"))


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


def _iter_oriented_rule_candidates(
    rule: object,
    *,
    aspect_code: str,
    calculation_context: str,
    source_code: str,
    target_code: str,
    prediction_context: object,
    system_rank: Mapping[str, int],
) -> Iterable[tuple[object, int]]:
    """Évalue une règle d'orbe dans les deux sens pour les aspects natals."""
    if str(getattr(rule, "aspect_code", "")).lower() != aspect_code.lower():
        return
    if not bool(getattr(rule, "is_enabled", True)):
        return
    if str(getattr(rule, "calculation_context", "")).lower() not in {
        calculation_context,
        "any",
    }:
        return
    if str(getattr(rule, "system_code", "")).lower() not in system_rank:
        return

    for oriented_source, oriented_target in (
        (source_code, target_code),
        (target_code, source_code),
    ):
        specificity = _orb_rule_specificity_for_orientation(
            rule,
            source_code=oriented_source,
            target_code=oriented_target,
            prediction_context=prediction_context,
        )
        if specificity is not None:
            yield (rule, specificity)


def _orb_rule_specificity_for_orientation(
    rule: object,
    *,
    source_code: str,
    target_code: str,
    prediction_context: object,
) -> int | None:
    """Retourne la spécificité si une règle correspond à l'orientation donnée."""
    source_type, source_is_planet = _body_reference_for_code(source_code, prediction_context)
    target_type, target_is_planet = _body_reference_for_code(target_code, prediction_context)
    if not _body_type_matches(
        str(getattr(rule, "source_body_type", "any")),
        source_type,
        is_planet=source_is_planet,
    ):
        return None
    if not _body_type_matches(
        str(getattr(rule, "target_body_type", "any")),
        target_type,
        is_planet=target_is_planet,
    ):
        return None
    if not _specific_code_matches(getattr(rule, "source_planet_code", None), source_code):
        return None
    if not _specific_code_matches(getattr(rule, "target_planet_code", None), target_code):
        return None
    if not _specific_code_matches(getattr(rule, "source_point_code", None), source_code):
        return None
    if not _specific_code_matches(getattr(rule, "target_point_code", None), target_code):
        return None

    score = 0
    for field_name in (
        "source_planet_code",
        "target_planet_code",
        "source_point_code",
        "target_point_code",
    ):
        if getattr(rule, field_name, None):
            score += 2
    for field_name in ("source_body_type", "target_body_type"):
        if str(getattr(rule, field_name, "any")).lower() != "any":
            score += 1
    return score


def _body_reference_for_code(body_code: str, prediction_context: object) -> tuple[str, bool]:
    """Associe un code runtime aux définitions DB de planète ou d'angle."""
    profile = _lookup_mapping_value(
        getattr(prediction_context, "planet_profiles", {}),
        body_code,
    )
    if profile is not None:
        class_code = str(getattr(profile, "class_code", "") or "").lower()
        if class_code in {"personal", "social", "transpersonal"}:
            class_code = f"{class_code}_planet"
        return (class_code or "planet", bool(getattr(profile, "is_planet", True)))

    angle_point = _lookup_mapping_value(
        getattr(prediction_context, "angle_points", {}),
        body_code,
    )
    if angle_point is not None:
        return ("angle", False)
    return ("unknown", False)


def _body_type_matches(rule_type: str, actual_type: str, *, is_planet: bool) -> bool:
    """Compare une famille de règle et une famille runtime."""
    normalized_rule = rule_type.lower()
    normalized_actual = actual_type.lower()
    if normalized_rule == "any":
        return True
    if normalized_rule == "planet":
        return is_planet
    return normalized_rule == normalized_actual


def _specific_code_matches(rule_code: object, actual_code: str) -> bool:
    """Compare une contrainte optionnelle de planète ou point."""
    return rule_code is None or str(rule_code).lower() == actual_code.lower()


def _lookup_mapping_value(mapping: object, key: str) -> object | None:
    """Lit un mapping en acceptant les variantes de casse usuelles."""
    if not isinstance(mapping, Mapping):
        return None
    candidates = (key, key.lower(), key.upper(), key.title())
    for candidate in candidates:
        if candidate in mapping:
            return mapping[candidate]
    return None


def _aspect_default_orb(prediction_context: object, aspect_code: str) -> float | None:
    """Lit l'orbe par défaut canonique d'une définition d'aspect."""
    profile = _lookup_mapping_value(
        getattr(prediction_context, "aspect_profiles", {}),
        aspect_code,
    )
    raw_orb = getattr(profile, "default_orb_deg", None)
    if isinstance(raw_orb, (int, float)):
        return float(raw_orb)
    return None


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
