from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.infra.db.models.user import UserModel
from app.services.b2b_canonical_plan_resolver import resolve_b2b_canonical_plan
from app.services.billing_service import BillingService
from app.services.enterprise_quota_usage_service import EnterpriseQuotaUsageService
from app.services.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    QuotaDefinition,
    UsageState,
)
from app.services.feature_scope_registry import FEATURE_SCOPE_REGISTRY, FeatureScope
from app.services.quota_usage_service import QuotaUsageService


class EffectiveEntitlementResolverService:
    """
    Service de résolution canonique des droits effectifs.
    Produit un snapshot complet (lecture seule) des droits pour un sujet B2C ou B2B.
    """

    REASON_GRANTED = "granted"
    REASON_FEATURE_NOT_IN_PLAN = "feature_not_in_plan"
    REASON_BILLING_INACTIVE = "billing_inactive"
    REASON_QUOTA_EXHAUSTED = "quota_exhausted"
    REASON_BINDING_DISABLED = "binding_disabled"
    REASON_SUBJECT_NOT_ELIGIBLE = "subject_not_eligible"
    _ACTIVE_BILLING_STATUSES = frozenset({"active", "trialing", "past_due"})

    @staticmethod
    def resolve_b2c_user_snapshot(
        db: Session, *, app_user_id: int
    ) -> EffectiveEntitlementsSnapshot:
        """Résout un snapshot complet pour un utilisateur B2C."""
        # 1. Validation éligibilité (existence utilisateur)
        user = db.get(UserModel, app_user_id)
        if not user:
            features = [
                f_code
                for f_code, scope in FEATURE_SCOPE_REGISTRY.items()
                if scope == FeatureScope.B2C
            ]
            entitlements = {
                f_code: EffectiveFeatureAccess(
                    granted=False,
                    reason_code=EffectiveEntitlementResolverService.REASON_SUBJECT_NOT_ELIGIBLE,
                    access_mode=None,
                    variant_code=None,
                    quota_limit=None,
                    quota_used=None,
                    quota_remaining=None,
                    period_unit=None,
                    period_value=None,
                    reset_mode=None,
                )
                for f_code in features
            }
            return EffectiveEntitlementsSnapshot(
                subject_type="b2c_user",
                subject_id=app_user_id,
                plan_code="none",
                billing_status="none",
                entitlements=entitlements,
            )

        # 2. Résolution billing/plan
        sub = BillingService.get_subscription_status_readonly(db, user_id=app_user_id)
        plan_code = BillingService.resolve_runtime_plan_code(sub)
        billing_status = BillingService.resolve_runtime_billing_status(sub)

        # 3. Chargement du plan canonique
        canonical_plan = None
        if plan_code != "none":
            for candidate_plan_code in BillingService.get_plan_lookup_codes(plan_code):
                canonical_plan = db.scalar(
                    select(PlanCatalogModel)
                    .where(
                        PlanCatalogModel.plan_code == candidate_plan_code,
                        PlanCatalogModel.audience == Audience.B2C,
                        PlanCatalogModel.is_active,
                    )
                    .limit(1)
                )
                if canonical_plan is not None:
                    break

        # 4. Features du scope B2C
        features = [
            f_code for f_code, scope in FEATURE_SCOPE_REGISTRY.items() if scope == FeatureScope.B2C
        ]

        # 5. Résolution globale
        return EffectiveEntitlementResolverService._resolve_snapshot(
            db,
            subject_type="b2c_user",
            subject_id=app_user_id,
            plan_code=plan_code,
            billing_status=billing_status,
            canonical_plan=canonical_plan,
            features=features,
            scope=FeatureScope.B2C,
        )

    @staticmethod
    def resolve_b2b_account_snapshot(
        db: Session, *, enterprise_account_id: int
    ) -> EffectiveEntitlementsSnapshot:
        """Résout un snapshot complet pour un compte B2B."""
        # 1. Chargement compte
        account = db.get(EnterpriseAccountModel, enterprise_account_id)
        if not account or account.status != "active":
            features = [
                f_code
                for f_code, scope in FEATURE_SCOPE_REGISTRY.items()
                if scope == FeatureScope.B2B
            ]
            entitlements = {
                f_code: EffectiveFeatureAccess(
                    granted=False,
                    reason_code=EffectiveEntitlementResolverService.REASON_SUBJECT_NOT_ELIGIBLE,
                    access_mode=None,
                    variant_code=None,
                    quota_limit=None,
                    quota_used=None,
                    quota_remaining=None,
                    period_unit=None,
                    period_value=None,
                    reset_mode=None,
                )
                for f_code in features
            }
            return EffectiveEntitlementsSnapshot(
                subject_type="b2b_account",
                subject_id=enterprise_account_id,
                plan_code="none",
                billing_status="none",
                entitlements=entitlements,
            )

        # 2. Résolution plan canonique
        canonical_plan = resolve_b2b_canonical_plan(db, enterprise_account_id)
        plan_code = canonical_plan.plan_code if canonical_plan else "none"
        billing_status = "active"  # Pour B2B actif, on considère le billing OK pour le snapshot

        # 3. Features du scope B2B
        features = [
            f_code for f_code, scope in FEATURE_SCOPE_REGISTRY.items() if scope == FeatureScope.B2B
        ]

        # 4. Résolution globale
        return EffectiveEntitlementResolverService._resolve_snapshot(
            db,
            subject_type="b2b_account",
            subject_id=enterprise_account_id,
            plan_code=plan_code,
            billing_status=billing_status,
            canonical_plan=canonical_plan,
            features=features,
            scope=FeatureScope.B2B,
        )

    @staticmethod
    def _resolve_snapshot(
        db: Session,
        *,
        subject_type: str,
        subject_id: int,
        plan_code: str,
        billing_status: str,
        canonical_plan: PlanCatalogModel | None,
        features: list[str],
        scope: FeatureScope,
    ) -> EffectiveEntitlementsSnapshot:
        """Logique de résolution partagée."""
        entitlements: dict[str, EffectiveFeatureAccess] = {}

        # Chargement en lot des bindings si plan présent
        bindings_map: dict[str, PlanFeatureBindingModel] = {}
        if canonical_plan:
            stmt = (
                select(PlanFeatureBindingModel, FeatureCatalogModel.feature_code)
                .join(FeatureCatalogModel)
                .where(
                    PlanFeatureBindingModel.plan_id == canonical_plan.id,
                    FeatureCatalogModel.feature_code.in_(features),
                )
            )
            for b, f_code in db.execute(stmt):
                bindings_map[f_code] = b

        ref_dt = datetime.now(timezone.utc)

        for f_code in features:
            binding = bindings_map.get(f_code)

            if not binding:
                entitlements[f_code] = EffectiveFeatureAccess(
                    granted=False,
                    reason_code=EffectiveEntitlementResolverService.REASON_FEATURE_NOT_IN_PLAN,
                    access_mode=None,
                    variant_code=None,
                    quota_limit=None,
                    quota_used=None,
                    quota_remaining=None,
                    period_unit=None,
                    period_value=None,
                    reset_mode=None,
                )
                continue

            # Binding présent
            if not binding.is_enabled or binding.access_mode == AccessMode.DISABLED:
                entitlements[f_code] = EffectiveFeatureAccess(
                    granted=False,
                    reason_code=EffectiveEntitlementResolverService.REASON_BINDING_DISABLED,
                    access_mode="disabled",
                    variant_code=binding.variant_code,
                    quota_limit=None,
                    quota_used=None,
                    quota_remaining=None,
                    period_unit=None,
                    period_value=None,
                    reset_mode=None,
                )
                continue

            if not EffectiveEntitlementResolverService._is_billing_active(
                subject_type=subject_type,
                billing_status=billing_status,
            ):
                entitlements[f_code] = EffectiveFeatureAccess(
                    granted=False,
                    reason_code=EffectiveEntitlementResolverService.REASON_BILLING_INACTIVE,
                    access_mode=binding.access_mode.value,
                    variant_code=binding.variant_code,
                    quota_limit=None,
                    quota_used=None,
                    quota_remaining=None,
                    period_unit=None,
                    period_value=None,
                    reset_mode=None,
                )
                continue

            if binding.access_mode == AccessMode.UNLIMITED:
                entitlements[f_code] = EffectiveFeatureAccess(
                    granted=True,
                    reason_code=EffectiveEntitlementResolverService.REASON_GRANTED,
                    access_mode="unlimited",
                    variant_code=binding.variant_code,
                    quota_limit=None,
                    quota_used=None,
                    quota_remaining=None,
                    period_unit=None,
                    period_value=None,
                    reset_mode=None,
                )
                continue

            # Cas QUOTA
            quotas = db.scalars(
                select(PlanFeatureQuotaModel).where(
                    PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
                )
            ).all()

            if not quotas or any(q.reset_mode.value == "rolling" for q in quotas):
                entitlements[f_code] = EffectiveFeatureAccess(
                    granted=False,
                    reason_code=EffectiveEntitlementResolverService.REASON_BINDING_DISABLED,
                    access_mode="quota",
                    variant_code=binding.variant_code,
                    quota_limit=None,
                    quota_used=None,
                    quota_remaining=None,
                    period_unit=None,
                    period_value=None,
                    reset_mode=None,
                )
                continue

            usage_states: list[UsageState] = []
            for q in quotas:
                q_def = QuotaDefinition(
                    quota_key=q.quota_key,
                    quota_limit=q.quota_limit,
                    period_unit=q.period_unit.value,
                    period_value=q.period_value,
                    reset_mode=q.reset_mode.value,
                )
                if scope == FeatureScope.B2C:
                    usage = QuotaUsageService.get_usage(
                        db,
                        user_id=subject_id,
                        feature_code=f_code,
                        quota=q_def,
                        ref_dt=ref_dt,
                    )
                else:
                    usage = EnterpriseQuotaUsageService.get_usage(
                        db,
                        account_id=subject_id,
                        feature_code=f_code,
                        quota=q_def,
                        ref_dt=ref_dt,
                    )
                usage_states.append(usage)

            # Synthèse
            summary = EffectiveEntitlementResolverService._summarize_usage(usage_states)
            granted = not summary["exhausted"]
            reason_code = (
                EffectiveEntitlementResolverService.REASON_GRANTED
                if granted
                else EffectiveEntitlementResolverService.REASON_QUOTA_EXHAUSTED
            )

            entitlements[f_code] = EffectiveFeatureAccess(
                granted=granted,
                reason_code=reason_code,
                access_mode="quota",
                variant_code=binding.variant_code,
                quota_limit=summary["quota_limit"],
                quota_used=summary["used"],
                quota_remaining=summary["remaining"],
                period_unit=summary["period_unit"],
                period_value=summary["period_value"],
                reset_mode=summary["reset_mode"],
                usage_states=usage_states,
            )

        return EffectiveEntitlementsSnapshot(
            subject_type=subject_type,
            subject_id=subject_id,
            plan_code=plan_code,
            billing_status=billing_status,
            entitlements=entitlements,
        )

    @staticmethod
    def _is_billing_active(*, subject_type: str, billing_status: str) -> bool:
        if subject_type == "b2c_user":
            return billing_status in EffectiveEntitlementResolverService._ACTIVE_BILLING_STATUSES
        return billing_status == "active"

    @staticmethod
    def _summarize_usage(usage_states: list[UsageState]) -> dict[str, Any]:
        """Synthèse déterministe de plusieurs quotas."""
        if not usage_states:
            return {
                "exhausted": False,
                "quota_limit": None,
                "used": None,
                "remaining": None,
                "period_unit": None,
                "period_value": None,
                "reset_mode": None,
            }

        # 1. Si au moins un épuisé, premier épuisé par ordre déterministe
        exhausted_states = [u for u in usage_states if u.exhausted]
        if exhausted_states:
            selected = sorted(
                exhausted_states,
                key=lambda u: (u.quota_key, u.period_unit, u.period_value),
            )[0]
            return {
                "exhausted": True,
                "quota_limit": selected.quota_limit,
                "used": selected.used,
                "remaining": selected.remaining,
                "period_unit": selected.period_unit,
                "period_value": selected.period_value,
                "reset_mode": selected.reset_mode,
            }

        # 2. Sinon, celui avec remaining minimal
        selected = sorted(
            usage_states,
            key=lambda u: (u.remaining, u.quota_key, u.period_unit, u.period_value),
        )[0]
        return {
            "exhausted": False,
            "quota_limit": selected.quota_limit,
            "used": selected.used,
            "remaining": selected.remaining,
            "period_unit": selected.period_unit,
            "period_value": selected.period_value,
            "reset_mode": selected.reset_mode,
        }
