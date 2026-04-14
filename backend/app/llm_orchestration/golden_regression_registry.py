from __future__ import annotations

from typing import Dict, FrozenSet, Set

from app.llm_orchestration.models import ExecutionPathKind, FallbackType


class GoldenRegressionThresholds:
    def __init__(
        self,
        strict_obs_fields: Set[str],
        thresholded_obs_fields: Dict[str, float],
        informational_obs_fields: Set[str],
        forbidden_execution_profile_sources: Set[str],
        forbidden_execution_paths: Set[ExecutionPathKind],
        forbidden_fallbacks: Set[FallbackType],
    ):
        self.strict_obs_fields = strict_obs_fields
        self.thresholded_obs_fields = thresholded_obs_fields
        self.informational_obs_fields = informational_obs_fields
        self.forbidden_execution_profile_sources = forbidden_execution_profile_sources
        self.forbidden_execution_paths = forbidden_execution_paths
        self.forbidden_fallbacks = forbidden_fallbacks


def get_obs_snapshot_classification(
    thresholds: GoldenRegressionThresholds,
) -> Dict[str, FrozenSet[str]]:
    """
    Expose the doctrinal obs_snapshot classification independently from threshold values.

    The threshold registry remains the single source of truth, but callers that only need
    field classes should not have to infer semantics from tolerance-oriented attribute names.
    """

    return {
        "strict": frozenset(thresholds.strict_obs_fields),
        "thresholded": frozenset(thresholds.thresholded_obs_fields),
        "informational": frozenset(thresholds.informational_obs_fields),
    }


# AC8, AC18: Classification of obs_snapshot fields
# AC10: Forbidden legacy paths on supported perimeter
GOLDEN_THRESHOLDS_DEFAULT = GoldenRegressionThresholds(
    strict_obs_fields={
        "pipeline_kind",
        "execution_path_kind",
        "fallback_kind",
        "requested_provider",
        "resolved_provider",
        "executed_provider",
        "context_compensation_status",
        "max_output_tokens_source",
    },
    thresholded_obs_fields={
        "max_output_tokens_final": 0.1,  # 10% drift allowed
    },
    informational_obs_fields={
        "executed_provider_mode",
        "attempt_count",
        "provider_error_code",
        "breaker_state",
        "breaker_scope",
        "active_snapshot_id",
        "active_snapshot_version",
        "manifest_entry_id",
    },
    forbidden_execution_profile_sources={
        "fallback_resolve_model",
        "fallback_provider_unsupported",
    },
    forbidden_execution_paths={
        ExecutionPathKind.LEGACY_USE_CASE_FALLBACK,
        ExecutionPathKind.LEGACY_EXECUTION_PROFILE_FALLBACK,
        ExecutionPathKind.NON_NOMINAL_PROVIDER_TOLERATED,
    },
    forbidden_fallbacks={
        FallbackType.USE_CASE_FIRST,
        FallbackType.RESOLVE_MODEL,
        FallbackType.PROVIDER_OPENAI,
        FallbackType.DEPRECATED_USE_CASE,
    },
)

GOLDEN_REGISTRY: Dict[str, GoldenRegressionThresholds] = {
    "default": GOLDEN_THRESHOLDS_DEFAULT,
    "chat": GOLDEN_THRESHOLDS_DEFAULT,
    "guidance": GOLDEN_THRESHOLDS_DEFAULT,
    "natal": GOLDEN_THRESHOLDS_DEFAULT,
    "horoscope_daily": GOLDEN_THRESHOLDS_DEFAULT,
}

OBS_SNAPSHOT_CLASSIFICATION_DEFAULT = get_obs_snapshot_classification(GOLDEN_THRESHOLDS_DEFAULT)
