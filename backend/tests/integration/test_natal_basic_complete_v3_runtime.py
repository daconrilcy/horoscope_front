# Commentaire global: garde runtime de la generation natale Basic complete legacy.
"""Verifie que l'ancien runtime Basic complete est eteint cote service public."""

from __future__ import annotations

import pytest

from app.main import app
from app.services.llm_generation.natal.interpretation_service import (
    NatalInterpretationService,
    NatalInterpretationServiceError,
)
from app.services.user_profile.birth_profile_service import UserBirthProfileData
from app.tests.helpers.natal_result_factory import make_natal_result


def _birth_profile() -> UserBirthProfileData:
    """Construit un profil de naissance complet pour le rejet controle."""
    return UserBirthProfileData(
        birth_date="1990-06-15",
        birth_time="12:30",
        birth_place="Paris, France",
        birth_lat=48.8566,
        birth_lon=2.3522,
        birth_timezone="Europe/Paris",
    )


@pytest.mark.asyncio
async def test_basic_complete_legacy_runtime_is_rejected_before_provider(db) -> None:
    """Prouve que Basic complete ne passe plus par l'ancien service natal."""
    with pytest.raises(NatalInterpretationServiceError) as exc_info:
        await NatalInterpretationService.interpret(
            db=db,
            user_id=408,
            chart_id="chart-basic-v3",
            natal_result=make_natal_result(),
            birth_profile=_birth_profile(),
            level="complete",
            persona_id=None,
            locale="fr-FR",
            question=None,
            request_id="req-basic-v3",
            trace_id="trace-basic-v3",
            force_refresh=True,
            variant_code="single_astrologer",
        )

    assert exc_info.value.code == "legacy_natal_generation_disabled"
    assert exc_info.value.details["replacement"] == "/v1/theme-natal/readings"


def test_public_natal_routes_and_openapi_remain_loadable() -> None:
    """Verifie la suppression runtime et OpenAPI de l'ancien POST public."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    openapi = app.openapi()

    assert "/v1/theme-natal/readings" in route_paths
    assert "/v1/natal/interpretation" not in route_paths
    assert all(not path.startswith("/v1/natal/interpretations") for path in route_paths)
    assert "paths" in openapi
    assert "/v1/theme-natal/readings" in openapi["paths"]
    assert "/v1/natal/interpretation" not in openapi["paths"]
    assert all(not path.startswith("/v1/natal/interpretations") for path in openapi["paths"])
