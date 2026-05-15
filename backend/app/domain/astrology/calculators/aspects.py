"""Calcule les aspects astrologiques à partir de contrats runtime validés."""

from __future__ import annotations

from itertools import combinations, product

from app.domain.astrology.celestial_runtime_catalog import (
    ANGLE_POINT_CODES,
    BODY_CLASS_BY_CODE,
)
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    PLANET_BODY_TYPES,
    AspectBodyRuntimeData,
    AspectCalculationResult,
    AspectDefinitionRuntimeData,
    AspectOrbRuleRuntimeData,
)


def _angular_distance(angle_a: float, angle_b: float) -> float:
    """Retourne la plus petite distance angulaire entre deux longitudes."""
    diff = abs(angle_a - angle_b) % 360.0
    return min(diff, 360.0 - diff)


def build_aspect_body_from_position(payload: dict[str, object]) -> AspectBodyRuntimeData:
    """Valide une position brute à la frontière du calculateur."""
    return AspectBodyRuntimeData.from_position(payload, BODY_CLASS_BY_CODE, ANGLE_POINT_CODES)


def build_aspect_body_from_code(code: str) -> AspectBodyRuntimeData:
    """Valide un code de corps à la frontière du calculateur."""
    return AspectBodyRuntimeData.from_code(code, BODY_CLASS_BY_CODE, ANGLE_POINT_CODES)


def _body_matches(
    rule: AspectOrbRuleRuntimeData,
    side: str,
    body: AspectBodyRuntimeData,
) -> bool:
    """Vérifie si une règle cible le corps reçu pour un côté donné."""
    planet_code = rule.source_planet_code if side == "source" else rule.target_planet_code
    point_code = rule.source_point_code if side == "source" else rule.target_point_code
    expected_type = rule.source_body_type if side == "source" else rule.target_body_type

    if planet_code is not None and body.code != planet_code:
        return False
    if point_code is not None and body.code != point_code:
        return False
    if expected_type == "any":
        return True
    if expected_type == "planet":
        return body.body_type in PLANET_BODY_TYPES
    if expected_type == "point":
        return body.body_type in {"point", "angle"}
    return body.body_type == expected_type


def _rule_specificity_score(rule: AspectOrbRuleRuntimeData) -> int:
    """Mesure la précision d'une règle pour départager deux priorités égales."""
    score = 0
    if rule.source_planet_code is not None:
        score += 100
    if rule.target_planet_code is not None:
        score += 100
    if rule.source_point_code is not None:
        score += 90
    if rule.target_point_code is not None:
        score += 90
    if rule.source_body_type != "any":
        score += 10
    if rule.target_body_type != "any":
        score += 10
    if rule.calculation_context != "any":
        score += 5
    return score


