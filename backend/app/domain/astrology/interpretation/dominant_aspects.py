"""Evaluation des aspects dominants.

Le classement reutilise `AspectRuntimeData` et reste dans astrology, sans
introduire de scoring produit ni de referentiel dedie a la synastrie.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.astrology.planet_catalog import planet_codes
from app.domain.astrology.runtime.aspect_runtime_data import AspectRuntimeData
from app.domain.astrology.runtime.dominant_aspect_runtime_data import (
    DominantAspectReason,
    DominantAspectRuntimeData,
)

DOMINANT_ASPECT_LUMINARY_CODES = frozenset(planet_codes()[:2])


class DominantAspectEvaluator:
    """Classe les aspects dominants de maniere deterministe."""

    def rank(self, aspects: Sequence[AspectRuntimeData]) -> tuple[DominantAspectRuntimeData, ...]:
        """Retourne les aspects tries par score decroissant et ordre stable."""
        scored = [self._score(aspect) for aspect in aspects]
        ordered = sorted(
            scored,
            key=lambda item: (
                -item[0],
                item[1].aspect.code,
                item[1].participants.planet_a,
                item[1].participants.planet_b,
            ),
        )
        return tuple(
            DominantAspectRuntimeData(
                aspect_runtime=aspect,
                dominance_score=score,
                rank=index + 1,
                reasons=reasons,
                score_factors=tuple(reason.value for reason in reasons),
            )
            for index, (score, aspect, reasons) in enumerate(ordered)
        )

    def _score(
        self,
        aspect: AspectRuntimeData,
    ) -> tuple[float, AspectRuntimeData, tuple[DominantAspectReason, ...]]:
        """Calcule le score de dominance structurelle d'un aspect."""
        score = aspect.strength.normalized_score
        reasons: list[DominantAspectReason] = []
        if aspect.metadata.is_exact:
            score += 0.18
            reasons.append(DominantAspectReason.EXACT_ORB)
        elif aspect.metadata.is_tight:
            score += 0.1
            reasons.append(DominantAspectReason.TIGHT_ORB)
        if aspect.metadata.is_major:
            score += 0.08
            reasons.append(DominantAspectReason.MAJOR_ASPECT)
        if {
            aspect.participants.planet_a,
            aspect.participants.planet_b,
        } & DOMINANT_ASPECT_LUMINARY_CODES:
            score += 0.08
            reasons.append(DominantAspectReason.LUMINARY_INVOLVED)
        if aspect.strength.normalized_score >= 0.65:
            reasons.append(DominantAspectReason.HIGH_STRENGTH)
        return round(min(score, 1.0), 4), aspect, tuple(reasons)
