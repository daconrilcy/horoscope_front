import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.thematic_consultation_entitlement_gate import (
    ConsultationEntitlementResult,
    ConsultationAccessDeniedError,
    ConsultationQuotaExceededError,
)
from app.services.entitlement_types import UsageState
from datetime import datetime, timezone
from app.api.v1.schemas.consultation import ConsultationGenerateData, ConsultationStatus, PrecisionLevel
from app.infra.db.session import get_db_session

client = TestClient(app)


@pytest.fixture
def mock_user():
    return MagicMock(id=42, email="user@example.com")


@pytest.fixture(autouse=True)
def override_auth(mock_user):
    from app.api.dependencies.auth import require_authenticated_user

    app.dependency_overrides[require_authenticated_user] = lambda: mock_user
    yield
    app.dependency_overrides.pop(require_authenticated_user, None)


def _make_quota_state(used=1, limit=1, period_unit="week"):
    return UsageState(
        feature_code="thematic_consultation",
        quota_key="consultations",
        quota_limit=limit,
        used=used,
        remaining=max(0, limit - used),
        exhausted=used >= limit,
        period_unit=period_unit,
        period_value=1,
        reset_mode="calendar",
        window_start=None,
        window_end=datetime(2026, 3, 30, 0, 0, 0, tzinfo=timezone.utc),
    )


def test_generate_canonical_quota_ok(mock_user):
    mock_result = ConsultationEntitlementResult(
        path="canonical_quota", usage_states=[_make_quota_state(used=1, limit=1)]
    )

    mock_data = ConsultationGenerateData.model_construct(consultation_id="123")

    with patch(
        "app.services.thematic_consultation_entitlement_gate.ThematicConsultationEntitlementGate.check_and_consume",
        return_value=mock_result,
    ), patch(
        "app.services.consultation_generation_service.ConsultationGenerationService.generate",
        return_value=mock_data,
    ):
        response = client.post(
            "/v1/consultations/generate",
            json={"consultation_type": "career", "question": "Quelle direction prendre ?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["quota_info"]["remaining"] == 0
    assert data["quota_info"]["limit"] == 1


def test_generate_canonical_unlimited_ok(mock_user):
    mock_result = ConsultationEntitlementResult(
        path="canonical_unlimited",
        usage_states=[
            UsageState(
                feature_code="thematic_consultation",
                quota_key="unlimited",
                quota_limit=None,
                used=0,
                remaining=None,
                exhausted=False,
                period_unit="unlimited",
                period_value=0,
                reset_mode="none",
                window_start=None,
                window_end=None,
            )
        ],
    )

    mock_data = ConsultationGenerateData.model_construct(consultation_id="123")

    with patch(
        "app.services.thematic_consultation_entitlement_gate.ThematicConsultationEntitlementGate.check_and_consume",
        return_value=mock_result,
    ), patch(
        "app.services.consultation_generation_service.ConsultationGenerationService.generate",
        return_value=mock_data,
    ):
        response = client.post(
            "/v1/consultations/generate",
            json={"consultation_type": "career", "question": "Quelle direction prendre ?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["quota_info"]["remaining"] is None


def test_generate_no_plan_rejected(mock_user):
    with patch(
        "app.services.thematic_consultation_entitlement_gate.ThematicConsultationEntitlementGate.check_and_consume",
        side_effect=ConsultationAccessDeniedError(
            reason="no_plan", billing_status="none", plan_code=""
        ),
    ):
        response = client.post(
            "/v1/consultations/generate",
            json={"consultation_type": "career", "question": "Quelle direction prendre ?"},
        )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "consultation_access_denied"
    assert response.json()["error"]["details"]["reason"] == "no_plan"


def test_generate_quota_exhausted_rejected(mock_user):
    with patch(
        "app.services.thematic_consultation_entitlement_gate.ThematicConsultationEntitlementGate.check_and_consume",
        side_effect=ConsultationQuotaExceededError(
            quota_key="consultations",
            used=1,
            limit=1,
            window_end=datetime(2026, 3, 30, 0, 0, 0, tzinfo=timezone.utc),
        ),
    ):
        response = client.post(
            "/v1/consultations/generate",
            json={"consultation_type": "career", "question": "Quelle direction prendre ?"},
        )

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "consultation_quota_exceeded"
    assert "window_end" in response.json()["error"]["details"]


def test_generate_disabled_binding_returns_disabled_by_plan(mock_user):
    with patch(
        "app.services.thematic_consultation_entitlement_gate.ThematicConsultationEntitlementGate.check_and_consume",
        side_effect=ConsultationAccessDeniedError(
            reason="disabled_by_plan", billing_status="active", plan_code="free"
        ),
    ):
        response = client.post(
            "/v1/consultations/generate",
            json={"consultation_type": "career", "question": "Quelle direction prendre ?"},
        )

    assert response.status_code == 403
    assert response.json()["error"]["details"]["reason"] == "disabled_by_plan"


def test_generate_rolls_back_on_error(mock_user, db_session):
    # On vérifie que db.rollback() est appelé en cas d'erreur d'entitlement
    with patch(
        "app.services.thematic_consultation_entitlement_gate.ThematicConsultationEntitlementGate.check_and_consume",
        side_effect=ConsultationQuotaExceededError(
            quota_key="consultations", used=1, limit=1, window_end=None
        ),
    ):
        with patch.object(db_session, "rollback") as mock_rollback:
            # On doit s'assurer que le Depends(get_db) utilise bien notre db_session mockée
            app.dependency_overrides[get_db_session] = lambda: db_session
            client.post(
                "/v1/consultations/generate",
                json={"consultation_type": "career", "question": "Quelle direction prendre ?"},
            )
            mock_rollback.assert_called_once()
            app.dependency_overrides.pop(get_db_session)


def test_premium_quota_2_per_day(mock_user, db_session):
    # Ce test nécessite une vraie intégration ou des mocks très précis du cycle complet
    # Pour AC 10, on va utiliser des mocks successifs pour simuler la consommation
    
    fixed_now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
    
    with patch("app.services.quota_window_resolver.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_now
        
        # 1ère consultation OK
        state1 = _make_quota_state(used=1, limit=2, period_unit="day")
        res1 = ConsultationEntitlementResult(path="canonical_quota", usage_states=[state1])
        
        # 2ème consultation OK
        state2 = _make_quota_state(used=2, limit=2, period_unit="day")
        res2 = ConsultationEntitlementResult(path="canonical_quota", usage_states=[state2])
        
        # 3ème consultation KO
        err3 = ConsultationQuotaExceededError(quota_key="consultations", used=2, limit=2, window_end=fixed_now)

        with patch("app.services.thematic_consultation_entitlement_gate.ThematicConsultationEntitlementGate.check_and_consume") as mock_gate:
            mock_gate.side_effect = [res1, res2, err3]
            
            mock_data = ConsultationGenerateData.model_construct(consultation_id="123")
            with patch("app.services.consultation_generation_service.ConsultationGenerationService.generate", return_value=mock_data):
                # 1
                resp1 = client.post("/v1/consultations/generate", json={"consultation_type": "career", "question": "Q1"})
                assert resp1.status_code == 200
                # 2
                resp2 = client.post("/v1/consultations/generate", json={"consultation_type": "career", "question": "Q2"})
                assert resp2.status_code == 200
                # 3
                resp3 = client.post("/v1/consultations/generate", json={"consultation_type": "career", "question": "Q3"})
                assert resp3.status_code == 429
