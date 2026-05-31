# Commentaire global: ce module extrait les faits natals Basic depuis les
# projections runtime existantes.
"""Builder canonique du graphe factuel natal Basic."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    AdvancedConditionInterpretationRuntimeData,
    AspectInterpretationRuntimeData,
    ChartInterpretationInputRuntimeData,
    ChartObjectInterpretationRuntimeData,
    DignityInterpretationRuntimeData,
    DominanceInterpretationRuntimeData,
    HousePositionInterpretationRuntimeData,
    RulershipInterpretationRuntimeData,
)
from app.domain.astrology.interpretation.natal_fact_graph import (
    NatalFact,
    NatalFactFamily,
    NatalFactGraph,
)

_GRAPH_VERSION = "natal_fact_graph.basic.v1"


def build_basic_natal_fact_graph(
    interpretation_input: ChartInterpretationInputRuntimeData,
    eligibility_context: EligibilityContext,
) -> NatalFactGraph:
    """Construit un graphe Basic depuis les projections deja resolues."""
    facts = tuple(
        sorted(
            _fact_stream(interpretation_input, eligibility_context),
            key=lambda fact: fact.fact_id,
        )
    )
    graph_id = _stable_id(
        "graph",
        interpretation_input.chart_id or "anonymous",
        eligibility_context.birth_time_status,
        *(fact.fact_id for fact in facts),
    )
    return NatalFactGraph(graph_id=graph_id, facts=facts)


def _fact_stream(
    interpretation_input: ChartInterpretationInputRuntimeData,
    eligibility_context: EligibilityContext,
) -> Iterable[NatalFact]:
    """Regroupe les extracteurs sans changer les donnees astrologiques."""
    yield from _object_facts(interpretation_input.objects, eligibility_context)
    yield from _aspect_facts(interpretation_input.aspects)
    yield from _house_facts(interpretation_input.house_positions, eligibility_context)
    yield from _rulership_facts(interpretation_input.rulerships, eligibility_context)
    yield from _condition_facts(
        interpretation_input.dignities,
        interpretation_input.advanced_condition_facts,
    )
    yield from _balance_facts(interpretation_input.sign_profile_balances)


def _object_facts(
    objects: Sequence[ChartObjectInterpretationRuntimeData],
    eligibility_context: EligibilityContext,
) -> Iterable[NatalFact]:
    """Extrait positions, luminaires, angles, signes et noeuds depuis les objets."""
    for item in objects:
        classifications = set(item.classifications)
        source_paths = _object_source_paths(item)
        if "luminary" in classifications:
            yield _fact(
                NatalFactFamily.LUMINARY,
                (item.code,),
                source_paths=source_paths,
                editorial_candidate=True,
            )
        if "planet" in classifications:
            yield _fact(
                NatalFactFamily.PLANET_POSITION,
                (item.code, item.zodiac_position.sign_code),
                source_paths=source_paths,
                editorial_candidate=True,
            )
        if "angle" in classifications and eligibility_context.can_use_angles:
            yield _fact(
                NatalFactFamily.ANGLE,
                (item.code,),
                requires_birth_time=True,
                source_paths=source_paths,
                editorial_candidate=True,
            )
        if _is_lunar_node_code(item.code):
            yield _fact(
                NatalFactFamily.NODE,
                (item.code, item.zodiac_position.sign_code),
                source_paths=source_paths,
                editorial_candidate=True,
            )
        yield _fact(
            NatalFactFamily.SIGN_EMPHASIS,
            (item.zodiac_position.sign_code, item.code),
            source_paths=source_paths,
            editorial_candidate=False,
        )


def _aspect_facts(aspects: Sequence[AspectInterpretationRuntimeData]) -> Iterable[NatalFact]:
    """Expose les aspects majeurs deja presents dans le runtime interpretatif."""
    for item in aspects:
        if not item.is_major:
            continue
        ordered_pair = tuple(sorted(item.participant_codes))
        yield _fact(
            NatalFactFamily.ASPECT,
            (*ordered_pair, item.code),
            source_paths=(f"aspects.{ordered_pair[0]}:{item.code}:{ordered_pair[1]}", item.source),
            editorial_candidate=True,
        )


def _house_facts(
    house_positions: Sequence[HousePositionInterpretationRuntimeData],
    eligibility_context: EligibilityContext,
) -> Iterable[NatalFact]:
    """Expose les maisons uniquement quand le contexte horaire les autorise."""
    if not eligibility_context.can_use_houses:
        return
    for item in house_positions:
        yield _fact(
            NatalFactFamily.HOUSE_EMPHASIS,
            (item.code, f"house:{item.house_number}", item.house_modality),
            requires_birth_time=True,
            source_paths=(f"house_positions.{item.code}", item.source),
            editorial_candidate=True,
        )


def _rulership_facts(
    rulerships: Sequence[RulershipInterpretationRuntimeData],
    eligibility_context: EligibilityContext,
) -> Iterable[NatalFact]:
    """Expose les maitrises seulement quand l'heure les rend eligibles."""
    if not eligibility_context.can_use_house_rulers:
        return
    for item in rulerships:
        ruled_houses = tuple(f"house:{house_number}" for house_number in item.rules_houses)
        yield _fact(
            NatalFactFamily.RULERSHIP,
            (item.code, *ruled_houses, *item.rules_signs),
            requires_birth_time=True,
            source_paths=(f"rulerships.{item.code}", item.source, *item.rulership_sources),
            editorial_candidate=True,
        )


