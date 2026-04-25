from app.services.canonical_entitlement.audit.diff_service import (
    CanonicalEntitlementMutationDiffService,
)

# Fixtures from Story Dev Notes
BEFORE_PAYLOAD_EMPTY = {}

BEFORE_PAYLOAD_BASIC = {
    "is_enabled": True,
    "access_mode": "unlimited",
    "variant_code": None,
    "source_origin": "stripe_webhook",
    "quotas": [],
}

AFTER_PAYLOAD_QUOTA = {
    "is_enabled": True,
    "access_mode": "quota",
    "variant_code": None,
    "source_origin": "stripe_webhook",
    "quotas": [
        {
            "quota_key": "daily",
            "quota_limit": 10,
            "period_unit": "day",
            "period_value": 1,
            "reset_mode": "calendar",
            "source_origin": "stripe_webhook",
        }
    ],
}


def test_binding_created_empty_before():
    # AC 9: test_binding_created_empty_before
    after = {
        "is_enabled": True,
        "access_mode": "unlimited",
        "variant_code": None,
        "source_origin": "stripe_webhook",
        "quotas": [],
    }
    result = CanonicalEntitlementMutationDiffService.compute_diff({}, after)
    assert result.change_kind == "binding_created"
    assert result.changed_fields == []
    assert result.risk_level == "medium"  # unlimited -> medium


def test_binding_updated_is_enabled_change():
    # AC 9: test_binding_updated_is_enabled_change
    before = {**BEFORE_PAYLOAD_BASIC}
    after = {**BEFORE_PAYLOAD_BASIC, "is_enabled": False}
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert result.change_kind == "binding_updated"
    assert "binding.is_enabled" in result.changed_fields
    assert result.risk_level == "high"


def test_access_mode_change_unlimited_to_quota():
    # AC 9: test_access_mode_change_unlimited_to_quota
    before = {**BEFORE_PAYLOAD_BASIC}
    after = {**BEFORE_PAYLOAD_BASIC, "access_mode": "quota"}
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert "binding.access_mode" in result.changed_fields
    assert result.risk_level == "high"


def test_quota_limit_decrease():
    # AC 9: test_quota_limit_decrease
    before = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 10,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    after = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 5,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert result.risk_level == "high"
    assert len(result.quota_changes.updated) == 1
    assert result.quota_changes.updated[0]["before_quota_limit"] == 10
    assert result.quota_changes.updated[0]["quota_limit"] == 5


def test_quota_limit_increase():
    # AC 9: test_quota_limit_increase
    before = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 10,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    after = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 20,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert result.risk_level == "medium"
    assert len(result.quota_changes.updated) == 1


def test_quota_added():
    # AC 9: test_quota_added
    before = {**BEFORE_PAYLOAD_BASIC, "quotas": []}
    after = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 10,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert result.risk_level == "medium"
    assert len(result.quota_changes.added) == 1
    assert "quotas[daily,day,1,calendar].quota_limit" not in result.changed_fields


def test_changed_fields_no_quota_path_for_added():
    # AC 9: test_changed_fields_no_quota_path_for_added
    before = {**BEFORE_PAYLOAD_BASIC, "quotas": []}
    after = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 10,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert len(result.quota_changes.added) == 1
    assert "quotas[daily,day,1,calendar].quota_limit" not in result.changed_fields


def test_quota_removed():
    # AC 9: test_quota_removed
    before = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 10,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    after = {**BEFORE_PAYLOAD_BASIC, "quotas": []}
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert result.risk_level == "high"
    assert len(result.quota_changes.removed) == 1


def test_variant_code_change():
    # AC 9: test_variant_code_change
    before = {**BEFORE_PAYLOAD_BASIC, "variant_code": "A"}
    after = {**BEFORE_PAYLOAD_BASIC, "variant_code": "B"}
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert "binding.variant_code" in result.changed_fields
    assert result.risk_level == "medium"


def test_source_origin_only_change():
    # AC 9: test_source_origin_only_change
    before = {**BEFORE_PAYLOAD_BASIC, "source_origin": "src1"}
    after = {**BEFORE_PAYLOAD_BASIC, "source_origin": "src2"}
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert "binding.source_origin" in result.changed_fields
    assert result.risk_level == "low"


def test_noop_before_equals_after():
    # AC 9: test_noop_before_equals_after
    before = {**BEFORE_PAYLOAD_BASIC}
    after = {**BEFORE_PAYLOAD_BASIC}
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert result.changed_fields == []
    assert result.risk_level == "low"


def test_quota_key_path_format():
    # AC 9: test_quota_key_path_format
    before = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 10,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    after = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 5,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert "quotas[daily,day,1,calendar].quota_limit" in result.changed_fields


def test_binding_created_quota_access_mode():
    # AC 9: test_binding_created_quota_access_mode
    after = {**BEFORE_PAYLOAD_BASIC, "access_mode": "quota"}
    result = CanonicalEntitlementMutationDiffService.compute_diff({}, after)
    assert result.risk_level == "high"


def test_binding_created_disabled_access_mode():
    # AC 9: test_binding_created_disabled_access_mode
    after = {**BEFORE_PAYLOAD_BASIC, "access_mode": "disabled"}
    result = CanonicalEntitlementMutationDiffService.compute_diff({}, after)
    assert result.risk_level == "low"


def test_changed_fields_no_quota_path_for_removed():
    # AC 9: test_changed_fields_no_quota_path_for_removed
    before = {
        **BEFORE_PAYLOAD_BASIC,
        "quotas": [
            {
                "quota_key": "daily",
                "quota_limit": 10,
                "period_unit": "day",
                "period_value": 1,
                "reset_mode": "calendar",
                "source_origin": "stripe_webhook",
            }
        ],
    }
    after = {**BEFORE_PAYLOAD_BASIC, "quotas": []}
    result = CanonicalEntitlementMutationDiffService.compute_diff(before, after)
    assert len(result.quota_changes.removed) == 1
    assert "quotas[daily,day,1,calendar].quota_limit" not in result.changed_fields
