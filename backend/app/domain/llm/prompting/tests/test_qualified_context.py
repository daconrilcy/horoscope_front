from unittest.mock import MagicMock, patch

import pytest

from app.domain.llm.prompting.context import (
    CommonContextBuilder,
    PromptCommonContext,
    QualifiedContext,
)


def test_qualified_context_quality_rules():
    # Full
    assert QualifiedContext.compute_quality([]) == "full"

    # Partial (secondary field missing)
    assert QualifiedContext.compute_quality(["period_covered"]) == "partial"

    # Partial (one natal missing)
    assert QualifiedContext.compute_quality(["natal_interpretation"]) == "partial"

    # Partial (persona missing)
    assert QualifiedContext.compute_quality(["astrologer_profile"]) == "partial"

    # Minimal (two natal missing)
    assert QualifiedContext.compute_quality(["natal_interpretation", "natal_data"]) == "minimal"

    # Minimal (persona AND one natal missing)
    assert QualifiedContext.compute_quality(["astrologer_profile", "natal_data"]) == "minimal"


def test_is_degraded():
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
async def test_build_full_context(db):
    # Mock dependencies to avoid DB lookup issues in this test
    with (
        patch(
            "app.services.user_birth_profile_service.UserBirthProfileService.get_for_user"
        ) as mock_profile,
        patch(
            "app.services.persona_config_service.PersonaConfigService.get_active"
        ) as mock_persona,
        patch(
            "app.services.user_natal_chart_service.UserNatalChartService.get_latest_for_user"
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

        # Ensure model_dump returns a real dict
        mock_chart.return_value.result.model_dump.return_value = {"planets": []}

        # Test 1: Full
        res = CommonContextBuilder.build(
            user_id=1, use_case_key="natal_interpretation", period="daily", db=db
        )
        assert res.context_quality == "full"
        assert res.source == "db"

        # Test 2: Partial (natal_interpretation missing for non-natal use case)
        res = CommonContextBuilder.build(user_id=1, use_case_key="chat", period="daily", db=db)
        assert res.context_quality == "partial"
        assert "natal_interpretation" in res.missing_fields

        # Test 3: Minimal (natal data fetch fails)
        mock_chart.side_effect = Exception("No chart")
        res = CommonContextBuilder.build(user_id=1, use_case_key="chat", period="daily", db=db)
        assert res.context_quality == "minimal"
        assert "natal_data" in res.missing_fields
        assert "natal_interpretation" in res.missing_fields
        assert res.source == "fallback"
