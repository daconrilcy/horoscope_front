"""Tests du contrat natal expose apres adaptation interpretative."""

from __future__ import annotations

from app.domain.astrology.interpretation_adapters.contracts import InterpretationAdapterResult
from app.domain.astrology.natal_calculation import NatalResult


def test_natal_result_exposes_interpretation_adapter_after_dominance() -> None:
    """Le contrat natal expose le resultat d'adaptation sans remplacer les dominantes."""
    fields = list(NatalResult.model_fields)

    assert "dominant_planets" in fields
    assert "interpretation_adapter" in fields
    assert fields.index("interpretation_adapter") > fields.index("dominant_planets")
    assert NatalResult.model_fields["interpretation_adapter"].annotation == (
        InterpretationAdapterResult | None
    )
