"""Calcule les aspects astrologiques avec une résolution explicite des orbes."""

from itertools import combinations, product

from app.core.constants import DEFAULT_FALLBACK_ORB
from app.domain.astrology.celestial_runtime_catalog import (
    ANGLE_POINT_CODES,
    BODY_CLASS_BY_CODE,
    LIGHT_BODY_CODES,
)


def _angular_distance(angle_a: float, angle_b: float) -> float:
    diff = abs(angle_a - angle_b) % 360.0
    return min(diff, 360.0 - diff)


def _normalize_pair_key(planet_a: str, planet_b: str) -> str:
    left, right = sorted((planet_a.strip().lower(), planet_b.strip().lower()))
    return f"{left}-{right}"


def _normalize_pair_overrides(value: object) -> dict[str, float]:
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, float] = {}
    for raw_key, raw_value in value.items():
        key = str(raw_key).strip().lower()
        parts = [part.strip() for part in key.split("-", maxsplit=1)]
        if len(parts) != 2 or not parts[0] or not parts[1]:
            continue
        try:
            parsed_value = float(raw_value)
        except (TypeError, ValueError):
            continue
        normalized[_normalize_pair_key(parts[0], parts[1])] = parsed_value
    return normalized


def _body_code(body: str | dict[str, object]) -> str:
    """Normalise le code d'un corps ou point astrologique."""
    if isinstance(body, dict):
        raw_code = body.get("planet_code") or body.get("point_code") or body.get("code")
    else:
        raw_code = body
    return str(raw_code).strip().lower()


def _body_type(body: str | dict[str, object]) -> str:
    """Classe un corps pour les règles d'orbe ciblées."""
    code = _body_code(body)
    if code in ANGLE_POINT_CODES:
        return "angle"
    return BODY_CLASS_BY_CODE.get(code, "point")


def _body_matches(rule: dict[str, object], side: str, body: str | dict[str, object]) -> bool:
    """Vérifie si une règle cible le corps reçu pour un côté donné."""
    body_code = _body_code(body)
    body_type = _body_type(body)
    planet_code = rule.get(f"{side}_planet_code")
    point_code = rule.get(f"{side}_point_code")
    if planet_code is not None and body_code != str(planet_code).strip().lower():
        return False
    if point_code is not None and body_code != str(point_code).strip().lower():
        return False

    expected_type = str(rule.get(f"{side}_body_type", "any")).strip().lower()
    if expected_type == "any":
        return True
    if expected_type == "planet":
        return body_type in {
            "luminary",
            "personal_planet",
            "social_planet",
            "transpersonal_planet",
        }
    if expected_type == "point":
        return body_type in {"point", "angle"}
    return body_type == expected_type


def _rule_specificity_score(rule: dict[str, object]) -> int:
    """Mesure la précision d'une règle pour départager deux priorités égales."""
    score = 0
    for side in ("source", "target"):
        if rule.get(f"{side}_planet_code") is not None:
            score += 100
        if rule.get(f"{side}_planet_id") is not None:
            score += 100
        if rule.get(f"{side}_point_code") is not None:
            score += 90
        if str(rule.get(f"{side}_body_type", "any")) != "any":
            score += 10
    if str(rule.get("calculation_context", rule.get("context", "any"))) != "any":
        score += 5
    return score


def _rule_matches_bodies(
    rule: dict[str, object],
    source_body: str | dict[str, object],
    target_body: str | dict[str, object],
    context: str,
) -> bool:
    """Applique une règle directe ou symétrique pour les aspects géométriques."""
    direct = _body_matches(rule, "source", source_body) and _body_matches(
        rule, "target", target_body
    )
    if direct:
        return True
    if context.strip().lower() not in {"natal", "any"}:
        return False
    return _body_matches(rule, "source", target_body) and _body_matches(rule, "target", source_body)


def _rule_effective_priority(rule: dict[str, object]) -> int:
    """Applique les bandes métier recommandées quand elles sont plus explicites."""
    raw_priority = int(rule.get("priority", 0))
    body_types = {
        str(rule.get("source_body_type", "any")).strip().lower(),
        str(rule.get("target_body_type", "any")).strip().lower(),
    }
    if rule.get("source_planet_code") is not None or rule.get("target_planet_code") is not None:
        return max(raw_priority, 1000)
    if rule.get("source_planet_id") is not None or rule.get("target_planet_id") is not None:
        return max(raw_priority, 1000)
    if "angle" in body_types:
        return max(raw_priority, 900)
    if "luminary" in body_types:
        return min(max(raw_priority, 800), 899)
    if body_types & {"personal_planet", "social_planet", "transpersonal_planet", "planet"}:
        return max(raw_priority, 700)
    return raw_priority


