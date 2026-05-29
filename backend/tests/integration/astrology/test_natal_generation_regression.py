"""Non-regression du flux public de generation et rechargement natal."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_authenticated_user
from app.core.auth_context import AuthenticatedUser
from app.domain.llm.configuration.theme_astral_contracts import THEME_ASTRAL_INPUT_CONTRACT_ID
from app.domain.llm.runtime.gateway import LLMGateway
from app.domain.llm.runtime.theme_astral_provider_payload_builder import (
    ThemeAstralProviderPayloadBuilder,
)
from app.infra.db.session import get_db_session
from app.main import app
from tests.unit.domain.astrology.interpretation.test_interpretation_material_builder import (
    _build_chart_input,
    _sources_for,
)


class _DumpableNatalChart:
    """Expose un payload route-compatible sans dependance DB ni calcul ephemeride."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def model_dump(self, *, mode: str = "python") -> dict[str, Any]:
        """Retourne la forme publique attendue par le routeur FastAPI."""
        del mode
        return self._payload


class _CommitRollbackOnlySession:
    """Session minimale prouvant les commits/rollbacks appeles par le routeur."""

    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        """Compteur de commit pour le flux nominal."""
        self.commits += 1

    def rollback(self) -> None:
        """Compteur de rollback pour les branches d'erreur non exercees ici."""
        self.rollbacks += 1


class _DumpableAstroProfile:
    """Expose un bloc astro_profile route-compatible pour isoler le latest."""

    def model_dump(self) -> dict[str, Any]:
        """Retourne la projection minimale attendue par la reponse publique."""
        return {
            "sun_sign": "Taurus",
            "sun_sign_code": "taurus",
            "ascendant_sign": "Leo",
            "ascendant_sign_code": "leo",
            "missing_birth_time": False,
        }


@pytest.fixture(autouse=True)
def _reset_dependency_overrides() -> None:
    """Isole les overrides FastAPI du test d'integration route."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_post_and_latest_natal_chart_keep_public_contract_and_runtime_inventory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le TestClient prouve le POST, le latest et l'inventaire runtime des routes."""
    db = _CommitRollbackOnlySession()
    captured_generate: dict[str, Any] = {}
    public_payload = _public_natal_chart_payload()
    client = TestClient(app)

    app.dependency_overrides[require_authenticated_user] = _authenticated_user
    app.dependency_overrides[get_db_session] = lambda: db

    def _generate_for_user(**kwargs: Any) -> _DumpableNatalChart:
        captured_generate.update(kwargs)
        return _DumpableNatalChart(public_payload)

    def _latest_for_user(**kwargs: Any) -> _DumpableNatalChart:
        assert kwargs["user_id"] == 381
        latest_payload = {
            **public_payload,
            "created_at": "2026-05-29T10:00:00Z",
            "interpretation": None,
            "astro_profile": None,
        }
        return _DumpableNatalChart(latest_payload)

    monkeypatch.setattr(
        "app.api.v1.routers.public.users.UserNatalChartService.generate_for_user",
        _generate_for_user,
    )
    monkeypatch.setattr(
        "app.api.v1.routers.public.users.UserNatalChartService.get_latest_for_user",
        _latest_for_user,
    )
    monkeypatch.setattr(
        "app.api.v1.routers.public.users.UserAstroProfileService.get_for_user",
        lambda *_args, **_kwargs: _DumpableAstroProfile(),
    )

    post_response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": "Bearer route-overridden"},
        json={"reference_version": "1.0.0", "accurate": True, "house_system": "placidus"},
    )
    latest_response = client.get(
        "/v1/users/me/natal-chart/latest",
        headers={"Authorization": "Bearer route-overridden"},
    )

    assert post_response.status_code == 200, post_response.text
    assert latest_response.status_code == 200, latest_response.text
    assert captured_generate == {
        "db": db,
        "user_id": 381,
        "reference_version": "1.0.0",
        "accurate": True,
        "zodiac": None,
        "ayanamsa": None,
        "frame": None,
        "house_system": "placidus",
        "altitude_m": None,
    }
    assert db.commits == 1

    generated = post_response.json()["data"]
    latest = latest_response.json()["data"]
    assert generated["chart_id"] == "chart-cs-381-paris-1973"
    assert latest["chart_id"] == generated["chart_id"]
    assert latest["astro_profile"]["sun_sign_code"] == "taurus"
    _assert_known_time_traditional_contract(generated["result"])
    _assert_known_time_traditional_contract(latest["result"])
    _assert_provider_payload_coexists_with_public_contract(generated)

    route_paths = {getattr(route, "path", "") for route in app.routes}
    assert "/v1/users/me/natal-chart" in route_paths
    assert "/v1/users/me/natal-chart/latest" in route_paths
    openapi_paths = app.openapi()["paths"]
    assert "/v1/users/me/natal-chart" in openapi_paths
    assert "/v1/users/me/natal-chart/latest" in openapi_paths


def _authenticated_user() -> AuthenticatedUser:
    """Retourne l'utilisateur de test du flux public natal."""
    return AuthenticatedUser(
        id=381,
        role="user",
        email="cs381@example.test",
        created_at=datetime(2026, 5, 29, tzinfo=UTC),
    )


