"""Unit tests for AstroContextBuilder."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.services.natal.astro_context_builder import AstroContextBuilder, AstroContextData
from app.services.user_profile.birth_profile_service import UserBirthProfileData


def test_get_lunar_phase_label() -> None:
    """Test human-readable lunar phase label generation."""
    # Mock calculate_planets to return Sun at 0 and Moon at 180 (Full Moon)
    with patch("app.domain.astrology.ephemeris_provider.calculate_planets") as mock_calc:
        sun = MagicMock(planet_id="sun", longitude=0.0)
        moon = MagicMock(planet_id="moon", longitude=180.0)
        mock_calc.return_value = MagicMock(planets=[sun, moon])

        label = AstroContextBuilder._get_lunar_phase_label(2451545.0)
        assert "Pleine Lune" in label
        assert "100%" in label


@pytest.mark.asyncio
async def test_build_daily_success() -> None:
    """Test build_daily returns AstroContextData."""
    mock_db = MagicMock()
    user_id = 1
    target_date = date(2026, 3, 18)

    # Mock UserBirthProfileService
    profile = UserBirthProfileData(
        birth_date="1990-01-01",
        birth_time="12:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )

    # Mock DailyPredictionService
    mock_run = MagicMock()
    mock_contributor = {
        "body": "jupiter",
        "target": "sun",
        "aspect": "trine",
        "orb_deg": 1.2,
        "phase": "applying",
    }
    mock_score = MagicMock(contributors=[mock_contributor])
    mock_run.category_scores = [mock_score]

    with (
        patch(
            "app.services.user_profile.birth_profile_service.UserBirthProfileService.get_for_user",
            return_value=profile,
        ),
        patch(
            "app.services.prediction.DailyPredictionService.get_or_compute"
        ) as mock_compute,
        patch(
            "app.services.natal.astro_context_builder.AstroContextBuilder._get_lunar_phase_label",
            return_value="Mock Phase",
        ),
    ):
        mock_compute.return_value = MagicMock(run=mock_run)

        result = AstroContextBuilder.build_daily(user_id, target_date, "Europe/Paris", mock_db)

        assert result is not None
        assert isinstance(result, AstroContextData)
        assert result.precision_level == "full"
        assert len(result.transits_active) == 1
        assert result.transits_active[0].planet == "Jupiter"
        assert result.lunar_phase == "Mock Phase"


@pytest.mark.asyncio
async def test_build_daily_degraded_mode() -> None:
    """Test build_daily returns precision_level='degraded' when birth_time is missing."""
    mock_db = MagicMock()
    profile = UserBirthProfileData(
        birth_date="1990-01-01",
        birth_time="00:00",  # Degraded
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )

    with (
        patch(
            "app.services.user_profile.birth_profile_service.UserBirthProfileService.get_for_user",
            return_value=profile,
        ),
        patch(
            "app.services.prediction.DailyPredictionService.get_or_compute",
            return_value=MagicMock(run=MagicMock()),
        ),
        patch(
            "app.services.natal.astro_context_builder.AstroContextBuilder._get_lunar_phase_label",
            return_value="Mock Phase",
        ),
    ):
        result = AstroContextBuilder.build_daily(1, date(2026, 3, 18), "Europe/Paris", mock_db)
        assert result.precision_level == "degraded"
