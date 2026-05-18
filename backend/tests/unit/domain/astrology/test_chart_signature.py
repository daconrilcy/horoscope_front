"""Tests du calcul canonique de signature du theme natal."""

from app.domain.astrology.interpretation.chart_signature import ChartSignatureCalculator
from app.domain.astrology.interpretation.house_strength_contracts import HouseStrengthReason
from app.domain.astrology.runtime.house_runtime_data import (
    HouseRuntimeData,
    HouseStrengthRuntimeData,
)
from app.domain.astrology.runtime.sign_runtime_data import (
    SignDominanceReason,
    SignOccupantRuntimeData,
    SignRuntimeData,
)


def test_chart_signature_ranks_signs_planets_houses_and_profiles() -> None:
    """Le calculateur classe les dominances avec tie-break stable."""
    balance = ChartSignatureCalculator().calculate(
        signs=[
            SignRuntimeData(
                sign="aries",
                occupants=(
                    SignOccupantRuntimeData(planet="sun", longitude=12.0, house=1),
                    SignOccupantRuntimeData(planet="mars", longitude=18.0, house=1),
                ),
                weight=0.8,
                dominant=True,
                active_dignities=(),
                reasons=(SignDominanceReason.OCCUPANTS_PRESENT,),
                element="fire",
                modality="cardinal",
                polarity="yang",
            ),
            SignRuntimeData(
                sign="taurus",
                occupants=(SignOccupantRuntimeData(planet="moon", longitude=40.0, house=2),),
                weight=0.4,
                dominant=False,
                active_dignities=(),
                reasons=(),
                element="earth",
                modality="fixed",
                polarity="yin",
            ),
        ],
        houses=[
            HouseRuntimeData(
                number=1,
                cusp_longitude=0.0,
                strength=HouseStrengthRuntimeData.from_parts(
                    normalized_score=0.7,
                    reasons=(HouseStrengthReason.BASELINE_HOUSE,),
                ),
            ),
            HouseRuntimeData(
                number=2,
                cusp_longitude=30.0,
                strength=HouseStrengthRuntimeData.from_parts(
                    normalized_score=0.3,
                    reasons=(HouseStrengthReason.BASELINE_HOUSE,),
                ),
            ),
        ],
        aspects=[],
    )

    assert balance.elements[0].code == "fire"
    assert balance.modalities[0].code == "cardinal"
    assert balance.dominant_signs[0].code == "aries"
    assert balance.dominant_planets[0].code == "mars"
    assert balance.dominant_houses[0].code == "1"
    assert balance.synthesis.primary_house == 1