def _normalize_system_inheritance(
    system_inheritance: dict[str, str | None] | list[dict[str, object]] | None,
    orb_rules: list[dict[str, object]],
) -> dict[str, str | None]:
    """Normalise la carte d'heritage des systemes astrologiques."""
    if isinstance(system_inheritance, dict):
        return {
            str(system_code).strip().lower(): (
                None if parent_code is None else str(parent_code).strip().lower()
            )
            for system_code, parent_code in system_inheritance.items()
        }
    if isinstance(system_inheritance, list):
        return {
            str(item.get("code", item.get("name", ""))).strip().lower(): (
                None
                if item.get("inherits_from_system_code") is None
                else str(item.get("inherits_from_system_code")).strip().lower()
            )
            for item in system_inheritance
            if isinstance(item, dict) and str(item.get("code", item.get("name", ""))).strip()
        }

    inheritance: dict[str, str | None] = {}
    for rule in orb_rules:
        system_code = str(rule.get("system_code", rule.get("astral_system_code", ""))).strip()
        if not system_code:
            continue
        parent_code = rule.get("inherits_from_system_code")
        inheritance.setdefault(
            system_code.lower(),
            None if parent_code is None else str(parent_code).strip().lower(),
        )
    return inheritance


def _system_chain(
    system_code: str,
    system_inheritance: dict[str, str | None] | list[dict[str, object]] | None,
    orb_rules: list[dict[str, object]],
) -> list[str]:
    """Construit la chaine local -> parent en refusant les cycles."""
    inheritance = _normalize_system_inheritance(system_inheritance, orb_rules)
    known_rule_systems = {
        str(rule.get("system_code", rule.get("astral_system_code", ""))).strip().lower()
        for rule in orb_rules
        if str(rule.get("system_code", rule.get("astral_system_code", ""))).strip()
    }
    normalized_system_code = system_code.strip().lower()
    if (
        orb_rules
        and normalized_system_code not in known_rule_systems
        and normalized_system_code not in inheritance
    ):
        raise ValueError(f"astral system inheritance metadata missing for {normalized_system_code}")
    chain: list[str] = []
    seen: set[str] = set()
    current: str | None = normalized_system_code
    while current:
        if current in seen:
            cycle = " -> ".join([*chain, current])
            raise ValueError(f"astral system inheritance cycle detected: {cycle}")
        seen.add(current)
        chain.append(current)
        current = inheritance.get(current)
    return chain


def resolve_orb(
    aspect_code: str,
    system_code: str,
    context: str,
    source_body: str | dict[str, object],
    target_body: str | dict[str, object],
    aspect_definitions: list[dict[str, object]],
    orb_rules: list[dict[str, object]],
    system_inheritance: dict[str, str | None] | list[dict[str, object]] | None = None,
) -> float | None:
    """Résout l'orbe astrologique de calcul.

    En calcul natal pur, `orb_max` reste égal à `resolved_orb_deg`. Le
    multiplicateur de profil d'aspect relève uniquement des usages prédictifs ou
    produit, et ne doit pas être injecté dans cette résolution.
    """
    normalized_aspect_code = aspect_code.strip().lower()
    normalized_system_code = system_code.strip().lower()
    definition = next(
        (
            item
            for item in aspect_definitions
            if str(item.get("code", item.get("aspect_code", ""))).strip().lower()
            == normalized_aspect_code
            and str(item.get("system_code", item.get("astral_system_code", normalized_system_code)))
            .strip()
            .lower()
            == normalized_system_code
        ),
        None,
    )
    if definition is None or not bool(definition.get("is_enabled", True)):
        return None

    system_chain = _system_chain(normalized_system_code, system_inheritance, orb_rules)
    depth_by_system = {code: depth for depth, code in enumerate(system_chain)}
    matching_rules = []
    for rule in orb_rules:
        rule_system_code = (
            str(rule.get("system_code", rule.get("astral_system_code", ""))).strip().lower()
        )
        if rule_system_code not in depth_by_system:
            continue
        if (
            bool(rule.get("is_enabled", True))
            and str(rule.get("aspect_code", "")).strip().lower() == normalized_aspect_code
            and str(rule.get("calculation_context", rule.get("context", "any"))).strip().lower()
            in (context.strip().lower(), "any")
            and _rule_matches_bodies(rule, source_body, target_body, context)
        ):
            matching_rules.append((depth_by_system[rule_system_code], rule))
    if matching_rules:
        selected = sorted(
            matching_rules,
            key=lambda item: (
                item[0],
                -_rule_effective_priority(item[1]),
                -_rule_specificity_score(item[1]),
            ),
        )[0][1]
        return float(selected["orb_deg"])
    return float(definition["default_orb_deg"])


