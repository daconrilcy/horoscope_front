"""Calcul de balance et signature globale du theme natal.

Le calculateur consomme uniquement des runtime astrology deja construits et ne
recalcule pas les forces dans les serializers.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence

from app.domain.astrology.interpretation.dominant_aspects import DominantAspectEvaluator
from app.domain.astrology.runtime.aspect_runtime_data import AspectRuntimeData
from app.domain.astrology.runtime.chart_signature_runtime_data import (
    BalanceScoreRuntimeData,
    ChartBalanceRuntimeData,
    ChartSignatureRuntimeData,
    DominanceRankRuntimeData,
)
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData
from app.domain.astrology.runtime.sign_runtime_data import SignRuntimeData


class ChartSignatureCalculator:
    """Calcule les dominances structurelles du theme natal."""

    def __init__(self, aspect_evaluator: DominantAspectEvaluator | None = None) -> None:
        """Initialise le calculateur avec l'evaluateur d'aspects canonique."""
        self._aspect_evaluator = aspect_evaluator or DominantAspectEvaluator()

    def calculate(
        self,
        *,
        signs: Sequence[SignRuntimeData],
        houses: Sequence[HouseRuntimeData],
        aspects: Sequence[AspectRuntimeData],
    ) -> ChartBalanceRuntimeData:
        """Retourne la balance globale avec tie-break par score puis code."""
        elements = _rank_balance(_weighted_profile(signs, "element"))
        modalities = _rank_balance(_weighted_profile(signs, "modality"))
        dominant_signs = _rank_dominance(
            ((item.sign, item.weight, "sign_runtime") for item in signs if item.weight > 0.0)
        )
        dominant_planets = _rank_dominance(_planet_scores(signs))
        dominant_houses = _rank_dominance(
            (
                (str(house.number), house.strength.score, "house_strength")
                for house in houses
                if house.strength is not None and house.strength.score > 0.0
            )
        )
        dominant_aspects = _rank_dominance(
            (
                (
                    item.aspect_runtime.aspect.code,
                    item.dominance_score,
                    "dominant_aspect",
                )
                for item in self._aspect_evaluator.rank(aspects)
            )
        )
        return ChartBalanceRuntimeData(
            elements=elements,
            modalities=modalities,
            dominant_signs=dominant_signs,
            dominant_planets=dominant_planets,
            dominant_houses=dominant_houses,
            dominant_aspects=dominant_aspects,
            synthesis=ChartSignatureRuntimeData(
                primary_element=elements[0].code if elements else None,
                primary_modality=modalities[0].code if modalities else None,
                primary_sign=dominant_signs[0].code if dominant_signs else None,
                primary_planet=dominant_planets[0].code if dominant_planets else None,
                primary_house=int(dominant_houses[0].code) if dominant_houses else None,
            ),
        )


def _weighted_profile(
    signs: Sequence[SignRuntimeData],
    field_name: str,
) -> Counter[str]:
    """Agrege les poids par profil de signe deja source dans le referentiel."""
    counter: Counter[str] = Counter()
    for sign in signs:
        code = getattr(sign, field_name)
        if isinstance(code, str) and code.strip():
            counter[code] += sign.weight
    return counter


def _planet_scores(
    signs: Sequence[SignRuntimeData],
) -> tuple[tuple[str, float, str], ...]:
    """Derive la dominance planetaire des occupants et dignites actives."""
    scores: Counter[str] = Counter()
    for sign in signs:
        for occupant in sign.occupants:
            scores[occupant.planet] += max(sign.weight, 0.05)
        for dignity in sign.active_dignities:
            scores[dignity.planet] += min(abs(dignity.weight) * 0.1, 0.2)
    max_score = max(scores.values(), default=0.0)
    if max_score <= 0.0:
        return ()
    return tuple(
        (planet, round(score / max_score, 4), "sign_runtime") for planet, score in scores.items()
    )


def _rank_balance(scores: Counter[str]) -> tuple[BalanceScoreRuntimeData, ...]:
    """Classe une balance en normalisant par le plus haut score."""
    max_score = max(scores.values(), default=0.0)
    if max_score <= 0.0:
        return ()
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return tuple(
        BalanceScoreRuntimeData(code=code, score=round(score / max_score, 4), rank=index + 1)
        for index, (code, score) in enumerate(ordered)
    )


def _rank_dominance(
    items: Iterable[tuple[object, float, str]],
) -> tuple[DominanceRankRuntimeData, ...]:
    """Classe des dominances selon un tie-break stable score puis code."""
    materialized = tuple(items)
    ordered = sorted(materialized, key=lambda item: (-float(item[1]), str(item[0])))
    return tuple(
        DominanceRankRuntimeData(
            code=str(code),
            score=round(float(score), 4),
            rank=index + 1,
            source=str(source),
        )
        for index, (code, score, source) in enumerate(ordered)
    )
