from typing import Literal

from app.api.v1.schemas.consultation import (
    ConsultationPrecheckData,
    ConsultationStatus,
    FallbackMode,
    PrecisionLevel,
    SafeguardIssue,
)

SafeguardResolution = Literal["fallback", "refusal", "reframing"]

SAFEGUARD_MATRIX: dict[SafeguardIssue, SafeguardResolution] = {
    SafeguardIssue.health: "refusal",
    SafeguardIssue.emotional_distress: "reframing",
    SafeguardIssue.obsessive_relation: "reframing",
    SafeguardIssue.pregnancy: "refusal",
    SafeguardIssue.death: "refusal",
    SafeguardIssue.legal_finance: "reframing",
    SafeguardIssue.third_party_manipulation: "refusal",
}


class ConsultationFallbackService:
    @staticmethod
    def resolve_safeguard(issue: SafeguardIssue) -> SafeguardResolution:
        return SAFEGUARD_MATRIX.get(issue, "refusal")

    @staticmethod
    def resolve_route_key(data: ConsultationPrecheckData) -> str | None:
        if data.status == ConsultationStatus.blocked or data.fallback_mode in {
            FallbackMode.safeguard_reframed,
            FallbackMode.safeguard_refused,
        }:
            return None

        consultation_type = data.consultation_type
        precision = data.precision_level
        fallback_mode = data.fallback_mode

        if consultation_type in {"period", "career", "work", "orientation"}:
            if precision == PrecisionLevel.high:
                return f"{consultation_type}_full"
            return f"{consultation_type}_no_birth_time"

        if consultation_type in {"relationship", "relation"}:
            route_prefix = "relationship" if consultation_type == "relationship" else "relation"
            if fallback_mode == FallbackMode.other_no_birth_time:
                return f"{route_prefix}_full_other_no_time"
            if fallback_mode == FallbackMode.relation_user_only:
                return f"{route_prefix}_user_only"
            if precision == PrecisionLevel.high:
                return f"{route_prefix}_full_full"
            return f"{route_prefix}_user_only"

        if consultation_type == "timing":
            if precision == PrecisionLevel.high:
                return "timing_full"
            return "timing_degraded"

        return None
