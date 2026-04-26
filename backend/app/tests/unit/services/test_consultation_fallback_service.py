from app.api.v1.schemas.routers.public.consultation import (
    ConsultationPrecheckData,
    ConsultationStatus,
    FallbackMode,
    PrecisionLevel,
)
from app.services.consultation.fallback_service import ConsultationFallbackService


def test_resolve_route_key_period_full():
    data = ConsultationPrecheckData(
        consultation_type="period",
        user_profile_quality="complete",
        precision_level=PrecisionLevel.high,
        status=ConsultationStatus.nominal,
        missing_fields=[],
        available_modes=["nominal"],
        blocking_reasons=[],
    )
    assert ConsultationFallbackService.resolve_route_key(data) == "period_full"


def test_resolve_route_key_period_degraded():
    data = ConsultationPrecheckData(
        consultation_type="period",
        user_profile_quality="incomplete",
        precision_level=PrecisionLevel.medium,
        status=ConsultationStatus.degraded,
        missing_fields=[],
        available_modes=["user_no_birth_time"],
        fallback_mode=FallbackMode.user_no_birth_time,
        blocking_reasons=[],
    )
    assert ConsultationFallbackService.resolve_route_key(data) == "period_no_birth_time"


def test_resolve_route_key_relationship_full_full():
    data = ConsultationPrecheckData(
        consultation_type="relationship",
        user_profile_quality="complete",
        precision_level=PrecisionLevel.high,
        status=ConsultationStatus.nominal,
        missing_fields=[],
        available_modes=["relationship_full"],
        blocking_reasons=[],
    )
    assert ConsultationFallbackService.resolve_route_key(data) == "relationship_full_full"


def test_resolve_route_key_relationship_user_only():
    data = ConsultationPrecheckData(
        consultation_type="relationship",
        user_profile_quality="complete",
        precision_level=PrecisionLevel.medium,
        status=ConsultationStatus.degraded,
        missing_fields=["other_person"],
        available_modes=["relationship_user_only"],
        fallback_mode=FallbackMode.relation_user_only,
        blocking_reasons=[],
    )
    assert ConsultationFallbackService.resolve_route_key(data) == "relationship_user_only"


def test_resolve_route_key_blocked():
    data = ConsultationPrecheckData(
        consultation_type="period",
        user_profile_quality="missing",
        precision_level=PrecisionLevel.blocked,
        status=ConsultationStatus.blocked,
        missing_fields=["user_birth_profile"],
        available_modes=[],
        blocking_reasons=["birth_profile_not_found"],
    )
    assert ConsultationFallbackService.resolve_route_key(data) is None
