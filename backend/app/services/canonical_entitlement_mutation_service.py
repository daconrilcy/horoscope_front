from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    SourceOrigin,
)
from app.services.feature_scope_registry import (
    FeatureScope,
    UnknownFeatureCodeError,
    get_feature_scope,
)

logger = logging.getLogger(__name__)

_SCOPE_TO_AUDIENCE: dict[FeatureScope, Audience] = {
    FeatureScope.B2C: Audience.B2C,
    FeatureScope.B2B: Audience.B2B,
}


class CanonicalMutationValidationError(ValueError):
    """Exception levée si une mutation canonique viole les invariants.

    Agrège toutes les violations détectées.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(
            "Canonical mutation validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )


class CanonicalEntitlementMutationService:
    @staticmethod
    def upsert_plan_feature_configuration(
        db: Session,
        plan: PlanCatalogModel,
        feature_code: str,
        *,
        is_enabled: bool,
        access_mode: AccessMode,
        variant_code: str | None = None,
        quotas: list[dict],
        source_origin: SourceOrigin,
    ) -> PlanFeatureBindingModel:
        """Crée ou met à jour un binding plan↔feature + remplace ses quotas.

        Valide les invariants canoniques avant toute écriture.
        Lève CanonicalMutationValidationError si une règle est violée.
        Pas de db.commit() — l'appelant contrôle la transaction.
        """
        # 1. Récupérer la feature du catalog (peut être None — géré dans _validate)
        feature = db.scalar(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == feature_code)
        )

        # 2. Valider — lève si erreurs
        errors = CanonicalEntitlementMutationService._validate(
            feature_code=feature_code,
            plan_audience=plan.audience,
            access_mode=access_mode,
            is_enabled=is_enabled,
            quotas=quotas,
            feature_row=feature,
        )
        if errors:
            raise CanonicalMutationValidationError(errors)

        # 3. Upsert binding
        # feature est forcément non None ici car _validate a levé sinon
        assert feature is not None

        binding = db.scalar(
            select(PlanFeatureBindingModel).where(
                PlanFeatureBindingModel.plan_id == plan.id,
                PlanFeatureBindingModel.feature_id == feature.id,
            )
        )
        if binding is None:
            binding = PlanFeatureBindingModel(
                plan_id=plan.id,
                feature_id=feature.id,
                is_enabled=is_enabled,
                access_mode=access_mode,
                variant_code=variant_code,
                source_origin=source_origin,
            )
            db.add(binding)
        else:
            binding.is_enabled = is_enabled
            binding.access_mode = access_mode
            binding.variant_code = variant_code
            binding.source_origin = source_origin
        db.flush()

        # 4. Remplacer les quotas atomiquement (helper privé)
        CanonicalEntitlementMutationService._replace_plan_feature_quotas(
            db, binding, quotas, source_origin=source_origin
        )
        return binding

    @staticmethod
    def _replace_plan_feature_quotas(
        db: Session,
        binding: PlanFeatureBindingModel,
        quotas: list[dict],
        *,
        source_origin: SourceOrigin,
    ) -> None:
        """Remplace atomiquement les quotas d'un binding — USAGE INTERNE UNIQUEMENT."""
        existing = db.scalars(
            select(PlanFeatureQuotaModel).where(
                PlanFeatureQuotaModel.plan_feature_binding_id == binding.id
            )
        ).all()

        desired_keys = {
            (q["quota_key"], q["period_unit"], q["period_value"], q["reset_mode"]) for q in quotas
        }

        # Supprimer les quotas devenus obsolètes
        for ex in existing:
            if (ex.quota_key, ex.period_unit, ex.period_value, ex.reset_mode) not in desired_keys:
                db.delete(ex)

        existing_map = {
            (ex.quota_key, ex.period_unit, ex.period_value, ex.reset_mode): ex for ex in existing
        }

        for q_data in quotas:
            key = (
                q_data["quota_key"],
                q_data["period_unit"],
                q_data["period_value"],
                q_data["reset_mode"],
            )
            if key not in existing_map:
                db.add(
                    PlanFeatureQuotaModel(
                        plan_feature_binding_id=binding.id,
                        source_origin=source_origin,
                        **q_data,
                    )
                )
            else:
                # Mettre à jour tous les champs mutables (pas seulement quota_limit)
                row = existing_map[key]
                row.quota_limit = q_data["quota_limit"]
                row.source_origin = source_origin
        db.flush()

    @staticmethod
    def _validate(
        feature_code: str,
        plan_audience: Audience,
        access_mode: AccessMode,
        is_enabled: bool,
        quotas: list[dict],
        feature_row: FeatureCatalogModel | None,
    ) -> list[str]:
        errors: list[str] = []

        # Check 1 : feature_code connu du registre (via l'API officielle)
        scope: FeatureScope | None = None
        try:
            scope = get_feature_scope(feature_code)
        except UnknownFeatureCodeError:
            errors.append(f"feature_code '{feature_code}' absent de FEATURE_SCOPE_REGISTRY.")

        # Check 2 : feature présente et active en DB
        if feature_row is None:
            errors.append(f"feature_code '{feature_code}' absent de feature_catalog.")
        elif not feature_row.is_active:
            errors.append(
                f"feature_code '{feature_code}' présent dans feature_catalog mais is_active=False."
            )

        # Check 3 : compatibilité scope ↔ audience (uniquement si scope connu)
        if scope is not None:
            expected_audience = _SCOPE_TO_AUDIENCE.get(scope)
            if expected_audience and plan_audience != expected_audience:
                errors.append(
                    f"feature '{feature_code}' de scope {scope.value.upper()} "
                    f"ne peut être bindée qu'à un plan {expected_audience.value.upper()}, "
                    f"reçu {plan_audience.value.upper()}."
                )

        # Check 4 : règles QUOTA / UNLIMITED / DISABLED + is_metered
        if access_mode == AccessMode.QUOTA:
            if not quotas:
                errors.append(
                    f"access_mode=QUOTA pour '{feature_code}' requiert au moins un quota."
                )
            if feature_row is not None and not feature_row.is_metered:
                errors.append(
                    f"access_mode=QUOTA pour '{feature_code}' "
                    "requiert is_metered=True dans feature_catalog."
                )
        elif access_mode in (AccessMode.UNLIMITED, AccessMode.DISABLED):
            if quotas:
                errors.append(
                    f"access_mode={access_mode.value.upper()} pour '{feature_code}' "
                    "ne doit pas avoir de quotas."
                )

        # Check 5 : normalisation is_enabled ↔ access_mode
        if access_mode == AccessMode.DISABLED and is_enabled:
            errors.append(f"access_mode=DISABLED pour '{feature_code}' requiert is_enabled=False.")
        elif access_mode in (AccessMode.QUOTA, AccessMode.UNLIMITED) and not is_enabled:
            errors.append(
                f"access_mode={access_mode.value.upper()} "
                f"pour '{feature_code}' requiert is_enabled=True."
            )

        return errors
