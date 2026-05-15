"""Tests du contrat de force canonique des aspects."""

import pytest

from app.domain.astrology.interpretation.aspect_strength import AspectStrengthEvaluator
from app.domain.astrology.interpretation.aspect_strength_contracts import (
    AspectStrengthLevel,
    AspectStrengthReason,
    AspectStrengthRuntimeData,
)


def test_aspect_strength_uses_enum_reasons_and_normalized_score() -> None:
    """La force aspect expose un score borne et des raisons enumerees."""
    strength = AspectStrengthEvaluator().evaluate(
        aspect_code="trine",
        orb_used=0.3,
        orb_max=6.0,
        participants=("sun", "moon"),
        is_major=True,
        is_minor=False,
    )

    assert strength.normalized_score == 1.0
    assert strength.level is AspectStrengthLevel.DOMINANT
    assert strength.is_exact is True
    assert strength.is_tight is True
    assert AspectStrengthReason.MAJOR_ASPECT in strength.reasons
    assert AspectStrengthReason.EXACT_ORB in strength.reasons
    assert AspectStrengthReason.LUMINARY_PARTICIPANT in strength.reasons
    assert all(isinstance(reason, AspectStrengthReason) for reason in strength.reasons)


def test_aspect_strength_reduces_score_for_wide_orb() -> None:
    """Un orbe large produit une force plus faible qu'un orbe serre."""
    evaluator = AspectStrengthEvaluator()
    tight = evaluator.evaluate(
        aspect_code="square",
        orb_used=0.5,
        orb_max=6.0,
        participants=("mars", "saturn"),
        is_major=True,
        is_minor=False,
    )
    wide = evaluator.evaluate(
        aspect_code="square",
        orb_used=5.5,
        orb_max=6.0,
        participants=("mars", "saturn"),
        is_major=True,
        is_minor=False,
    )

    assert tight.normalized_score > wide.normalized_score
    assert AspectStrengthReason.WIDE_ORB in wide.reasons


def test_aspect_strength_contract_rejects_invalid_normalized_score() -> None:
    """Le contrat runtime refuse les scores hors echelle normalisee."""
    with pytest.raises(ValueError, match="between 0 and 1"):
        AspectStrengthRuntimeData(
            normalized_score=1.2,
            level=AspectStrengthLevel.DOMINANT,
            is_exact=True,
            is_tight=True,
            reasons=(AspectStrengthReason.EXACT_ORB,),
        )
