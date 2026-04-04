from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.main import app
from app.services.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    UsageState,
)

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


def _make_access(
    granted: bool,
    reason_code: str,
    access_mode: str | None = None,
    variant_code: str | None = None,
    quota_limit: int | None = None,
    quota_used: int | None = None,
    quota_remaining: int | None = None,
    period_unit: str | None = None,
    period_value: int | None = None,
    reset_mode: str | None = None,
    usage_states: list[UsageState] = None,
) -> EffectiveFeatureAccess:
    return EffectiveFeatureAccess(
        granted=granted,
        reason_code=reason_code,
        access_mode=access_mode,
        variant_code=variant_code,
        quota_limit=quota_limit,
        quota_used=quota_used,
        quota_remaining=quota_remaining,
        period_unit=period_unit,
        period_value=period_value,
        reset_mode=reset_mode,
        usage_states=usage_states or [],
    )


def test_role_guard_b2b_user():
    """Vérifie que l'endpoint retourne 403 pour un rôle non autorisé (ex: b2b_user)."""
    app.dependency_overrides[require_authenticated_user] = _override_auth(role="b2b_user")
    response = client.get("/v1/entitlements/me")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"
    app.dependency_overrides.clear()


@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.compute_upgrade_hints"
)
@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.resolve_b2c_user_snapshot"
)
def test_no_plan_user(mock_resolve, mock_hints):
    """
    Vérifie que pour un utilisateur sans plan, toutes les features sont en
    reason_code='feature_not_in_plan'.
    """
    app.dependency_overrides[require_authenticated_user] = _override_auth()
    mock_hints.return_value = []

    # Mock retourne un snapshot 'none'
    mock_resolve.return_value = EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=42,
        plan_code="none",
        billing_status="none",
        entitlements={
            fc: _make_access(granted=False, reason_code="feature_not_in_plan")
            for fc in [
                "astrologer_chat",
                "thematic_consultation",
                "natal_chart_long",
                "natal_chart_short",
                "horoscope_daily",
            ]
        },
    )

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["plan_code"] == "none"
    assert data["billing_status"] == "none"
    features = data["features"]
    assert len(features) == 5
    for f in features:
        assert f["granted"] is False
        assert f["reason_code"] == "feature_not_in_plan"
        assert f["usage_states"] == []

    # Vérifie que le resolver a été appelé une fois
    assert mock_resolve.call_count == 1
    app.dependency_overrides.clear()


@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.compute_upgrade_hints"
)
@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.resolve_b2c_user_snapshot"
)
def test_billing_inactive(mock_resolve, mock_hints):
    """Vérifie le retour quand le billing est inactif (ex: past_due)."""
    app.dependency_overrides[require_authenticated_user] = _override_auth()
    mock_hints.return_value = []

    mock_resolve.return_value = EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=42,
        plan_code="basic",
        billing_status="past_due",
        entitlements={
            fc: _make_access(granted=False, reason_code="billing_inactive", access_mode="quota")
            for fc in [
                "astrologer_chat",
                "thematic_consultation",
                "natal_chart_long",
                "natal_chart_short",
                "horoscope_daily",
            ]
        },
    )

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["plan_code"] == "basic"
    assert data["billing_status"] == "past_due"
    features = data["features"]
    assert len(features) == 5
    for f in features:
        assert f["granted"] is False
        assert f["reason_code"] == "billing_inactive"
    app.dependency_overrides.clear()


@patch("app.services.quota_usage_service.QuotaUsageService.consume")
@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.compute_upgrade_hints"
)
@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.resolve_b2c_user_snapshot"
)
def test_quota_path_no_consume(mock_resolve, mock_hints, mock_consume):
    """Vérifie que l'endpoint n'appelle JAMAIS consume (lecture seule)."""
    app.dependency_overrides[require_authenticated_user] = _override_auth()
    mock_hints.return_value = []

    usage = UsageState(
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

    mock_resolve.return_value = EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=42,
        plan_code="basic",
        billing_status="active",
        entitlements={
            "astrologer_chat": _make_access(
                granted=True,
                reason_code="granted",
                access_mode="quota",
                quota_remaining=4,
                quota_limit=5,
                usage_states=[usage],
            ),
            "thematic_consultation": _make_access(granted=True, reason_code="granted"),
            "natal_chart_long": _make_access(granted=True, reason_code="granted"),
            "natal_chart_short": _make_access(granted=True, reason_code="granted"),
            "horoscope_daily": _make_access(granted=True, reason_code="granted"),
        },
    )

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200

    # Vérifie que consume n'a JAMAIS été appelé
    mock_consume.assert_not_called()
    app.dependency_overrides.clear()


@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.compute_upgrade_hints"
)
@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.resolve_b2c_user_snapshot"
)
def test_unknown_feature_ignored_gracefully(mock_resolve, mock_hints):
    """Vérifie qu'une feature présente dans le snapshot mais hors FEATURES_TO_QUERY est ignorée."""
    app.dependency_overrides[require_authenticated_user] = _override_auth()
    mock_hints.return_value = []

    mock_resolve.return_value = EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=42,
        plan_code="basic",
        billing_status="active",
        entitlements={
            "unknown_feature": _make_access(
                granted=True,
                reason_code="granted",
                access_mode="unlimited",
            ),
            # Les 5 features prioritaires
            "astrologer_chat": _make_access(granted=True, reason_code="granted"),
            "thematic_consultation": _make_access(granted=True, reason_code="granted"),
            "natal_chart_long": _make_access(granted=True, reason_code="granted"),
            "natal_chart_short": _make_access(granted=True, reason_code="granted"),
            "horoscope_daily": _make_access(granted=True, reason_code="granted"),
        },
    )

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200
    features = response.json()["data"]["features"]
    # On vérifie qu'on n'a QUE les 5 features prioritaires (AC2)
    assert len(features) == 5
    feature_codes = [f["feature_code"] for f in features]
    assert "unknown_feature" not in feature_codes
    app.dependency_overrides.clear()


@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.compute_upgrade_hints"
)
@patch(
    "app.services.effective_entitlement_resolver_service.EffectiveEntitlementResolverService.resolve_b2c_user_snapshot"
)
def test_missing_priority_feature_is_returned_as_denied(mock_resolve, mock_hints):
    """Vérifie qu'une feature prioritaire absente du snapshot reste présente dans la réponse."""
    app.dependency_overrides[require_authenticated_user] = _override_auth()
    mock_hints.return_value = []

    mock_resolve.return_value = EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=42,
        plan_code="basic",
        billing_status="active",
        entitlements={
            "astrologer_chat": _make_access(granted=True, reason_code="granted"),
            "thematic_consultation": _make_access(granted=True, reason_code="granted"),
            "natal_chart_short": _make_access(granted=True, reason_code="granted"),
            "horoscope_daily": _make_access(granted=True, reason_code="granted"),
        },
    )

    response = client.get("/v1/entitlements/me")
    assert response.status_code == 200

    features = response.json()["data"]["features"]
    assert len(features) == 5
    missing_feature = next(f for f in features if f["feature_code"] == "natal_chart_long")
    assert missing_feature["granted"] is False
    assert missing_feature["reason_code"] == "feature_not_in_plan"
    assert missing_feature["access_mode"] is None
    assert missing_feature["usage_states"] == []
    app.dependency_overrides.clear()
