from unittest.mock import patch

import pytest

from app.services.entitlement.feature_scope_registry import FEATURE_SCOPE_REGISTRY, FeatureScope
from app.services.feature_registry_consistency_validator import (
    FeatureRegistryConsistencyError,
    FeatureRegistryConsistencyValidator,
)


def test_validator_passes_with_valid_registry():
    """État actuel du code -> validate() ne lève pas d'exception."""
    FeatureRegistryConsistencyValidator.validate()


def test_validator_fails_on_missing_registry_entry():
    broken_registry = {k: v for k, v in FEATURE_SCOPE_REGISTRY.items() if k != "astrologer_chat"}

    with patch.dict(
        "app.services.entitlement.feature_scope_registry.FEATURE_SCOPE_REGISTRY",
        broken_registry,
        clear=True,
    ):
        with pytest.raises(FeatureRegistryConsistencyError) as excinfo:
            FeatureRegistryConsistencyValidator.validate()

        assert "astrologer_chat" in str(excinfo.value)


def test_validator_fails_on_wrong_scope_b2b_as_b2c():
    broken_registry = FEATURE_SCOPE_REGISTRY.copy()
    broken_registry["b2b_api_access"] = FeatureScope.B2C

    with patch.dict(
        "app.services.entitlement.feature_scope_registry.FEATURE_SCOPE_REGISTRY",
        broken_registry,
        clear=True,
    ):
        with pytest.raises(FeatureRegistryConsistencyError) as excinfo:
            FeatureRegistryConsistencyValidator.validate()

        assert "b2b_api_access" in str(excinfo.value)
        assert "b2b" in str(excinfo.value).lower()


def test_validator_fails_on_wrong_scope_b2c_as_b2b():
    broken_registry = FEATURE_SCOPE_REGISTRY.copy()
    broken_registry["astrologer_chat"] = FeatureScope.B2B

    with patch.dict(
        "app.services.entitlement.feature_scope_registry.FEATURE_SCOPE_REGISTRY",
        broken_registry,
        clear=True,
    ):
        with pytest.raises(FeatureRegistryConsistencyError) as excinfo:
            FeatureRegistryConsistencyValidator.validate()

        assert "astrologer_chat" in str(excinfo.value)
        assert "b2c" in str(excinfo.value).lower()


def test_validator_fails_on_missing_seed_feature():
    broken_registry = {k: v for k, v in FEATURE_SCOPE_REGISTRY.items() if k != "natal_chart_long"}

    with patch.dict(
        "app.services.entitlement.feature_scope_registry.FEATURE_SCOPE_REGISTRY",
        broken_registry,
        clear=True,
    ):
        with pytest.raises(FeatureRegistryConsistencyError) as excinfo:
            FeatureRegistryConsistencyValidator.validate()

        assert "natal_chart_long" in str(excinfo.value)


def test_validator_collects_invalid_scope_type_without_crashing():
    broken_registry = FEATURE_SCOPE_REGISTRY.copy()
    broken_registry["astrologer_chat"] = "b2c"

    with patch.dict(
        "app.services.entitlement.feature_scope_registry.FEATURE_SCOPE_REGISTRY",
        broken_registry,
        clear=True,
    ):
        with pytest.raises(FeatureRegistryConsistencyError) as excinfo:
            FeatureRegistryConsistencyValidator.validate()

    message = str(excinfo.value)
    assert "astrologer_chat" in message
    assert "Scope invalide 'b2c' (type str)" in message
    assert "Doit être une instance de FeatureScope" in message
