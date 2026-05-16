"""Tests des utilitaires zodiacaux adossés au catalogue canonique."""

import pytest

from app.domain.astrology.zodiac import ordered_sign_codes, sign_from_longitude


def test_sign_from_longitude_uses_injected_reference_order() -> None:
    """Le calcul de signe peut consommer l'ordre fourni par le référentiel DB."""
    sign_codes = tuple(f"sign_{index}" for index in range(12))

    assert sign_from_longitude(0.0, sign_codes) == "sign_0"
    assert sign_from_longitude(359.9, sign_codes) == "sign_11"


def test_ordered_sign_codes_rejects_invalid_reference_order() -> None:
    """Un catalogue de signes incomplet est bloqué avant les calculs."""
    with pytest.raises(ValueError, match="12 unique codes"):
        ordered_sign_codes(("aries", "taurus"))
