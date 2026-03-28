from unittest.mock import patch

import pytest

from app.services.feature_registry_consistency_validator import (
    FeatureRegistryConsistencyError,
    FeatureRegistryConsistencyValidator,
)
from app.services.feature_scope_registry import FEATURE_SCOPE_REGISTRY, FeatureScope


def test_validator_passes_with_valid_registry():
    """
    État actuel du code -> validate() ne lève pas d'exception.
    """
    # Ne devrait pas lever d'exception si le registre actuel est cohérent
    FeatureRegistryConsistencyValidator.validate()

def test_validator_fails_on_missing_registry_entry():
    """
    Patcher FEATURE_SCOPE_REGISTRY sans 'astrologer_chat' -> lève FeatureRegistryConsistencyError.
    """
    broken_registry = {k: v for k, v in FEATURE_SCOPE_REGISTRY.items() if k != "astrologer_chat"}
    
    with patch(
        "app.services.feature_registry_consistency_validator.FEATURE_SCOPE_REGISTRY",
        broken_registry,
    ):
        with pytest.raises(FeatureRegistryConsistencyError) as excinfo:
            FeatureRegistryConsistencyValidator.validate()
        assert "astrologer_chat" in str(excinfo.value)

def test_validator_fails_on_wrong_scope_b2b_as_b2c():
    """
    Patcher FEATURE_SCOPE_REGISTRY avec 'b2b_api_access' -> FeatureScope.B2C.
    """
    broken_registry = FEATURE_SCOPE_REGISTRY.copy()
    broken_registry["b2b_api_access"] = FeatureScope.B2C
    
    with patch(
        "app.services.feature_registry_consistency_validator.FEATURE_SCOPE_REGISTRY",
        broken_registry,
    ):
        with pytest.raises(FeatureRegistryConsistencyError) as excinfo:
            FeatureRegistryConsistencyValidator.validate()
        assert "b2b_api_access" in str(excinfo.value)
        assert "b2b" in str(excinfo.value).lower()

def test_validator_fails_on_wrong_scope_b2c_as_b2b():
    """
    Patcher scope de 'astrologer_chat' -> FeatureScope.B2B.
    """
    broken_registry = FEATURE_SCOPE_REGISTRY.copy()
    broken_registry["astrologer_chat"] = FeatureScope.B2B
    
    with patch(
        "app.services.feature_registry_consistency_validator.FEATURE_SCOPE_REGISTRY",
        broken_registry,
    ):
        with pytest.raises(FeatureRegistryConsistencyError) as excinfo:
            FeatureRegistryConsistencyValidator.validate()
        assert "astrologer_chat" in str(excinfo.value)
        assert "b2c" in str(excinfo.value).lower()

def test_validator_fails_on_missing_seed_feature():
    """
    Patcher FEATURE_SCOPE_REGISTRY pour retirer une feature metered B2C.
    """
    # On retire 'natal_chart_long' qui est une feature metered B2C du seed
    broken_registry = {k: v for k, v in FEATURE_SCOPE_REGISTRY.items() if k != "natal_chart_long"}
    
    with patch(
        "app.services.feature_registry_consistency_validator.FEATURE_SCOPE_REGISTRY",
        broken_registry,
    ):
        with pytest.raises(FeatureRegistryConsistencyError) as excinfo:
            FeatureRegistryConsistencyValidator.validate()
        assert "natal_chart_long" in str(excinfo.value)
