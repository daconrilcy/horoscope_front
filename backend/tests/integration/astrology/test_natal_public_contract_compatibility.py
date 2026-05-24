# Tests de compatibilite publique du contrat natal.
"""Verifie que les surfaces runtime internes restent hors API publique."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.domain.astrology.natal_calculation import HouseResult, NatalResult, PlanetPosition
from app.domain.astrology.natal_preparation import BirthPreparedData
from app.main import app

FORBIDDEN_PUBLIC_RUNTIME_TERMS = (
    "chart_objects",
    "ChartObjectRuntimeData",
    "FixedStarConjunctionRuntimePayload",
    "interpretation_input",
    "CalculationGraphExecutionTrace",
    "CalculationGraphManifest",
)


def test_openapi_keeps_natal_runtime_surfaces_internal() -> None:
    """Le schema public ne contient pas les payloads runtime internes."""
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    serialized_openapi = str(response.json())
    assert all(term not in serialized_openapi for term in FORBIDDEN_PUBLIC_RUNTIME_TERMS)


def test_public_natal_calculate_route_is_still_registered() -> None:
    """La route publique de calcul natal reste exposee."""
    route_paths = {route.path for route in app.routes}

    assert "/v1/astrology-engine/natal/calculate" in route_paths


def test_public_natal_calculate_keeps_legacy_projection_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le TestClient prouve la compatibilite publique sans exposer chart_objects."""
    client = TestClient(app)
    prepared = BirthPreparedData(
        birth_datetime_local="1990-06-15T10:30:00+02:00",
        birth_datetime_utc="1990-06-15T08:30:00Z",
        timestamp_utc=645438600,
        julian_day=2448057.8541666665,
        birth_timezone="Europe/Paris",
    )

    def _fake_calculate(*args: object, **kwargs: object) -> NatalResult:
        """Retourne un resultat minimal avec les projections publiques historiques."""
        del args, kwargs
        return NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system="equal",
            engine="simplified",
            prepared_input=prepared,
            planet_positions=[
                PlanetPosition(
                    planet="Soleil",
                    planet_code="sun",
                    longitude=84.0,
                    sign="Gemeaux",
                    sign_code="gemini",
                    degree_in_sign=24.0,
                    house_number=10,
                )
            ],
            houses=[HouseResult(number=1, cusp_longitude=12.0)],
            astral_points=[],
            dignities=[],
            advanced_conditions=[],
            aspects=[],
            chart_objects=[],
        )

    monkeypatch.setattr(
        "app.api.v1.routers.public.astrology_engine.NatalCalculationService.calculate",
        _fake_calculate,
    )
    monkeypatch.setattr(
        "app.api.v1.routers.public.astrology_engine.ChartResultService.persist_trace",
        lambda **kwargs: "chart-cs-224",
    )

    response = client.post(
        "/v1/astrology-engine/natal/calculate",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "reference_version": "1.0.0",
        },
        headers={"x-request-id": "rid-cs-224"},
    )

    assert response.status_code == 200, response.text
    result = response.json()["data"]["result"]
    assert response.json()["meta"]["request_id"] == "rid-cs-224"
    assert "planet_positions" in result
    assert "houses" in result
    assert "astral_points" in result
    assert "dignities" in result
    assert "advanced_conditions" in result
    assert "aspects" in result
    assert "chart_objects" not in result
