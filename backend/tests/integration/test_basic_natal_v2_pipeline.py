# Commentaire global: garde d'extinction du pipeline Basic natal V2 legacy.
"""Verifie que l'ancien service natal ne regenere plus les lectures Basic V2."""

from __future__ import annotations

import pytest

from app.services.llm_generation.natal.interpretation_service import (
    NatalInterpretationService,
    NatalInterpretationServiceError,
)
from app.tests.helpers.natal_result_factory import make_natal_result
from tests.integration.basic_natal_v2_helpers import basic_birth_profile


@pytest.mark.asyncio
async def test_basic_complete_legacy_pipeline_is_rejected_before_provider(db) -> None:
    """Prouve que la generation Basic historique renvoie vers le runtime theme_natal."""
    with pytest.raises(NatalInterpretationServiceError) as exc_info:
        await NatalInterpretationService.interpret(
            db=db,
            user_id=418,
            chart_id="chart-basic-v2",
            natal_result=make_natal_result(),
            birth_profile=basic_birth_profile(),
            level="complete",
            persona_id=None,
            locale="fr-FR",
            question=None,
            request_id="req-basic-v2",
            trace_id="trace-basic-v2",
            force_refresh=True,
            variant_code="single_astrologer",
        )

    assert exc_info.value.code == "legacy_natal_generation_disabled"
    assert exc_info.value.details["replacement"] == "/v1/theme-natal/readings"
