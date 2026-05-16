"""Tests des contrats de balance et signature du theme natal."""

import pytest

from app.domain.astrology.runtime.chart_signature_runtime_data import (
    BalanceScoreRuntimeData,
    ChartBalanceRuntimeData,
    ChartSignatureRuntimeData,
)


def test_chart_balance_contract_accepts_complete_shape() -> None:
    """Le contrat de balance expose les familles attendues."""
    balance = ChartBalanceRuntimeData(
        elements=(BalanceScoreRuntimeData(code="fire", score=1.0, rank=1),),
        modalities=(),
        dominant_signs=(),
        dominant_planets=(),
        dominant_houses=(),
        dominant_aspects=(),
        synthesis=ChartSignatureRuntimeData(
            primary_element="fire",
            primary_modality=None,
            primary_sign=None,
            primary_planet=None,
            primary_house=None,
        ),
    )

    assert balance.version == "1"
    assert balance.elements[0].code == "fire"


def test_balance_score_rejects_invalid_rank() -> None:
    """Un rang de balance doit etre strictement positif."""
    with pytest.raises(ValueError, match="rank"):
        BalanceScoreRuntimeData(code="fire", score=1.0, rank=0)
