"""Tests du classement des aspects dominants."""

import pytest

from app.domain.astrology.interpretation.dominant_aspects import DominantAspectEvaluator
from app.domain.astrology.natal_calculation import AspectResult
from app.domain.astrology.runtime.dominant_aspect_runtime_data import (
    DominantAspectReason,
    DominantAspectRuntimeData,
)


def _runtime(aspect_code: str, orb: float) -> object:
    runtime = AspectResult(
        aspect_code=aspect_code,
        planet_a="sun",
        planet_b="moon",
        angle=120.0 if aspect_code == "trine" else 90.0,
        orb=orb,
        orb_used=orb,
        orb_max=6.0,
    ).aspect_runtime
    assert runtime is not None
    return runtime


def test_dominant_aspects_are_ranked_deterministically() -> None:
    """Le classement suit le score puis un ordre stable."""
    wide = _runtime("trine", 4.0)
    tight = _runtime("square", 0.2)

    result = DominantAspectEvaluator().rank((wide, tight))

    assert result[0].aspect_runtime.aspect.code == "square"
    assert result[0].rank == 1
    assert result[1].rank == 2


def test_dominance_score_increases_when_orb_tightens() -> None:
    """Un orbe plus serre augmente la dominance structurelle."""
    loose = DominantAspectEvaluator().rank((_runtime("trine", 5.0),))[0]
    tight = DominantAspectEvaluator().rank((_runtime("trine", 0.2),))[0]

    assert tight.dominance_score > loose.dominance_score
    assert DominantAspectReason.EXACT_ORB in tight.reasons


def test_dominant_aspect_contract_rejects_invalid_rank_and_score() -> None:
    """Le contrat dominant refuse un score ou un rang non canonique."""
    runtime = _runtime("trine", 0.2)

    with pytest.raises(ValueError, match="score"):
        DominantAspectRuntimeData(
            aspect_runtime=runtime,
            dominance_score=1.4,
            rank=1,
            reasons=(DominantAspectReason.EXACT_ORB,),
        )
    with pytest.raises(ValueError, match="rank"):
        DominantAspectRuntimeData(
            aspect_runtime=runtime,
            dominance_score=0.8,
            rank=0,
            reasons=(DominantAspectReason.EXACT_ORB,),
        )
