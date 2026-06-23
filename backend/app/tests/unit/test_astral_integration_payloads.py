# Commentaire global: couvre les contrats de payload envoyes a Astral.
"""Tests unitaires des payloads metier Astral."""

from __future__ import annotations

import pytest

from app.core.datetime_provider import datetime_provider
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
        "location": {"latitude": 48.8566, "longitude": 2.3522, "label": "Paris, France"},
        "current_location": None,
    }


def _astral_natal_birth_payload() -> dict[str, object]:
    """Retourne la projection de naissance acceptee par les contrats natal."""
    return {
        "date": "1990-06-15",
        "time": "14:30",
        "timezone": "Europe/Paris",
        "location": {"latitude": 48.8566, "longitude": 2.3522, "label": "Paris, France"},
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


def test_build_natal_basic_payload_matches_astral_full_contract() -> None:
    """Construit le payload full avec heure normalisee et projection Basic."""
    payload = AstralIntegrationService._build_service_payload(
        command=AstralJobCommand(
            product="natal_full",
            plan="basic",
            client_request_id="natal-basic-request-1",
        ),
        plan="basic",
        birth_payload=_birth_payload(),
    )

    assert payload == {
        "request_contract_version": "astro_engine_request_v1",
        "request_id": "natal-basic-request-1",
        "idempotency_key": "natal-basic-request-1",
        "calculation": {
            "type": "natal",
            "house_system": "placidus",
            "zodiacal_reference_system": "tropical",
            "coordinate_reference_system": "geocentric",
        },
        "birth": {
            "date": "1990-06-15",
            "time": "14:30:00",
            "timezone": "Europe/Paris",
            "location": {"latitude": 48.8566, "longitude": 2.3522, "label": "Paris, France"},
        },
        "projection": {"level": "compact"},
    }


def test_build_natal_premium_payload_uses_rich_projection() -> None:
    """Aligne le plan Premium sur le niveau de projection riche Astral."""
    payload = AstralIntegrationService._build_service_payload(
        command=AstralJobCommand(
            product="natal_full",
            plan="premium",
            client_request_id="natal-premium-request-1",
        ),
        plan="premium",
        birth_payload=_birth_payload(),
    )

    assert payload["projection"] == {"level": "rich"}


def test_build_natal_full_without_birth_time_degrades_to_simplified_payload() -> None:
    """Dégrade une lecture full sans heure vers le contrat simplifié."""
    birth_payload = {**_birth_payload(), "time": None}

    payload = AstralIntegrationService._build_service_payload(
        command=AstralJobCommand(
            product="natal_full",
            plan="premium",
            client_request_id="natal-no-time-request-1",
        ),
        plan="premium",
        birth_payload=birth_payload,
    )

    assert payload == {
        "request_contract_version": "astro_simplified_natal_request_v1",
        "request_id": "natal-no-time-request-1",
        "birth": {
            "date": "1990-06-15",
            "timezone": "Europe/Paris",
            "location": {"latitude": 48.8566, "longitude": 2.3522, "label": "Paris, France"},
        },
    }


def test_service_code_degrades_full_without_birth_time_to_simplified() -> None:
    """Garantit que le service_code reste coherent avec le payload degrade."""
    birth_payload = {**_birth_payload(), "time": None}

    effective_product = AstralIntegrationService._effective_product(
        product="natal_full",
        plan="basic",
        birth_payload=birth_payload,
    )

    assert effective_product == "natal_simplified"
    assert AstralIntegrationService._service_code(effective_product, "basic") == "natal_simplified"


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
        "date": datetime_provider.today().isoformat(),
        "timezone": "Europe/Paris",
        "target_language": "fr",
        "audience_level": "expert",
        "chart_calculation_id": "chart-123",
    }
