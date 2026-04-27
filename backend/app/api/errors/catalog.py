"""Catalogue typé des erreurs HTTP exposées par l'API."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ApiErrorCode(StrEnum):
    """Codes d'erreur transverses réutilisables par les routeurs."""

    INSUFFICIENT_ROLE = "insufficient_role"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INTERNAL_ERROR = "internal_error"
    AUDIT_UNAVAILABLE = "audit_unavailable"
    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"


@dataclass(frozen=True, kw_only=True)
class HttpErrorDefinition:
    """Associe un code applicatif à un statut HTTP et un message public."""

    code: str
    status_code: int
    message: str


HTTP_ERROR_CATALOG: tuple[HttpErrorDefinition, ...] = (
    HttpErrorDefinition(
        code=ApiErrorCode.INVALID_REQUEST.value,
        status_code=400,
        message="request is invalid",
    ),
    HttpErrorDefinition(
        code=ApiErrorCode.UNAUTHORIZED.value,
        status_code=401,
        message="authentication is required",
    ),
    HttpErrorDefinition(
        code=ApiErrorCode.FORBIDDEN.value,
        status_code=403,
        message="access is forbidden",
    ),
    HttpErrorDefinition(
        code=ApiErrorCode.NOT_FOUND.value,
        status_code=404,
        message="resource was not found",
    ),
    HttpErrorDefinition(
        code=ApiErrorCode.RATE_LIMIT_EXCEEDED.value,
        status_code=429,
        message="rate limit exceeded",
    ),
    HttpErrorDefinition(
        code=ApiErrorCode.AUDIT_UNAVAILABLE.value,
        status_code=503,
        message="audit persistence is unavailable",
    ),
    HttpErrorDefinition(
        code=ApiErrorCode.INTERNAL_ERROR.value,
        status_code=500,
        message="internal server error",
    ),
)


_EXPLICIT_STATUS_BY_CODE: dict[str, int] = {
    entry.code: entry.status_code for entry in HTTP_ERROR_CATALOG
}
_EXPLICIT_STATUS_BY_CODE.update(
    {
        "account_suspended": 403,
        "alert_event_not_retryable": 409,
        "audit_forbidden": 403,
        "birth_profile_not_found": 404,
        "b2b_api_access_denied": 403,
        "b2b_api_quota_exceeded": 429,
        "b2b_no_binding": 403,
        "b2b_no_canonical_plan": 403,
        "chart_result_not_found": 404,
        "compute_failed": 503,
        "coherence_validation_failed": 400,
        "endpoint_not_available": 404,
        "ephemeris_calc_failed": 503,
        "gateway_config_error": 500,
        "houses_calc_failed": 503,
        "invalid_birth_input": 422,
        "diff_filter_result_set_too_large": 400,
        "enterprise_account_inactive": 422,
        "invalid_api_key": 401,
        "invalid_request_payload": 422,
        "invalid_token": 401,
        "invalid_token_type": 401,
        "insufficient_role": 403,
        "lint_failed": 422,
        "interpretation_failed": 502,
        "llm_rate_limit": 429,
        "llm_upstream_timeout": 504,
        "missing_timezone": 422,
        "missing_access_token": 401,
        "missing_api_key": 401,
        "natal_chart_not_found": 404,
        "natal_chart_long_access_denied": 403,
        "natal_chart_long_quota_exceeded": 429,
        "natal_missing": 404,
        "output_validation_error": 422,
        "persona_profile_archive_forbidden": 422,
        "plan_price_not_configured": 422,
        "privacy_evidence_incomplete": 422,
        "revoked_api_key": 403,
        "runtime_preview_incomplete_for_execution": 422,
        "sample_payload_inactive": 422,
        "sample_payload_runtime_preview_only": 422,
        "sample_payload_target_mismatch": 422,
        "snapshot_bundle_unusable": 422,
        "stripe_api_error": 502,
        "stripe_portal_subscription_update_disabled": 422,
        "stripe_portal_subscription_update_no_change_options": 422,
        "stripe_portal_subscription_update_not_allowed_for_trial": 422,
        "upstream_timeout": 504,
        "unknown_use_case": 404,
        "invalid_signature": 400,
        "webhook_secret_not_configured": 503,
        "stripe_billing_profile_not_found": 404,
        "stripe_portal_configuration_missing": 503,
        "stripe_subscription_not_found": 404,
        "stripe_unavailable": 503,
        "token_expired": 401,
        "weekly_generation_failed": 422,
    }
)


def resolve_application_error_status(code: str) -> int:
    """Résout le statut HTTP d'un code applicatif à la frontière API."""
    if code in _EXPLICIT_STATUS_BY_CODE:
        return _EXPLICIT_STATUS_BY_CODE[code]
    if code.endswith("_not_found") or "not_found" in code:
        return 404
    if "forbidden" in code or "not_allowed" in code or code.endswith("_disabled"):
        return 403
    if "unauthorized" in code or "authentication" in code:
        return 401
    if "rate_limit" in code or "quota" in code:
        return 429
    if "unavailable" in code or "timeout" in code:
        return 503
    if "conflict" in code or code.endswith("_already_exists"):
        return 409
    if "eval_failed" in code or "golden_regression_failed" in code:
        return 409
    if "gateway" in code:
        return 502
    if "invalid" in code or "validation" in code or code.endswith("_required"):
        return 422
    if "ambiguous" in code or "nonexistent" in code:
        return 422
    return 500


def validate_error_catalog() -> None:
    """Vérifie les invariants du catalogue au démarrage des tests."""
    codes = [entry.code for entry in HTTP_ERROR_CATALOG]
    if len(codes) != len(set(codes)):
        raise ValueError("api error catalog contains duplicate codes")
    for entry in HTTP_ERROR_CATALOG:
        if not 400 <= entry.status_code <= 599:
            raise ValueError(f"invalid HTTP status for error code {entry.code}")
        if not entry.message.strip():
            raise ValueError(f"empty message for error code {entry.code}")
