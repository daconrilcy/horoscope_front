import pytest

from app.services.feature_scope_registry import (
    FeatureScope,
    InvalidQuotaScopeError,
    UnknownFeatureCodeError,
    get_feature_scope,
)


def test_known_b2c_feature_codes():
    assert get_feature_scope("astrologer_chat") == FeatureScope.B2C
    assert get_feature_scope("thematic_consultation") == FeatureScope.B2C
    assert get_feature_scope("natal_chart_long") == FeatureScope.B2C


def test_known_b2b_feature_codes():
    assert get_feature_scope("b2b_api_access") == FeatureScope.B2B


def test_unknown_feature_code_raises():
    with pytest.raises(UnknownFeatureCodeError) as exc_info:
        get_feature_scope("unknown_code")
    assert "unknown_code" in str(exc_info.value)


def test_invalid_scope_error_message_b2b():
    # Test documentation requirement: verify message contains
    # EnterpriseQuotaUsageService for B2B features
    exc = InvalidQuotaScopeError(
        feature_code="b2b_api_access",
        actual_scope=FeatureScope.B2B,
        expected_scope=FeatureScope.B2C,
        correct_service="EnterpriseQuotaUsageService",
        wrong_service="QuotaUsageService",
    )
    assert "feature_code 'b2b_api_access' is B2B" in str(exc)
    assert "use EnterpriseQuotaUsageService, not QuotaUsageService" in str(exc)