def _normalize_aspect_definition(
    definition: tuple[str, float] | dict[str, object],
    fallback_orb: float,
    default_system_code: str = "modern",
) -> dict[str, object]:
    if isinstance(definition, tuple):
        aspect_code, angle = definition
        return {
            "aspect_code": str(aspect_code),
            "system_code": default_system_code,
            "angle": float(angle),
            "default_orb": float(fallback_orb),
            "default_orb_deg": float(fallback_orb),
            "orb_luminaries": None,
            "orb_pair_overrides": {},
            "is_enabled": True,
        }

    aspect_code = str(definition.get("code", "")).strip()
    system_code = str(
        definition.get("system_code", definition.get("astral_system_code", default_system_code))
    ).strip()
    angle = float(definition.get("angle", 0.0))
    default_orb = float(definition.get("default_orb_deg", fallback_orb))
    orb_luminaries_raw = definition.get("orb_luminaries")
    orb_luminaries = float(orb_luminaries_raw) if orb_luminaries_raw is not None else None

    # Prioritize 'orb_pair_overrides' then 'orb_pairs' then 'orb_overrides'
    pair_overrides_raw = (
        definition.get("orb_pair_overrides")
        or definition.get("orb_pairs")
        or definition.get("orb_overrides")
    )
    pair_overrides = _normalize_pair_overrides(pair_overrides_raw)

    return {
        "aspect_code": aspect_code,
        "system_code": system_code,
        "angle": angle,
        "default_orb": default_orb,
        "default_orb_deg": default_orb,
        "orb_luminaries": orb_luminaries,
        "orb_pair_overrides": pair_overrides,
        "is_enabled": bool(definition.get("is_enabled", True)),
    }


