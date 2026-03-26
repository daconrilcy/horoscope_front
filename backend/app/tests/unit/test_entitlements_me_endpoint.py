from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.main import app
from app.services.entitlement_types import FeatureEntitlement, UsageState

client = TestClient(app)


def _override_auth(user_id=42, role="user"):
    def _override():
        return AuthenticatedUser(
            id=user_id,
            role=role,
            email="test@example.com",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

    return _override


def test_role_guard_b2b_user():
    """Vérifie que l'endpoint retourne 403 pour un rôle non autorisé (ex: b2b_user)."""
    app.dependency_overrides[require_authenticated_user] = _override_auth(role="b2b_user")
    response = client.get("/v1/entitlements/me")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"
    app.dependency_overrides.clear()


@patch("app.services.entitlement_service.EntitlementService.get_feature_entitlement")
def test_no_plan_user(mock_get_entitlement):
    """Vérifie que pour un utilisateur sans plan, toutes les features sont en reason='no_plan'."""
    app.dependency_overrides[require_authenticated_user] = _override_auth()

    # Mock retourne une entitlement 'no_plan'
    mock_get_entitlement.return_value = FeatureEntitlement(
        plan_code="none",
        billing_status="none",
        is_enabled_by_plan=False,
        access_mode="disabled",
        variant_code=None,
        quotas=[],
        final_access=False,
        reason="no_plan",
        usage_states=[],
    )

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200

    data = response.json()["data"]
    features = data["features"]
    assert len(features) == 4
    for f in features:
        assert f["final_access"] is False
        assert f["reason"] == "no_plan"
        assert f["usage_states"] == []

    # Vérifie que get_feature_entitlement a été appelé pour les 4 features
    assert mock_get_entitlement.call_count == 4
    app.dependency_overrides.clear()


@patch("app.services.entitlement_service.EntitlementService.get_feature_entitlement")
def test_billing_inactive(mock_get_entitlement):
    """Vérifie le retour quand le billing est inactif (ex: past_due)."""
    app.dependency_overrides[require_authenticated_user] = _override_auth()

    mock_get_entitlement.return_value = FeatureEntitlement(
        plan_code="basic",
        billing_status="past_due",
        is_enabled_by_plan=True,
        access_mode="quota",
        variant_code=None,
        quotas=[],
        final_access=False,
        reason="billing_inactive",
        usage_states=[],
    )

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200
    features = response.json()["data"]["features"]
    for f in features:
        assert f["final_access"] is False
        assert f["reason"] == "billing_inactive"
    app.dependency_overrides.clear()


@patch("app.services.quota_usage_service.QuotaUsageService.consume")
@patch("app.services.entitlement_service.EntitlementService.get_feature_entitlement")
def test_quota_path_no_consume(mock_get_entitlement, mock_consume):
    """Vérifie que l'endpoint n'appelle JAMAIS consume (lecture seule)."""
    app.dependency_overrides[require_authenticated_user] = _override_auth()

    mock_get_entitlement.return_value = FeatureEntitlement(
        plan_code="basic",
        billing_status="active",
        is_enabled_by_plan=True,
        access_mode="quota",
        variant_code=None,
        quotas=[],
        final_access=True,
        reason="canonical_binding",
        usage_states=[
            UsageState(
                feature_code="astrologer_chat",
                quota_key="messages",
                quota_limit=5,
                used=1,
                remaining=4,
                exhausted=False,
                period_unit="day",
                period_value=1,
                reset_mode="calendar",
                window_start=datetime.now(timezone.utc),
                window_end=datetime.now(timezone.utc),
            )
        ],
    )

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200

    # Vérifie que consume n'a JAMAIS été appelé
    mock_consume.assert_not_called()
    app.dependency_overrides.clear()


@patch("app.services.entitlement_service.EntitlementService.get_feature_entitlement")
def test_unknown_feature_included_gracefully(mock_get_entitlement):
    """Vérifie qu'une feature inconnue ou sans binding est incluse sans erreur 500."""
    app.dependency_overrides[require_authenticated_user] = _override_auth()

    mock_get_entitlement.return_value = FeatureEntitlement(
        plan_code="basic",
        billing_status="active",
        is_enabled_by_plan=True,
        access_mode="unknown",
        variant_code=None,
        quotas=[],
        final_access=False,
        reason="feature_unknown",
        usage_states=[],
    )

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200
    features = response.json()["data"]["features"]
    assert len(features) == 4
    for f in features:
        assert f["reason"] == "feature_unknown"
    app.dependency_overrides.clear()
