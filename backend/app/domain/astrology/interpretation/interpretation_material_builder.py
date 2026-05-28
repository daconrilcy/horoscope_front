# Builder canonique du materiau interpretatif theme astral.
"""Selectionne des textes sources rattaches aux faits astrologiques calcules."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    AspectInterpretationRuntimeData,
    ChartInterpretationInputRuntimeData,
    ChartObjectInterpretationRuntimeData,
    DominanceInterpretationRuntimeData,
    HousePositionInterpretationRuntimeData,
)

from .interpretation_material_contracts import (
    INTERPRETATION_MATERIAL_KEYS,
    DeliveryProfile,
    InterpretationMaterialBlock,
    InterpretationMaterialItem,
    InterpretationMaterialKey,
    InterpretationMaterialSource,
)


@dataclass(frozen=True, slots=True)
class _ProfilePolicy:
    """Politique de seuils et quotas pour un profil de livraison."""

    threshold: float
    limits: Mapping[InterpretationMaterialKey, int]


_PROFILE_POLICIES: dict[DeliveryProfile, _ProfilePolicy] = {
    "free": _ProfilePolicy(
        threshold=0.35,
        limits={key: 1 for key in INTERPRETATION_MATERIAL_KEYS},
    ),
    "basic": _ProfilePolicy(
        threshold=0.2,
        limits={key: 3 for key in INTERPRETATION_MATERIAL_KEYS},
    ),
    "premium": _ProfilePolicy(
        threshold=0.0,
        limits={key: 6 for key in INTERPRETATION_MATERIAL_KEYS},
    ),
}


class InterpretationMaterialBuilder:
    """Construit le bloc source-attribue `interpretation_material`."""

    def build(
        self,
        chart_input: ChartInterpretationInputRuntimeData,
        *,
        sources: Iterable[InterpretationMaterialSource],
        delivery_profile: DeliveryProfile,
    ) -> InterpretationMaterialBlock:
        """Associe les sources aux faits calcules puis applique score et quotas."""
        policy = _PROFILE_POLICIES[delivery_profile]
        source_index = _SourceIndex(sources)
        selected = {
            key: self._select_section(
                candidates=_candidate_items(key, chart_input, source_index),
                limit=policy.limits[key],
                threshold=policy.threshold,
            )
            for key in INTERPRETATION_MATERIAL_KEYS
        }
        return InterpretationMaterialBlock(**selected)

    def _select_section(
        self,
        *,
        candidates: Iterable[InterpretationMaterialItem],
        limit: int,
        threshold: float,
    ) -> tuple[InterpretationMaterialItem, ...]:
        """Trie de maniere stable et coupe selon le profil de livraison."""
        ranked = sorted(
            (item for item in candidates if item.weight >= threshold),
            key=lambda item: (-item.weight, item.fact_ref, item.source_ref),
        )
        return tuple(ranked[:limit])


class _SourceIndex:
    """Index de sources explicites sans acces DB ni fallback implicite."""

    def __init__(self, sources: Iterable[InterpretationMaterialSource]) -> None:
        self._sources = tuple(sources)

    def find(
        self,
        section: InterpretationMaterialKey,
        **criteria: object,
    ) -> tuple[InterpretationMaterialSource, ...]:
        """Retourne seulement les sources qui correspondent exactement au fait."""
        return tuple(
            source
            for source in self._sources
            if source.section == section
            and all(
                _matches_optional(getattr(source, field_name), value)
                for field_name, value in criteria.items()
            )
            and _source_has_text(source)
            and source.source_ref.strip()
        )


def _candidate_items(
    section: InterpretationMaterialKey,
    chart_input: ChartInterpretationInputRuntimeData,
    source_index: _SourceIndex,
) -> tuple[InterpretationMaterialItem, ...]:
    """Route une section vers les faits calcules qui en sont proprietaires."""
    if section == "planet_sign_interpretations":
        return tuple(
            _item_from_source(
                source, fact_ref=_planet_sign_fact_ref(item), fact_weight=_object_weight(item)
            )
            for item in chart_input.objects
            for source in source_index.find(
                section,
                planet_code=item.code,
                sign_code=item.zodiac_position.sign_code,
            )
        )
    if section == "planet_house_interpretations":
        return tuple(
            _item_from_source(
                source, fact_ref=_planet_house_fact_ref(item), fact_weight=_house_weight(item)
            )
            for item in chart_input.house_positions
            for source in source_index.find(
                section,
                planet_code=item.code,
                house_number=item.house_number,
            )
        )
    if section == "aspect_interpretations":
        return tuple(
            _item_from_source(
                source, fact_ref=_aspect_fact_ref(item), fact_weight=_aspect_weight(item)
            )
            for item in chart_input.aspects
            for source in source_index.find(section, aspect_code=item.code)
        )
    if section == "dominant_themes":
        return tuple(
            _item_from_source(source, fact_ref=_dominance_fact_ref(item), fact_weight=item.score)
            for item in chart_input.dominance
            for source in source_index.find(section, dominance_code=item.code)
        )
    if section in {"tensions", "resources", "integration_levers", "warnings"}:
        return _derived_signal_items(section, chart_input, source_index)
    raise ValueError(f"unsupported interpretation material section: {section}")


def _derived_signal_items(
    section: InterpretationMaterialKey,
    chart_input: ChartInterpretationInputRuntimeData,
    source_index: _SourceIndex,
) -> tuple[InterpretationMaterialItem, ...]:
    """Selectionne tensions, ressources, leviers et limites depuis les faits calcules."""
    candidates: list[InterpretationMaterialItem] = []
    candidates.extend(
        _item_from_source(source, fact_ref=_dominance_fact_ref(item), fact_weight=item.score)
        for item in chart_input.dominance
        for source in source_index.find(section, dominance_code=item.code)
    )
    candidates.extend(
        _item_from_source(source, fact_ref=_aspect_fact_ref(item), fact_weight=_aspect_weight(item))
        for item in chart_input.aspects
        for source in source_index.find(section, aspect_code=item.code)
    )
    candidates.extend(
        _item_from_source(
            source,
            fact_ref=f"advanced_condition:{item.condition_code}",
            fact_weight=max(0.0, item.ranking_weight),
        )
        for item in chart_input.advanced_condition_facts
        for source in source_index.find(section, condition_code=item.condition_code)
    )
    return tuple(candidates)


def _item_from_source(
    source: InterpretationMaterialSource,
    *,
    fact_ref: str,
    fact_weight: float,
) -> InterpretationMaterialItem:
    """Compose un item sans inventer de texte absent de la source."""
    weight = round(max(0.0, source.base_weight) + max(0.0, fact_weight), 4)
    return InterpretationMaterialItem(
        source_ref=source.source_ref,
        fact_ref=fact_ref,
        theme=source.theme,
        keywords=source.keywords,
        interpretive_text=_clean_optional(source.interpretive_text),
        writing_hint=None
        if _clean_optional(source.interpretive_text) is not None
        else _clean_optional(source.writing_hint),
        risk=source.risk,
        resource=source.resource,
        weight=weight,
        selection_reason=f"matched_calculated_fact:{fact_ref}",
    )


def _source_has_text(source: InterpretationMaterialSource) -> bool:
    """Refuse les sources sans texte ni consigne redactionnelle explicite."""
    return (
        _clean_optional(source.interpretive_text) is not None
        or _clean_optional(source.writing_hint) is not None
    )


def _clean_optional(value: str | None) -> str | None:
    """Normalise les chaines optionnelles sans creer de contenu de remplacement."""
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _matches_optional(source_value: object, fact_value: object) -> bool:
    """Autorise une source plus large seulement quand la DB ne porte pas l'axe calcule."""
    return source_value is None or source_value == fact_value