def _condition_facts(
    dignities: Sequence[DignityInterpretationRuntimeData],
    advanced_conditions: Sequence[AdvancedConditionInterpretationRuntimeData],
) -> Iterable[NatalFact]:
    """Expose les conditions et dignites deja resolues par les owners amont."""
    for item in dignities:
        for condition_code in item.condition_codes:
            yield _fact(
                NatalFactFamily.CONDITION,
                (item.code, condition_code),
                source_paths=(f"dignities.{item.code}.{condition_code}", item.source),
                editorial_candidate=True,
            )
    for item in advanced_conditions:
        yield _fact(
            NatalFactFamily.CONDITION,
            (item.source_planet_code, item.condition_code),
            source_paths=(f"advanced_conditions.{item.condition_code}", item.reference_version),
            editorial_candidate=True,
        )


def _balance_facts(sign_profile_balances: object) -> Iterable[NatalFact]:
    """Expose les equilibres de signes depuis les balances runtime disponibles."""
    if sign_profile_balances is None:
        return
    for item in sign_profile_balances.elements:
        yield _balance_fact(NatalFactFamily.ELEMENT_BALANCE, item, "sign_profile_balances.elements")
    for item in sign_profile_balances.modalities:
        yield _balance_fact(
            NatalFactFamily.MODALITY_BALANCE, item, "sign_profile_balances.modalities"
        )


def _balance_fact(
    family: NatalFactFamily,
    item: DominanceInterpretationRuntimeData,
    source_path: str,
) -> NatalFact:
    """Projette une balance runtime en fait atomique."""
    return _fact(
        family,
        (item.code,),
        source_paths=(f"{source_path}.{item.code}", item.source),
        editorial_candidate=False,
    )


def _fact(
    family: NatalFactFamily,
    objects: tuple[str, ...],
    *,
    source_paths: tuple[str, ...],
    editorial_candidate: bool,
    requires_birth_time: bool = False,
    confidence: str = "runtime_confirmed",
) -> NatalFact:
    """Construit un fait avec identifiant stable derive de son contenu."""
    normalized_objects = tuple(str(item).strip().lower() for item in objects)
    return NatalFact(
        fact_id=_stable_id(family.value, *normalized_objects),
        family=family,
        objects=normalized_objects,
        confidence=confidence,
        requires_birth_time=requires_birth_time,
        source_paths=tuple(str(item) for item in source_paths if str(item).strip()),
        editorial_candidate=editorial_candidate,
    )


def _stable_id(prefix: str, *parts: str) -> str:
    """Produit un identifiant court stable a partir de valeurs deja projetees."""
    payload = json.dumps(
        [prefix, *parts], ensure_ascii=True, sort_keys=False, separators=(",", ":")
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _object_source_paths(item: ChartObjectInterpretationRuntimeData) -> tuple[str, ...]:
    """Retourne les chemins de source disponibles pour un objet interpretable."""
    return (
        f"objects.{item.code}",
        f"source.{item.source_type.value}.{item.source_key}",
        *item.source_codes,
    )


def _is_lunar_node_code(code: str) -> bool:
    """Reconnait les noeuds par le code deja fourni dans la projection runtime."""
    normalized = code.strip().lower()
    return normalized in {"north_node", "south_node", "true_node", "mean_node"}
