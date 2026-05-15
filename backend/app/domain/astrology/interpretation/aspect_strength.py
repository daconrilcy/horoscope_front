"""Evaluation astrologique de la force des aspects.

Ce module convertit l'orbe, la famille d'aspect et les participants en score
normalise, sans categorie produit ni dependance prediction.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.astrology.celestial_runtime_catalog import (
    ANGLE_POINT_CODES,
    BODY_CLASS_BY_CODE,
    LIGHT_BODY_CODES,
    OUTER_PLANET_CODES,
)

from .aspect_strength_contracts import (
    AspectStrengthReason,
    AspectStrengthRuntimeData,
    resolve_aspect_strength_level,
)

EXACT_ORB_DEG = 0.5
TIGHT_RATIO = 0.25
MODERATE_RATIO = 0.6


class AspectStrengthEvaluator:
    """Calcule la force technique d'un aspect a partir de son runtime brut."""

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

        if float(orb_used) <= EXACT_ORB_DEG:
            score += 0.15
            reasons.append(AspectStrengthReason.EXACT_ORB)
        elif ratio <= TIGHT_RATIO:
            score += 0.08
            reasons.append(AspectStrengthReason.TIGHT_ORB)
        elif ratio <= MODERATE_RATIO:
            reasons.append(AspectStrengthReason.MODERATE_ORB)
        else:
            reasons.append(AspectStrengthReason.WIDE_ORB)

        if any(code in LIGHT_BODY_CODES for code in participant_codes):
            score += 0.08
            reasons.append(AspectStrengthReason.LUMINARY_PARTICIPANT)
        if any(code in ANGLE_POINT_CODES for code in participant_codes):
            score += 0.06
            reasons.append(AspectStrengthReason.ANGLE_PARTICIPANT)
        if len(participant_codes) == 2 and all(
            code in OUTER_PLANET_CODES for code in participant_codes
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
            is_exact=float(orb_used) <= EXACT_ORB_DEG,
            is_tight=ratio <= TIGHT_RATIO,
            reasons=tuple(reasons),
        )


def participant_class(code: str) -> str:
    """Retourne la classe astrologique d'un participant."""
    normalized_code = code.strip().lower()
    if normalized_code in ANGLE_POINT_CODES:
        return "angle"
    return BODY_CLASS_BY_CODE.get(normalized_code, "point")