def _public_natal_chart_payload() -> dict[str, Any]:
    """Construit le payload public connu 1973-04-24 11:00 Paris."""
    return {
        "chart_id": "chart-cs-381-paris-1973",
        "metadata": {
            "reference_version": "1.0.0",
            "ruleset_version": "1.0.0",
            "house_system": "placidus",
            "engine": "simplified",
            "zodiac": "tropical",
            "frame": "geocentric",
            "ayanamsa": None,
            "aspect_school": "traditional",
            "altitude_m": None,
            "timezone_used": "Europe/Paris",
            "jd_ut": 2441806.875,
            "jd_tt": 2441806.875,
            "place_resolved_id": 19730424,
            "ephemeris_path_version": "test-v1",
            "ephemeris_path_hash": "hash-cs-381",
        },
        "result": {
            "reference_version": "1.0.0",
            "ruleset_version": "1.0.0",
            "prepared_input": {
                "birth_datetime_local": "1973-04-24T11:00:00",
                "birth_datetime_utc": "1973-04-24T09:00:00Z",
                "timestamp_utc": 104230800,
                "julian_day": 2441806.875,
                "birth_timezone": "Europe/Paris",
                "timezone_used": "Europe/Paris",
                "jd_ut": 2441806.875,
                "jd_tt": 2441806.875,
                "place_resolved_id": 19730424,
            },
            "planet_positions": [{"planet_code": "sun", "sign_code": "taurus"}],
            "houses": [{"number": 1, "cusp_longitude": 120.0}],
            "aspects": [{"aspect_type": "trine", "planet_a": "sun", "planet_b": "moon"}],
            "traditional_conditions": {
                "sun": {
                    "planet_code": "sun",
                    "hayz": {
                        "planet_code": "sun",
                        "is_hayz": True,
                        "sect_match": True,
                        "hemisphere_match": True,
                        "sign_gender_match": True,
                        "chart_sect": "day",
                        "intrinsic_sect": "diurnal",
                        "planet_sect_condition": "in_sect",
                        "planet_horizon_position": "above_horizon",
                        "sign_gender": "feminine",
                        "calculation_basis": "sect_hemisphere_sign_gender",
                        "reference_system": "traditional",
                        "evidence": ["known-time Paris fixture"],
                    },
                    "rejoicing": {
                        "planet_code": "sun",
                        "is_rejoicing": False,
                        "current_house": 10,
                        "rejoicing_house": None,
                        "calculation_basis": "planetary_joy_house",
                        "reference_system": "traditional",
                        "evidence": [],
                    },
                }
            },
        },
    }


def _assert_known_time_traditional_contract(result: dict[str, Any]) -> None:
    """Valide la separation du payload public exploitable pour heure connue."""
    assert result["prepared_input"]["birth_datetime_local"] == "1973-04-24T11:00:00"
    assert result["prepared_input"]["birth_timezone"] == "Europe/Paris"
    assert "chart_json" not in result
    assert "natal_data" not in result
    conditions = result["traditional_conditions"]
    assert isinstance(conditions, dict)
    assert "planets" not in conditions
    assert conditions["sun"]["hayz"]["is_hayz"] is True
    assert conditions["sun"]["rejoicing"]["is_rejoicing"] is False


def _assert_provider_payload_coexists_with_public_contract(public_chart: dict[str, Any]) -> None:
    """Prouve que le payload provider enrichi reste distinct du payload public genere."""
    chart_input = _build_chart_input(aspect_codes=("trine", "square", "opposition"))
    provider_payload = ThemeAstralProviderPayloadBuilder().build(
        chart_input=chart_input,
        interpretation_sources=_sources_for(chart_input),
        commercial_plan="premium",
        astrologer_voice={"tone": "sobre"},
    )

    rendered = LLMGateway().build_user_payload(
        use_case="theme_astral",
        user_input={"locale": "fr-FR"},
        context={THEME_ASTRAL_INPUT_CONTRACT_ID: provider_payload},
        policy="none",
        locale="fr-FR",
    )

    prefix = f"{THEME_ASTRAL_INPUT_CONTRACT_ID}: "
    rendered_provider_payload = json.loads(rendered.removeprefix(prefix))
    birth_context = rendered_provider_payload["input_data"]["birth_context"]
    public_input = public_chart["result"]["prepared_input"]

    assert rendered.startswith(prefix)
    assert public_input["birth_datetime_local"].startswith(birth_context["birth_date"])
    assert birth_context["birth_time_local"] == "11:00"
    assert birth_context["birth_place"]["city"] == "Paris"
    assert birth_context["birth_place"]["timezone"] == public_input["birth_timezone"]
    assert rendered_provider_payload["input_data"]["selected_themes"]["section_keys"]
    assert rendered_provider_payload["input_data"]["interpretation_material"]
    assert not rendered_provider_payload["input_data"]["limits"]["missing_data"]["birth_context"]
    assert "traditional_conditions" not in rendered_provider_payload["input_data"]
    assert "chart_json" not in rendered
    assert "natal_data" not in rendered
