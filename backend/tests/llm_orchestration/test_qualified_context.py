"""Vérifie le contexte qualifié LLM depuis la racine de tests orchestration."""

from unittest.mock import MagicMock, patch

import pytest

from app.domain.llm.prompting.context import (
    CommonContextBuilder,
    PromptCommonContext,
    QualifiedContext,
)


def test_qualified_context_quality_rules() -> None:
    """Verifie les transitions full, partial et minimal du contexte qualifie."""
    assert QualifiedContext.compute_quality([]) == "full"
    assert QualifiedContext.compute_quality(["period_covered"]) == "partial"
    assert QualifiedContext.compute_quality(["natal_interpretation"]) == "partial"
    assert QualifiedContext.compute_quality(["astrologer_profile"]) == "partial"
    assert QualifiedContext.compute_quality(["natal_interpretation", "natal_data"]) == "minimal"
    assert QualifiedContext.compute_quality(["astrologer_profile", "natal_data"]) == "minimal"


def test_is_degraded() -> None:
    """Verifie le predicat de degradation expose par le contexte qualifie."""
    ctx = QualifiedContext(
        payload=PromptCommonContext(
            precision_level="p",
            astrologer_profile={},
            period_covered="p",
            today_date="d",
            use_case_name="n",
            use_case_key="k",
        ),
        source="db",
        context_quality="partial",
    )
    assert ctx.is_degraded() is True

    ctx.context_quality = "full"
    assert ctx.is_degraded() is False


@pytest.mark.asyncio
async def test_build_full_context(db) -> None:
    """Construit un contexte complet puis degrade sans changer les assertions metier."""
    with (
        patch(
            "app.services.user_profile.birth_profile_service.UserBirthProfileService.get_for_user"
        ) as mock_profile,
        patch(
            "app.services.llm_generation.guidance.persona_config_service."
            "PersonaConfigService.get_active"
        ) as mock_persona,
        patch(
            "app.services.user_profile.natal_chart_service."
            "UserNatalChartService.get_latest_for_user"
        ) as mock_chart,
    ):
        mock_profile.return_value = MagicMock(birth_time="12:00", birth_place="Paris")
        mock_persona.return_value = MagicMock(
            display_name="A",
            response_style="S",
            tone="T",
            prudence_level="L",
            to_prompt_line=lambda: "desc",
        )
        mock_chart.return_value.result.model_dump.return_value = {"planets": []}

        res = CommonContextBuilder.build(
            user_id=1, use_case_key="natal_interpretation", period="daily", db=db
        )
        assert res.context_quality == "full"
        assert res.source == "db"

        res = CommonContextBuilder.build(user_id=1, use_case_key="chat", period="daily", db=db)
        assert res.context_quality == "partial"
        assert "natal_interpretation" in res.missing_fields

        mock_chart.side_effect = Exception("No chart")
        res = CommonContextBuilder.build(user_id=1, use_case_key="chat", period="daily", db=db)
        assert res.context_quality == "minimal"
        assert "natal_data" in res.missing_fields
        assert "natal_interpretation" in res.missing_fields
        assert res.source == "fallback"
