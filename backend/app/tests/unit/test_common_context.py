"""Unit tests for CommonContextBuilder."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.domain.llm.prompting.context import (
    CommonContextBuilder,
    PromptCommonContext,
    QualifiedContext,
)


def test_qualified_context_compute_quality():
    """Test transitions between full, partial, and minimal quality."""

    # 1. Full Quality
    full_payload = PromptCommonContext(
        today_date="mardi 7 avril 2026",
        use_case_name="test",
        use_case_key="test",
        astrologer_profile={"name": "Luna"},
        natal_interpretation="Some interp",
        natal_data={"planets": []},  # Added
        precision_level="précision complète",
        period_covered="daily",
    )
    ctx_full = QualifiedContext(payload=full_payload, source="daily")
    assert ctx_full.context_quality == "full"
    assert ctx_full.is_degraded() is False

    # 2. Partial (missing interpretation but has raw data)
    partial_payload = PromptCommonContext(
        today_date="mardi 7 avril 2026",
        use_case_name="test",
        use_case_key="test",
        astrologer_profile={"name": "Luna"},
        natal_data={"planets": []},
        precision_level="précision complète",
        period_covered="daily",
    )
    ctx_partial = QualifiedContext(payload=partial_payload, source="daily")
    assert ctx_partial.context_quality == "partial"
    assert "natal_interpretation" in ctx_partial.missing_fields

    # 3. Minimal (missing profile)
    minimal_payload = PromptCommonContext(
        today_date="mardi 7 avril 2026",
        use_case_name="test",
        use_case_key="test",
        natal_interpretation="Some interp",
        astrologer_profile={},  # Missing content
        precision_level="unknown",
        period_covered="daily",
    )
    ctx_minimal = QualifiedContext(payload=minimal_payload, source="daily")
    assert ctx_minimal.context_quality == "minimal"
    assert "astrologer_profile" in ctx_minimal.missing_fields
    assert ctx_minimal.is_degraded() is True


def test_format_date_fr() -> None:
    """Test French date formatting."""
    d = date(2026, 3, 18)
    formatted = CommonContextBuilder._format_date_fr(d)
    assert "mercredi 18 mars 2026" in formatted


@pytest.mark.asyncio
async def test_build_common_context_with_interpretation() -> None:
    """Test build() when a natal interpretation exists."""
    mock_db = MagicMock()
    user_id = 1

    # Mock Persona
    mock_persona = MagicMock()
    mock_persona.model_dump.return_value = {"name": "Astrologue", "description": "Expert"}

    # Mock Profile
    mock_profile = MagicMock()
    mock_profile.birth_date = "1990-01-01"
    mock_profile.birth_time = "12:00"
    mock_profile.birth_place = "Paris"

    # Mock Interpretation in DB
    mock_interp = MagicMock()
    mock_interp.interpretation_payload = {"summary": "Votre thème est harmonieux."}

    with (
        patch(
            "app.services.persona_config_service.PersonaConfigService.get_active",
            return_value=mock_persona,
        ),
        patch(
            "app.services.user_birth_profile_service.UserBirthProfileService.get_for_user",
            return_value=mock_profile,
        ),
        patch("app.domain.llm.prompting.context.select"),
    ):
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_interp
        ctx = CommonContextBuilder.build(user_id, "chat_astrologer", "daily", mock_db)

        assert ctx.payload.natal_interpretation == "Votre thème est harmonieux."
        assert ctx.payload.natal_data is None
        assert ctx.payload.precision_level == "précision complète"
        assert ctx.payload.use_case_name == "chat-astrologer-v1"


@pytest.mark.asyncio
async def test_build_common_context_without_interpretation() -> None:
    """Test build() when no interpretation exists (fallback to raw data)."""
    mock_db = MagicMock()
    user_id = 1

    # Mock Persona & Profile
    mock_persona = MagicMock()
    mock_persona.model_dump.return_value = {"name": "Astrologue"}
    mock_profile = MagicMock()
    mock_profile.birth_time = "00:00"  # Degraded

    # Mock Chart Service
    mock_chart = MagicMock()
    mock_chart.result.model_dump.return_value = {"planets": {"sun": {"sign": "aries"}}}

    with (
        patch(
            "app.services.persona_config_service.PersonaConfigService.get_active",
            return_value=mock_persona,
        ),
        patch(
            "app.services.user_birth_profile_service.UserBirthProfileService.get_for_user",
            return_value=mock_profile,
        ),
        patch(
            "app.services.user_natal_chart_service.UserNatalChartService.get_latest_for_user",
            return_value=mock_chart,
        ),
        patch("app.domain.llm.prompting.context.select"),
    ):
        # No interpretation in DB
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        ctx = CommonContextBuilder.build(user_id, "guidance_daily", "daily", mock_db)

        assert ctx.payload.natal_interpretation is None
        assert ctx.payload.natal_data == {"planets": {"sun": {"sign": "aries"}}}
        assert "heure de naissance manquante" in ctx.payload.precision_level


@pytest.mark.asyncio
async def test_build_common_context_accepts_canonical_horoscope_daily_key() -> None:
    """The daily common context should use the canonical Story 66 key."""
    mock_db = MagicMock()
    user_id = 1

    mock_persona = MagicMock()
    mock_persona.display_name = "Astrologue"
    mock_persona.response_style = "clair"
    mock_persona.tone = "bienveillant"
    mock_persona.prudence_level = "standard"
    mock_persona.to_prompt_line.return_value = "Astrologue - style clair"

    mock_profile = MagicMock()
    mock_profile.birth_time = "12:00"
    mock_profile.birth_place = "Paris"

    mock_interp = MagicMock()
    mock_interp.interpretation_payload = {"summary": "Votre synthèse natale."}

    mock_chart = MagicMock()
    mock_chart.result.model_dump.return_value = {"planets": {"sun": {"sign": "aries"}}}

    with (
        patch(
            "app.services.persona_config_service.PersonaConfigService.get_active",
            return_value=mock_persona,
        ),
        patch(
            "app.services.user_birth_profile_service.UserBirthProfileService.get_for_user",
            return_value=mock_profile,
        ),
        patch(
            "app.services.user_natal_chart_service.UserNatalChartService.get_latest_for_user",
            return_value=mock_chart,
        ),
        patch("app.domain.llm.prompting.context.select"),
    ):
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_interp

        ctx = CommonContextBuilder.build(user_id, "horoscope_daily", "daily", mock_db)

        assert ctx.payload.use_case_key == "horoscope_daily"
        assert ctx.payload.use_case_name == "horoscope-daily-canonical-v1"
        assert ctx.payload.natal_interpretation == "Votre synthèse natale."
        assert ctx.context_quality == "full"
