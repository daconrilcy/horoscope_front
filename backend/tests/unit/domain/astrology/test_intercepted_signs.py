"""Tests de détection des signes interceptés."""

from app.domain.astrology.calculators.intercepted_signs import resolve_intercepted_signs


def test_resolve_intercepted_signs_excludes_neighbor_cusps() -> None:
    """Cancer est intercepté entre une cuspide Gémeaux et une cuspide Lion."""
    assert resolve_intercepted_signs(
        ["gemini", "cancer", "leo"],
        "gemini",
        "leo",
    ) == ["cancer"]


def test_resolve_intercepted_signs_returns_empty_when_only_cusp_signs() -> None:
    """Aucune interception n'existe quand seuls les signes de cuspides sont touchés."""
    assert resolve_intercepted_signs(["aries", "taurus"], "aries", "taurus") == []
