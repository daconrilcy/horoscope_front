# Commentaire global: tests de couverture editoriale des support_elements Basic.
"""Verifie la diversite thematique des appuis astrologiques vulgarises."""

from __future__ import annotations

from app.domain.astrology.interpretation.client_interpretation_projection_v1_builder import (
    ClientInterpretationProjectionV1Builder,
)
from tests.unit.domain.astrology.test_client_interpretation_projection_v1_builder import (
    _structured_facts,
)


def test_basic_support_elements_cover_multiple_families() -> None:
    payload = ClientInterpretationProjectionV1Builder().build(
        _structured_facts(),
        requested_plan="basic",
        current_plan="basic",
    )
    support = payload["support_elements"]
    values = " ".join(item["value"] for item in support).casefold()
    assert len(support) == 6
    assert "sun" in values or "position principale" in values
    assert "regence" in values
    assert "theme dominant" in values
    assert "maison" in values
    assert "major" in values