def calculate_major_aspects(
    positions: list[dict[str, object]],
    aspect_definitions: list[tuple[str, float] | dict[str, object]],
    max_orb: float = DEFAULT_FALLBACK_ORB,
    orb_rules: list[dict[str, object]] | None = None,
    system_code: str = "modern",
    calculation_context: str = "natal",
    system_inheritance: dict[str, str | None] | list[dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    """Calcule les aspects entre positions planétaires avec résolution hiérarchique.

    Sans `orb_rules`, l'ancien chemin reste pair_override > luminary_override >
    default_orb. Avec `orb_rules`, les exceptions ciblées sont résolues avant le
    fallback `default_orb_deg`.
    """
    normalized_definitions = [
        _normalize_aspect_definition(definition, max_orb, system_code)
        for definition in aspect_definitions
    ]

    # Pre-normalize planet data to avoid repeated work in the hot loop
    prepared_positions = []
    for pos in positions:
        code = str(pos["planet_code"]).strip().lower()
        prepared_positions.append(
            {
                "planet_code": code,
                "longitude": float(pos["longitude"]),
                "is_luminary": code in LIGHT_BODY_CODES,
            }
        )

    aspects: list[dict[str, object]] = []
    for left, right in combinations(prepared_positions, 2):
        planet_a = left["planet_code"]
        planet_b = right["planet_code"]
        is_any_luminary = left["is_luminary"] or right["is_luminary"]
        pair_key = f"{planet_a}-{planet_b}" if planet_a < planet_b else f"{planet_b}-{planet_a}"

        distance = _angular_distance(left["longitude"], right["longitude"])

        for aspect_def in normalized_definitions:
            if not bool(aspect_def["is_enabled"]):
                continue
            angle = float(aspect_def["angle"])
            orb = abs(distance - angle)

            # Resolve the threshold limit for this pair
            if orb_rules is not None:
                resolved_orb = resolve_orb(
                    aspect_code=str(aspect_def["aspect_code"]),
                    system_code=system_code,
                    context=calculation_context,
                    source_body=str(planet_a),
                    target_body=str(planet_b),
                    aspect_definitions=normalized_definitions,
                    orb_rules=orb_rules,
                    system_inheritance=system_inheritance,
                )
                if resolved_orb is None:
                    continue
                orb_limit = resolved_orb
            elif pair_key in aspect_def["orb_pair_overrides"]:
                orb_limit = aspect_def["orb_pair_overrides"][pair_key]
            elif is_any_luminary and aspect_def["orb_luminaries"] is not None:
                orb_limit = aspect_def["orb_luminaries"]
            else:
                orb_limit = aspect_def["default_orb"]

            if orb <= orb_limit:
                # Standardize planet order (alphabetical) for stable API output
                p_a, p_b = sorted((planet_a, planet_b))
                aspects.append(
                    {
                        "aspect_code": aspect_def["aspect_code"],
                        "planet_a": p_a,
                        "planet_b": p_b,
                        "angle": round(angle, 6),
                        "orb": round(orb, 6),  # backward compat: actual angular deviation
                        "orb_used": round(orb, 6),  # story 24-2: actual angular deviation
                        "orb_max": round(orb_limit, 6),  # story 24-2: resolved max threshold
                    }
                )

    aspects.sort(
        key=lambda item: (
            str(item["aspect_code"]),
            str(item["planet_a"]),
            str(item["planet_b"]),
        )
    )
    return aspects


def calculate_interchart_aspects(
    source_positions: list[dict[str, object]],
    target_positions: list[dict[str, object]],
    aspect_definitions: list[tuple[str, float] | dict[str, object]],
    max_orb: float = DEFAULT_FALLBACK_ORB,
    orb_rules: list[dict[str, object]] | None = None,
    system_code: str = "modern",
    system_inheritance: dict[str, str | None] | list[dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    """Calcule les aspects entre deux jeux de positions sans referentiel dedie."""
    normalized_definitions = [
        _normalize_aspect_definition(definition, max_orb, system_code)
        for definition in aspect_definitions
    ]
    aspects: list[dict[str, object]] = []
    for source, target in product(source_positions, target_positions):
        source_code = str(source["planet_code"]).strip().lower()
        target_code = str(target["planet_code"]).strip().lower()
        distance = _angular_distance(float(source["longitude"]), float(target["longitude"]))
        for aspect_def in normalized_definitions:
            if not bool(aspect_def["is_enabled"]):
                continue
            angle = float(aspect_def["angle"])
            orb = abs(distance - angle)
            if orb_rules is not None:
                resolved_orb = resolve_orb(
                    aspect_code=str(aspect_def["aspect_code"]),
                    system_code=system_code,
                    context="interchart",
                    source_body=source_code,
                    target_body=target_code,
                    aspect_definitions=normalized_definitions,
                    orb_rules=orb_rules,
                    system_inheritance=system_inheritance,
                )
                if resolved_orb is None:
                    continue
                orb_limit = resolved_orb
            else:
                pair_key = _normalize_pair_key(source_code, target_code)
                source_is_luminary = source_code in LIGHT_BODY_CODES
                target_is_luminary = target_code in LIGHT_BODY_CODES
                if pair_key in aspect_def["orb_pair_overrides"]:
                    orb_limit = aspect_def["orb_pair_overrides"][pair_key]
                elif (source_is_luminary or target_is_luminary) and aspect_def[
                    "orb_luminaries"
                ] is not None:
                    orb_limit = aspect_def["orb_luminaries"]
                else:
                    orb_limit = aspect_def["default_orb"]
            if orb <= orb_limit:
                aspects.append(
                    {
                        "aspect_code": aspect_def["aspect_code"],
                        "planet_a": source_code,
                        "planet_b": target_code,
                        "chart_a": "source",
                        "chart_b": "target",
                        "angle": round(angle, 6),
                        "orb": round(orb, 6),
                        "orb_used": round(orb, 6),
                        "orb_max": round(orb_limit, 6),
                    }
                )
    aspects.sort(
        key=lambda item: (
            str(item["aspect_code"]),
            str(item["planet_a"]),
            str(item["planet_b"]),
        )
    )
    return aspects
