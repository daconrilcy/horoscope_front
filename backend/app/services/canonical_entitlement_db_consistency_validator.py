from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.services.feature_scope_registry import FEATURE_SCOPE_REGISTRY, FeatureScope

logger = logging.getLogger(__name__)

_SCOPE_TO_AUDIENCE: dict[FeatureScope, Audience] = {
    FeatureScope.B2C: Audience.B2C,
    FeatureScope.B2B: Audience.B2B,
}
_MANDATORY_METERED_FEATURES = frozenset(
    {
        "astrologer_chat",
        "thematic_consultation",
        "natal_chart_long",
        "b2b_api_access",
    }
)


class CanonicalEntitlementDbConsistencyError(ValueError):
    """Exception levée si la DB entitlements est incohérente avec le registre."""


class CanonicalEntitlementDbConsistencyValidator:
    @staticmethod
    def validate(db: Session) -> None:
        errors: list[str] = []

        # Check 1 : registre → DB (présence active)
        feature_rows_by_code = {
            row.feature_code: row for row in db.query(FeatureCatalogModel).all()
        }
        for feature_code in FEATURE_SCOPE_REGISTRY:
            row = feature_rows_by_code.get(feature_code)
            if row is None:
                errors.append(f"feature_code '{feature_code}' absent de feature_catalog.")
            elif not row.is_active:
                errors.append(
                    f"feature_code '{feature_code}' présent dans feature_catalog "
                    "mais is_active=False."
                )

        bindings = db.query(PlanFeatureBindingModel).all()

        # Check 2 : DB → registre (features metered actives utilisées en quota)
        quota_feature_ids = {
            binding.feature_id for binding in bindings if binding.access_mode == AccessMode.QUOTA
        }
        for feature_id in quota_feature_ids:
            feature_row = db.get(FeatureCatalogModel, feature_id)
            if feature_row is None or not feature_row.is_active or not feature_row.is_metered:
                continue
            if feature_row.feature_code not in FEATURE_SCOPE_REGISTRY:
                errors.append(
                    f"feature_code '{feature_row.feature_code}' participe à un binding QUOTA "
                    "avec is_metered=True et is_active=True dans feature_catalog mais absent "
                    "de FEATURE_SCOPE_REGISTRY."
                )

        # Check 3 : DB → registre (features dans les bindings)
        for binding in bindings:
            feature_row = db.get(FeatureCatalogModel, binding.feature_id)
            if feature_row is None:
                continue
            if feature_row.feature_code not in FEATURE_SCOPE_REGISTRY:
                plan_row = db.get(PlanCatalogModel, binding.plan_id)
                pname = plan_row.plan_code if plan_row else f"plan_id={binding.plan_id}"
                errors.append(
                    f"feature_code '{feature_row.feature_code}' est utilisé dans "
                    f"plan_feature_bindings (plan='{pname}') mais absent de FEATURE_SCOPE_REGISTRY."
                )

        # Check 4 & 5 : scope B2C/B2B ↔ audience plan
        # Toute feature de scope B2C ne peut être bindée qu'à des plans plan_catalog.audience = B2C.
        # Toute feature de scope B2B ne peut être bindée qu'à des plans plan_catalog.audience = B2B.
        for binding in bindings:
            feature_row = db.get(FeatureCatalogModel, binding.feature_id)
            plan_row = db.get(PlanCatalogModel, binding.plan_id)
            if feature_row is None or plan_row is None:
                continue  # FK broken — not this validator's responsibility
            feature_code = feature_row.feature_code
            scope = FEATURE_SCOPE_REGISTRY.get(feature_code)
            if scope is None:
                continue  # Déjà signalé au check 3
            expected_audience = _SCOPE_TO_AUDIENCE.get(scope)
            if expected_audience is None:
                continue  # INTERNAL scope — no cross-check needed
            if plan_row.audience != expected_audience:
                errors.append(
                    f"Feature '{feature_code}' (scope {scope.value}) liée au plan "
                    f"'{plan_row.plan_code}' (audience={plan_row.audience.value}) : "
                    f"attendu audience={expected_audience.value}."
                )

        # Check 6 : QUOTA → au moins un quota
        # Tout binding access_mode = QUOTA possède au moins un PlanFeatureQuotaModel valide.
        quota_bindings = (
            db.query(PlanFeatureBindingModel).filter_by(access_mode=AccessMode.QUOTA).all()
        )
        for binding in quota_bindings:
            count = (
                db.query(PlanFeatureQuotaModel)
                .filter_by(plan_feature_binding_id=binding.id)
                .count()
            )
            if count == 0:
                feature_row = db.get(FeatureCatalogModel, binding.feature_id)
                plan_row = db.get(PlanCatalogModel, binding.plan_id)
                fname = (
                    feature_row.feature_code if feature_row else f"feature_id={binding.feature_id}"
                )
                pname = plan_row.plan_code if plan_row else f"plan_id={binding.plan_id}"
                errors.append(
                    f"Binding QUOTA feature='{fname}' plan='{pname}' "
                    "n'a aucun quota dans plan_feature_quotas."
                )

        # Check 7 : UNLIMITED/DISABLED → aucun quota parasite
        # Aucun binding access_mode = UNLIMITED ou DISABLED ne possède de quota associé.
        non_quota_bindings = (
            db.query(PlanFeatureBindingModel)
            .filter(
                PlanFeatureBindingModel.access_mode.in_([AccessMode.UNLIMITED, AccessMode.DISABLED])
            )
            .all()
        )
        for binding in non_quota_bindings:
            count = (
                db.query(PlanFeatureQuotaModel)
                .filter_by(plan_feature_binding_id=binding.id)
                .count()
            )
            if count > 0:
                feature_row = db.get(FeatureCatalogModel, binding.feature_id)
                plan_row = db.get(PlanCatalogModel, binding.plan_id)
                fname = (
                    feature_row.feature_code if feature_row else f"feature_id={binding.feature_id}"
                )
                pname = plan_row.plan_code if plan_row else f"plan_id={binding.plan_id}"
                errors.append(
                    f"Binding {binding.access_mode.value.upper()} feature='{fname}' "
                    f"plan='{pname}' a {count} quota(s) parasite(s)."
                )

        # Check 12 : features quota connues du registre
        for feature_code in _MANDATORY_METERED_FEATURES:
            row = feature_rows_by_code.get(feature_code)
            if row is None or not row.is_active:
                continue
            if not row.is_metered:
                errors.append(f"Mandatory feature '{feature_code}' doit être is_metered=True.")

        if errors:
            raise CanonicalEntitlementDbConsistencyError(
                "Canonical entitlement DB inconsistencies detected:\n"
                + "\n".join(f"  {i + 1}. {e}" for i, e in enumerate(errors))
            )
