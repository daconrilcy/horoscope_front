"""Tests du calcul des signes contenus dans une maison."""

from app.domain.astrology.calculators.contained_signs import resolve_contained_signs


def test_resolve_contained_signs_includes_three_signs() -> None:
    """Une maison de Gémeaux à Lion contient aussi Cancer."""
    assert resolve_contained_signs(75.0, 142.0) == ["gemini", "cancer", "leo"]


def test_resolve_contained_signs_supports_zodiac_wrap() -> None:
    """Le calcul traverse correctement le passage Poissons vers Bélier."""
    assert resolve_contained_signs(350.0, 40.0) == ["pisces", "aries", "taurus"]


def test_resolve_contained_signs_keeps_single_sign_interval() -> None:
    """Une maison courte dans un même signe ne duplique pas ce signe."""
    assert resolve_contained_signs(12.0, 24.0) == ["aries"]