def _planet_sign_fact_ref(item: ChartObjectInterpretationRuntimeData) -> str:
    """Identifie le fait calcule planete-signe."""
    return f"object:{item.code}:sign:{item.zodiac_position.sign_code}"


def _planet_house_fact_ref(item: HousePositionInterpretationRuntimeData) -> str:
    """Identifie le fait calcule planete-maison."""
    return f"object:{item.code}:house:{item.house_number}"


def _aspect_fact_ref(item: AspectInterpretationRuntimeData) -> str:
    """Identifie le fait calcule d'aspect."""
    participants = "-".join(item.participant_codes)
    return f"aspect:{item.code}:{participants}"


def _dominance_fact_ref(item: DominanceInterpretationRuntimeData) -> str:
    """Identifie un fait calcule de dominance."""
    return f"dominance:{item.code}"


def _object_weight(item: ChartObjectInterpretationRuntimeData) -> float:
    """Calcule un poids local depuis les scores deja presents sur l'objet."""
    if item.dominance is not None:
        return item.dominance.score
    if item.dignity is not None:
        return max(0.0, min(1.0, item.dignity.total_score / 10.0))
    return 0.0


def _house_weight(item: HousePositionInterpretationRuntimeData) -> float:
    """Pondere legerement les maisons angulaires sans recalcul astrologique."""
    return 0.25 if item.house_modality == "angular" else 0.0


def _aspect_weight(item: AspectInterpretationRuntimeData) -> float:
    """Pondere les aspects majeurs et serres depuis leurs faits runtime."""
    major_bonus = 0.3 if item.is_major else 0.0
    orb_ratio = 0.0 if item.orb_max <= 0 else max(0.0, 1.0 - (item.orb / item.orb_max))
    return round(major_bonus + orb_ratio, 4)
