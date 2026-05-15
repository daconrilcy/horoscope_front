"""Evaluation astrologique de la force des aspects.

Ce module convertit l'orbe, la famille d'aspect et les participants en score
normalise, sans categorie produit ni dependance prediction.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog

from .aspect_strength_contracts import (
    AspectStrengthReason,
    AspectStrengthRuntimeData,
    resolve_aspect_strength_level,
)


@dataclass(frozen=True, slots=True)
class AspectStrengthThresholds:
    """Seuils explicites de qualification technique de l'orbe."""

    exact_orb_deg: float
    tight_ratio: float
    moderate_ratio: float


class AspectStrengthEvaluator:
    """Calcule la force technique d'un aspect a partir de son runtime brut."""

    def __init__(
        self,
        thresholds: AspectStrengthThresholds | None = None,
        celestial_catalog: CelestialRuntimeCatalog | None = None,
    ) -> None:
        """Initialise l'evaluateur avec des seuils injectables et immutables."""
        self._thresholds = thresholds or AspectStrengthThresholds(
            exact_orb_deg=0.5,
            tight_ratio=0.25,
            moderate_ratio=0.6,
        )
        self._celestial_catalog = celestial_catalog or CelestialRuntimeCatalog.empty()

    def evaluate(
        self,
        *,
        aspect_code: str,
        orb_used: float,
        orb_max: float,
        participants: Iterable[str],
        is_major: bool,
        is_minor: bool,
        phase_type: str | None = None,
    ) -> AspectStrengthRuntimeData:
        """Retourne le score normalise, le niveau et les raisons enumerees."""
        del aspect_code
        participant_codes = tuple(code.strip().lower() for code in participants)
        safe_orb_max = max(float(orb_max), 0.01)
        ratio = min(max(float(orb_used) / safe_orb_max, 0.0), 1.0)
        score = 1.0 - ratio
        reasons: list[AspectStrengthReason] = []

        if is_major:
            score += 0.12
            reasons.append(AspectStrengthReason.MAJOR_ASPECT)
        elif is_minor:
            score += 0.04
            reasons.append(AspectStrengthReason.MINOR_ASPECT)
        else:
            reasons.append(AspectStrengthReason.ADVANCED_ASPECT)

        if float(orb_used) <= self._thresholds.exact_orb_deg:
            score += 0.15
            reasons.append(AspectStrengthReason.EXACT_ORB)
        elif ratio <= self._thresholds.tight_ratio:
            score += 0.08
            reasons.append(AspectStrengthReason.TIGHT_ORB)
        elif ratio <= self._thresholds.moderate_ratio:
            reasons.append(AspectStrengthReason.MODERATE_ORB)
        else:
            reasons.append(AspectStrengthReason.WIDE_ORB)

        if any(self._celestial_catalog.is_luminary(code) for code in participant_codes):
            score += 0.08
            reasons.append(AspectStrengthReason.LUMINARY_PARTICIPANT)
        if any(self._celestial_catalog.is_angle_point(code) for code in participant_codes):
            score += 0.06
            reasons.append(AspectStrengthReason.ANGLE_PARTICIPANT)
        if len(participant_codes) == 2 and all(
            self._celestial_catalog.is_transpersonal(code) for code in participant_codes
        ):
            score -= 0.08
            reasons.append(AspectStrengthReason.TRANSPERSONAL_PAIR)

        normalized_phase = (phase_type or "").strip().lower()
        if normalized_phase == "applying":
            score += 0.04
            reasons.append(AspectStrengthReason.APPLYING_PHASE)
        elif normalized_phase == "separating":
            reasons.append(AspectStrengthReason.SEPARATING_PHASE)

        bounded_score = round(min(max(score, 0.0), 1.0), 2)
        return AspectStrengthRuntimeData(
            normalized_score=bounded_score,
            level=resolve_aspect_strength_level(bounded_score),
            is_exact=float(orb_used) <= self._thresholds.exact_orb_deg,
            is_tight=ratio <= self._thresholds.tight_ratio,
            reasons=tuple(reasons),
        )


def participant_class(
    code: str,
    celestial_catalog: CelestialRuntimeCatalog | None = None,
) -> str:
    """Retourne la classe astrologique d'un participant."""
    catalog = celestial_catalog or CelestialRuntimeCatalog.empty()
    return catalog.body_type_for_code(code)
