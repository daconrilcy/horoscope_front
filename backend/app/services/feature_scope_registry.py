from enum import Enum


class FeatureScope(str, Enum):
    B2C = "b2c"
    B2B = "b2b"


class UnknownFeatureCodeError(ValueError):
    def __init__(self, feature_code: str) -> None:
        self.feature_code = feature_code
        super().__init__(
            f"Unknown feature_code '{feature_code}'. "
            "Register it in FEATURE_SCOPE_REGISTRY before use."
        )


class InvalidQuotaScopeError(ValueError):
    def __init__(
        self,
        feature_code: str,
        actual_scope: FeatureScope,
        expected_scope: FeatureScope,
    ) -> None:
        self.feature_code = feature_code
        self.actual_scope = actual_scope
        self.expected_scope = expected_scope
        correct_service = _service_name_for_scope(actual_scope)
        wrong_service = _service_name_for_scope(expected_scope)
        super().__init__(
            f"feature_code '{feature_code}' is {actual_scope.value.upper()} — "
            f"use {correct_service}, not {wrong_service}."
        )


# Source unique de vérité pour le scope de chaque feature_code.
# IMPORTANT: Tout nouveau feature_code DOIT être enregistré ici avant utilisation.
FEATURE_SCOPE_REGISTRY: dict[str, FeatureScope] = {
    # B2C features (QuotaUsageService + feature_usage_counters)
    "natal_chart_short": FeatureScope.B2C,
    "astrologer_chat": FeatureScope.B2C,
    "thematic_consultation": FeatureScope.B2C,
    "natal_chart_long": FeatureScope.B2C,
    "horoscope_daily": FeatureScope.B2C,
    # B2B features (EnterpriseQuotaUsageService + enterprise_feature_usage_counters)
    "b2b_api_access": FeatureScope.B2B,
}


def get_feature_scope(feature_code: str) -> FeatureScope:
    """Retourne le scope du feature_code ou lève UnknownFeatureCodeError."""
    scope = FEATURE_SCOPE_REGISTRY.get(feature_code)
    if scope is None:
        raise UnknownFeatureCodeError(feature_code)
    return scope


def require_feature_scope(feature_code: str, expected_scope: FeatureScope) -> None:
    """Valide le scope d'un feature_code et bloque tout mauvais routage de service."""
    actual_scope = get_feature_scope(feature_code)
    if actual_scope != expected_scope:
        raise InvalidQuotaScopeError(
            feature_code=feature_code,
            actual_scope=actual_scope,
            expected_scope=expected_scope,
        )


def _service_name_for_scope(scope: FeatureScope) -> str:
    if scope == FeatureScope.B2C:
        return "QuotaUsageService"
    return "EnterpriseQuotaUsageService"
