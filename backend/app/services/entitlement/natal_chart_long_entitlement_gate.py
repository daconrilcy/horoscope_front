"""Gate entitlement canonique pour l'acces natal long cote runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.entitlement.b2c_runtime_gate import (
    consume_b2c_quota,
    resolve_b2c_access,
    resolve_b2c_entitlement_snapshot,
)
from app.services.entitlement.entitlement_types import UsageState


class NatalChartLongAccessDeniedError(Exception):
    def __init__(
        self,
        reason: str,
        billing_status: str,
        plan_code: str,
        reason_code: str | None = None,
    ) -> None:
        self.reason = reason
        self.reason_code = reason_code or reason
        self.billing_status = billing_status
        self.plan_code = plan_code
        super().__init__(f"Natal chart long access denied: {reason}")


class NatalChartLongQuotaExceededError(Exception):
    def __init__(self, quota_key: str, used: int, limit: int, window_end: datetime | None) -> None:
        self.quota_key = quota_key
        self.used = used
        self.limit = limit
        self.window_end = window_end
        super().__init__(f"Natal chart long quota '{quota_key}' exceeded: {used}/{limit}")


@dataclass
class NatalChartLongEntitlementResult:
    path: str  # "canonical_quota" | "canonical_unlimited" | "corrective_regeneration"
    variant_code: str | None  # "single_astrologer" | "multi_astrologer" | None
    usage_states: list[UsageState] = field(default_factory=list)
    corrective_regeneration: bool = False
    corrective_interpretation_id: int | None = None
    corrective_original_use_case: str | None = None


class NatalChartLongEntitlementGate:
    FEATURE_CODE = "natal_chart_long"

    @staticmethod
    def check_access(db: Session, *, user_id: int) -> NatalChartLongEntitlementResult:
        """Verifie l acces natal long sans consommer de quota."""
        access_snapshot = resolve_b2c_access(
            db,
            user_id=user_id,
            feature_code=NatalChartLongEntitlementGate.FEATURE_CODE,
            denied_error_factory=NatalChartLongAccessDeniedError,
            quota_error_factory=NatalChartLongQuotaExceededError,
        )
        return NatalChartLongEntitlementResult(
            path=access_snapshot.path,
            variant_code=access_snapshot.variant_code,
            usage_states=access_snapshot.usage_states,
        )

    @staticmethod
    def check_and_consume(db: Session, *, user_id: int) -> NatalChartLongEntitlementResult:
        """Verifie puis consomme les quotas natal long applicables."""
        result = NatalChartLongEntitlementGate.check_access(db, user_id=user_id)
        return NatalChartLongEntitlementGate.consume_on_acceptance(
            db,
            user_id=user_id,
            access_result=result,
        )

    @staticmethod
    def check_access_for_complete_generation(
        db: Session,
        *,
        user_id: int,
    ) -> NatalChartLongEntitlementResult:
        """Verifie l'acces sans consommer; autorise une regeneration corrective idempotente."""
        try:
            return NatalChartLongEntitlementGate.check_access(db, user_id=user_id)
        except NatalChartLongQuotaExceededError as quota_error:
            from app.services.llm_generation.natal.interpretation_service import (
                NatalInterpretationService,
            )

            entitlement_snapshot = resolve_b2c_entitlement_snapshot(db, user_id=user_id)
            access = entitlement_snapshot.entitlements.get(
                NatalChartLongEntitlementGate.FEATURE_CODE
            )
            variant_code = access.variant_code if access else None
            corrective_claim = NatalInterpretationService.claim_corrective_regeneration_eligibility(
                db,
                user_id=user_id,
                variant_code=variant_code,
            )
            if corrective_claim is None:
                raise quota_error from None
            interpretation_id, original_use_case = corrective_claim
            return NatalChartLongEntitlementResult(
                path="corrective_regeneration",
                variant_code=variant_code,
                usage_states=[],
                corrective_regeneration=True,
                corrective_interpretation_id=interpretation_id,
                corrective_original_use_case=original_use_case,
            )

    @staticmethod
    def release_corrective_regeneration_claim(
        db: Session,
        *,
        access_result: NatalChartLongEntitlementResult | None,
    ) -> None:
        """Libere une reservation corrective apres rejet ou erreur de generation."""
        if (
            access_result is None
            or access_result.corrective_interpretation_id is None
            or access_result.corrective_original_use_case is None
        ):
            return
        from app.services.llm_generation.natal.interpretation_service import (
            NatalInterpretationService,
        )

        NatalInterpretationService.release_corrective_regeneration_claim(
            db,
            interpretation_id=access_result.corrective_interpretation_id,
            original_use_case=access_result.corrective_original_use_case,
        )

    @staticmethod
    def consume_on_acceptance(
        db: Session,
        *,
        user_id: int,
        access_result: NatalChartLongEntitlementResult,
    ) -> NatalChartLongEntitlementResult:
        """Consomme le quota uniquement apres acceptation d'une lecture complete valide."""
        if access_result.corrective_regeneration or access_result.path == "corrective_regeneration":
            return access_result
        if access_result.path == "canonical_unlimited":
            return access_result

        consumed_states = consume_b2c_quota(
            db,
            user_id=user_id,
            feature_code=NatalChartLongEntitlementGate.FEATURE_CODE,
            usage_states=access_result.usage_states,
            quota_error_factory=NatalChartLongQuotaExceededError,
        )

        return NatalChartLongEntitlementResult(
            path="canonical_quota",
            variant_code=access_result.variant_code,
            usage_states=consumed_states,
            corrective_regeneration=access_result.corrective_regeneration,
        )
