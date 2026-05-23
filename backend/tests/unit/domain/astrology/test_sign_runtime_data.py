"""Tests du contrat runtime canonique des signes natals."""

import pytest

from app.domain.astrology.runtime.sign_runtime_data import (
    SignDominanceReason,
    SignOccupantRuntimeData,
    SignRuntimeData,
)


def test_sign_runtime_contract_accepts_complete_shape() -> None:
    """Le contrat expose les faits attendus avec un poids borne."""
    runtime = SignRuntimeData(
        sign="aries",
        occupants=(SignOccupantRuntimeData(planet="sun", longitude=12.0, house=1),),
        weight=0.7,
        dominant=True,
        active_dignities=(),
        reasons=(SignDominanceReason.OCCUPANTS_PRESENT,),
        element="fire",
        modality="cardinal",
        polarity="yang",
        seasonal_quadrant="spring",
        fertility="barren",
        voice="semi_vocal",
        form="bestial",
        synthesis_role="dominant_focus",
    )

    assert runtime.sign == "aries"
    assert runtime.dominant is True
    assert runtime.seasonal_quadrant == "spring"


def test_sign_runtime_contract_rejects_unbounded_weight() -> None:
    """Le poids de signe reste normalise entre zero et un."""
    with pytest.raises(ValueError, match="weight"):
        SignRuntimeData(
            sign="aries",
            occupants=(),
            weight=1.2,
            dominant=False,
            active_dignities=(),
            reasons=(),
            element="fire",
            modality="cardinal",
            polarity="yang",
            seasonal_quadrant="spring",
            fertility="barren",
            voice="semi_vocal",
            form="bestial",
        )


def test_sign_runtime_contract_rejects_missing_profile() -> None:
    """Le contrat refuse un profil de signe incomplet."""
    with pytest.raises(ValueError, match="element"):
        SignRuntimeData(
            sign="aries",
            occupants=(),
            weight=0.0,
            dominant=False,
            active_dignities=(),
            reasons=(),
            element="",
            modality="cardinal",
            polarity="yang",
            seasonal_quadrant="spring",
            fertility="barren",
            voice="semi_vocal",
            form="bestial",
        )
