import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementResult,
    NatalChartLongAccessDeniedError,
    NatalChartLongQuotaExceededError,
)
from app.services.entitlement_types import UsageState

from datetime import datetime, timezone
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user

client = TestClient(app)

COMPLETE_PAYLOAD = {"use_case_level": "complete", "locale": "fr-FR"}
SHORT_PAYLOAD = {"use_case_level": "short", "locale": "fr-FR"}


def _override_auth() -> AuthenticatedUser:
    return AuthenticatedUser(
        id=42,
        role="user",
        email="test-user@example.com",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _make_usage_state(used=1, limit=1, remaining=0):
    return UsageState(
        feature_code="natal_chart_long",
        quota_key="interpretations",
        quota_limit=limit,
        used=used,
        remaining=remaining,
        exhausted=used >= limit,
        period_unit="lifetime",
        period_value=1,
        reset_mode="lifetime",
        window_start=None,
        window_end=None,  # lifetime → pas de window_end
    )


from app.api.v1.schemas.natal_interpretation import (
    NatalInterpretationResponse,
    NatalInterpretationData,
    InterpretationMeta,
)
from app.llm_orchestration.schemas import AstroResponseV3

from app.infra.db.session import get_db_session

def _make_valid_interpretation_response(level="complete"):
    return NatalInterpretationResponse(
        data=NatalInterpretationData(
            chart_id="test_chart",
            use_case="natal_interpretation",
            interpretation=AstroResponseV3(
                title="Test Title",
                summary="A" * 901,
                sections=[{
                    "key": "inner_life",
                    "heading": f"Heading {i}",
                    "content": "B" * 281
                } for i in range(5)],
                highlights=["H1", "H2", "H3", "H4", "H5"],
                advice=["A1", "A2", "A3", "A4", "A5"],
                evidence=[]
            ),
            meta=InterpretationMeta(
                level=level,
                use_case="natal_interpretation",
                validation_status="valid"
            )
        ),
        disclaimers=[]
    )


@pytest.fixture
def mock_user_and_chart():
    app.dependency_overrides[require_authenticated_user] = _override_auth
    with patch("app.services.user_natal_chart_service.UserNatalChartService.get_latest_for_user") as mock_chart, \
         patch("app.services.user_birth_profile_service.UserBirthProfileService.get_for_user") as mock_profile:
        
        chart_obj = MagicMock()
        chart_obj.chart_id = "test_chart"
        chart_obj.result = {}
        mock_chart.return_value = chart_obj
        
        profile_obj = MagicMock()
        mock_profile.return_value = profile_obj
        
        yield mock_chart, mock_profile
    app.dependency_overrides.pop(require_authenticated_user, None)
    app.dependency_overrides.pop(get_db_session, None)


def test_short_level_bypasses_gate(mock_user_and_chart):
    """use_case_level=short → gate non appelé, entitlement_info=None."""
    with patch("app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume") as mock_gate, \
         patch("app.services.natal_interpretation_service_v2.NatalInterpretationServiceV2.interpret") as mock_interpret:
        
        mock_interpret.return_value = _make_valid_interpretation_response(level="short")
        
        response = client.post("/v1/natal/interpretation", json=SHORT_PAYLOAD)
    
    assert response.status_code == 200
    mock_gate.assert_not_called()
    assert response.json().get("entitlement_info") is None


def test_complete_canonical_quota_ok(mock_user_and_chart):
    usage_state = _make_usage_state(used=1, limit=1, remaining=0)
    result = NatalChartLongEntitlementResult(
        path="canonical_quota",
        variant_code="single_astrologer",
        usage_states=[usage_state]
    )

    with patch("app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
               return_value=result), \
         patch("app.services.natal_interpretation_service_v2.NatalInterpretationServiceV2.interpret") as mock_interpret:
        
        mock_interpret.return_value = _make_valid_interpretation_response(level="complete")
        
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)
    
    assert response.status_code == 200
    data = response.json()
    assert data["entitlement_info"]["remaining"] == 0
    assert data["entitlement_info"]["limit"] == 1
    assert data["entitlement_info"]["variant_code"] == "single_astrologer"


def test_complete_canonical_unlimited_ok(mock_user_and_chart):
    result = NatalChartLongEntitlementResult(
        path="canonical_unlimited",
        variant_code="multi_astrologer",
        usage_states=[]
    )

    with patch("app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
               return_value=result), \
         patch("app.services.natal_interpretation_service_v2.NatalInterpretationServiceV2.interpret") as mock_interpret:
        
        mock_interpret.return_value = _make_valid_interpretation_response(level="complete")
        
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)
    
    assert response.status_code == 200
    data = response.json()
    assert data["entitlement_info"]["remaining"] is None
    assert data["entitlement_info"]["variant_code"] == "multi_astrologer"


def test_complete_no_plan_rejected(mock_user_and_chart):
    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongAccessDeniedError(reason="no_plan", billing_status="none", plan_code=""),
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)
    
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "natal_chart_long_access_denied"
    assert response.json()["error"]["details"]["reason"] == "no_plan"


def test_complete_quota_exhausted_rejected(mock_user_and_chart):
    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongQuotaExceededError(
            quota_key="interpretations", used=1, limit=1, window_end=None
        ),
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)
    
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "natal_chart_long_quota_exceeded"
    assert response.json()["error"]["details"]["window_end"] is None


def test_complete_disabled_binding_returns_disabled_by_plan(mock_user_and_chart):
    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongAccessDeniedError(reason="disabled_by_plan", billing_status="active", plan_code="free"),
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)
    
    assert response.status_code == 403
    assert response.json()["error"]["details"]["reason"] == "disabled_by_plan"


def test_complete_no_canonical_binding_returns_no_binding(mock_user_and_chart):
    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongAccessDeniedError(reason="canonical_no_binding", billing_status="active", plan_code="basic"),
    ):
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)
    
    assert response.status_code == 403
    assert response.json()["error"]["details"]["reason"] == "canonical_no_binding"


def test_complete_rolls_back_on_access_denied(mock_user_and_chart, db_session):
    from app.infra.db.session import get_db_session
    app.dependency_overrides[get_db_session] = lambda: db_session
    
    with patch(
        "app.services.natal_chart_long_entitlement_gate.NatalChartLongEntitlementGate.check_and_consume",
        side_effect=NatalChartLongAccessDeniedError(reason="no_plan", billing_status="none", plan_code=""),
    ):
        with patch.object(db_session, 'rollback') as mock_rollback:
            response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)
    
    assert response.status_code == 403
    mock_rollback.assert_called()
