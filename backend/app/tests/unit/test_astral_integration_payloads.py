# Commentaire global: couvre les contrats de payload envoyes a Astral.
"""Tests unitaires des payloads metier Astral."""

from __future__ import annotations

from datetime import date

import pytest

from app.services.astral.integration_service import (
    AstralIntegrationService,
    AstralIntegrationServiceError,
    AstralJobCommand,
)


def _birth_payload() -> dict[str, object]:
    """Retourne un profil de naissance minimal compatible Astral."""
    return {
        "date": "1990-06-15",
        "time": "14:30",
        "timezone": "Europe/Paris",
        "location": {"latitude": 48.8566, "longitude": 2.3522},
        "current_location": None,
    }


def _astral_natal_birth_payload() -> dict[str, object]:
    """Retourne la projection de naissance acceptee par les contrats natal."""
    return {
        "date": "1990-06-15",
        "time": "14:30",
        "timezone": "Europe/Paris",
        "location": {"latitude": 48.8566, "longitude": 2.3522},
    }


def test_build_natal_simplified_payload_matches_astral_contract() -> None:
    """Construit le payload natal simplifie sans contexte backend imbrique."""
    payload = AstralIntegrationService._build_service_payload(
        command=AstralJobCommand(
            product="natal_simplified",
            plan="free",
            client_request_id="natal-request-1",
        ),
        plan="free",
        birth_payload=_birth_payload(),
    )

    assert payload == {
        "request_contract_version": "astro_simplified_natal_request_v1",
        "request_id": "natal-request-1",
        "birth": _astral_natal_birth_payload(),
    }
    assert "context" not in payload


def test_build_horoscope_payload_requires_chart_calculation_id() -> None:
    """Bloque localement les horoscopes sans theme Astral deja calcule."""
    with pytest.raises(AstralIntegrationServiceError) as exc_info:
        AstralIntegrationService._build_service_payload(
            command=AstralJobCommand(
                product="horoscope_daily",
                plan="free",
                client_request_id="daily-request-1",
            ),
            plan="free",
            birth_payload=_birth_payload(),
        )

    assert exc_info.value.code == "astral_chart_calculation_required"


def test_build_horoscope_payload_matches_astral_contract() -> None:
    """Construit le payload horoscope plat attendu par Astral."""
    payload = AstralIntegrationService._build_service_payload(
        command=AstralJobCommand(
            product="horoscope_daily",
            plan="premium",
            chart_calculation_id="chart-123",
            client_request_id="daily-request-1",
            audience_level="advanced",
        ),
        plan="premium",
        birth_payload=_birth_payload(),
    )

    assert payload == {
        "date": date.today().isoformat(),
        "timezone": "Europe/Paris",
        "target_language": "fr",
        "audience_level": "expert",
        "chart_calculation_id": "chart-123",
    }