def _rule_matches_bodies(
    rule: AspectOrbRuleRuntimeData,
    source_body: AspectBodyRuntimeData,
    target_body: AspectBodyRuntimeData,
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


def _rule_effective_priority(rule: AspectOrbRuleRuntimeData) -> int:
    """Applique les bandes métier recommandées quand elles sont plus explicites."""
    body_types = {rule.source_body_type, rule.target_body_type}
    if rule.source_planet_code is not None or rule.target_planet_code is not None:
        return max(rule.priority, 1000)
    if "angle" in body_types:
        return max(rule.priority, 900)
    if "luminary" in body_types:
        return min(max(rule.priority, 800), 899)
    if body_types & {*PLANET_BODY_TYPES, "planet"}:
        return max(rule.priority, 700)
    return rule.priority


def _system_chain(
    system_code: str,
    system_inheritance: dict[str, str | None],
    orb_rules: list[AspectOrbRuleRuntimeData],
) -> list[str]:
    """Construit la chaine local -> parent en refusant les cycles."""
    known_rule_systems = {rule.system_code for rule in orb_rules}
    normalized_system_code = system_code.strip().lower()
    if (
        orb_rules
        and normalized_system_code not in known_rule_systems
        and normalized_system_code not in system_inheritance
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
        current = system_inheritance.get(current)
    return chain


def _definition_for_system(
    aspect_code: str,
    system_code: str,
    aspect_definitions: list[AspectDefinitionRuntimeData],
) -> AspectDefinitionRuntimeData | None:
    """Retourne la définition active correspondant au système demandé."""
    normalized_aspect_code = aspect_code.strip().lower()
    normalized_system_code = system_code.strip().lower()
    return next(
        (
            definition
            for definition in aspect_definitions
            if definition.code == normalized_aspect_code
            and definition.system_code == normalized_system_code
        ),
        None,
    )


def resolve_orb(
    aspect_code: str,
    system_code: str,
    context: str,
    source_body: AspectBodyRuntimeData,
    target_body: AspectBodyRuntimeData,
    aspect_definitions: list[AspectDefinitionRuntimeData],
    orb_rules: list[AspectOrbRuleRuntimeData],
    system_inheritance: dict[str, str | None],
) -> float | None:
    """Résout l'orbe astrologique de calcul depuis les règles typées."""
    normalized_aspect_code = aspect_code.strip().lower()
    normalized_system_code = system_code.strip().lower()
    definition = _definition_for_system(
        normalized_aspect_code, normalized_system_code, aspect_definitions
    )
    if definition is None or not definition.is_enabled:
        return None

    system_chain = _system_chain(normalized_system_code, system_inheritance, orb_rules)
    depth_by_system = {code: depth for depth, code in enumerate(system_chain)}
    matching_rules = [
        (depth_by_system[rule.system_code], rule)
        for rule in orb_rules
        if rule.system_code in depth_by_system
        and rule.is_enabled
        and rule.aspect_code == normalized_aspect_code
        and rule.calculation_context in (context.strip().lower(), "any")
        and _rule_matches_bodies(rule, source_body, target_body, context)
    ]
    if matching_rules:
        selected = sorted(
            matching_rules,
            key=lambda item: (
                item[0],
                -_rule_effective_priority(item[1]),
                -_rule_specificity_score(item[1]),
            ),
        )[0][1]
        return selected.orb_deg
    return definition.default_orb_deg


def _calculation_result(
    definition: AspectDefinitionRuntimeData,
    left: AspectBodyRuntimeData,
    right: AspectBodyRuntimeData,
    orb: float,
    orb_limit: float,
    *,
    chart_a: str | None = None,
    chart_b: str | None = None,
) -> AspectCalculationResult:
    """Construit un résultat avec ordre déterministe des participants."""
    if chart_a is None and chart_b is None:
        planet_a, planet_b = sorted((left.code, right.code))
    else:
        planet_a, planet_b = left.code, right.code
    rounded_orb = round(orb, 6)
    return AspectCalculationResult(
        aspect_code=definition.code,
        planet_a=planet_a,
        planet_b=planet_b,
        chart_a=chart_a,
        chart_b=chart_b,
        angle=round(definition.angle, 6),
        orb=rounded_orb,
        orb_used=rounded_orb,
        orb_max=round(orb_limit, 6),
        family=definition.family,
        is_major=definition.is_major,
        is_minor=definition.is_minor,
        default_valence=definition.default_valence,
        interpretive_valence=definition.interpretive_valence,
        energy_type=definition.energy_type,
    )


def calculate_major_aspects(
    positions: list[AspectBodyRuntimeData],
    aspect_definitions: list[AspectDefinitionRuntimeData],
    orb_rules: list[AspectOrbRuleRuntimeData],
    system_inheritance: dict[str, str | None],
    system_code: str = "modern",
    calculation_context: str = "natal",
) -> list[dict[str, object]]:
    """Calcule les aspects majeurs entre positions planétaires."""
    enabled_definitions = [
        definition
        for definition in aspect_definitions
        if definition.is_enabled and definition.is_major and definition.system_code == system_code
    ]
    aspects: list[AspectCalculationResult] = []
    for left, right in combinations(positions, 2):
        if left.longitude is None or right.longitude is None:
            raise ValueError("aspect position longitude is required")
        distance = _angular_distance(left.longitude, right.longitude)
        for definition in enabled_definitions:
            orb = abs(distance - definition.angle)
            resolved_orb = resolve_orb(
                aspect_code=definition.code,
                system_code=system_code,
                context=calculation_context,
                source_body=left,
                target_body=right,
                aspect_definitions=aspect_definitions,
                orb_rules=orb_rules,
                system_inheritance=system_inheritance,
            )
            if resolved_orb is None:
                continue
            if orb <= resolved_orb:
                aspects.append(_calculation_result(definition, left, right, orb, resolved_orb))

    return [
        aspect.as_dict()
        for aspect in sorted(
            aspects,
            key=lambda item: (item.aspect_code, item.planet_a, item.planet_b),
        )
    ]


def calculate_interchart_aspects(
    source_positions: list[AspectBodyRuntimeData],
    target_positions: list[AspectBodyRuntimeData],
    aspect_definitions: list[AspectDefinitionRuntimeData],
    orb_rules: list[AspectOrbRuleRuntimeData],
    system_inheritance: dict[str, str | None],
    system_code: str = "modern",
) -> list[dict[str, object]]:
    """Calcule les aspects entre deux jeux de positions avec contrats typés."""
    enabled_definitions = [
        definition
        for definition in aspect_definitions
        if definition.is_enabled and definition.system_code == system_code
    ]
    aspects: list[AspectCalculationResult] = []
    for source, target in product(source_positions, target_positions):
        if source.longitude is None or target.longitude is None:
            raise ValueError("aspect position longitude is required")
        distance = _angular_distance(source.longitude, target.longitude)
        for definition in enabled_definitions:
            orb = abs(distance - definition.angle)
            resolved_orb = resolve_orb(
                aspect_code=definition.code,
                system_code=system_code,
                context="interchart",
                source_body=source,
                target_body=target,
                aspect_definitions=aspect_definitions,
                orb_rules=orb_rules,
                system_inheritance=system_inheritance,
            )
            if resolved_orb is None:
                continue
            if orb <= resolved_orb:
                aspects.append(
                    _calculation_result(
                        definition,
                        source,
                        target,
                        orb,
                        resolved_orb,
                        chart_a="source",
                        chart_b="target",
                    )
                )
    return [
        aspect.as_dict()
        for aspect in sorted(
            aspects,
            key=lambda item: (item.aspect_code, item.planet_a, item.planet_b),
        )
    ]
