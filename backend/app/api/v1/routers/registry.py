"""Registre canonique des routeurs HTTP API v1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from fastapi import APIRouter, FastAPI

from app.api.v1.routers.admin.audit import router as admin_audit_router
from app.api.v1.routers.admin.content import router as admin_content_router
from app.api.v1.routers.admin.dashboard import router as admin_dashboard_router
from app.api.v1.routers.admin.entitlements import router as admin_entitlements_router
from app.api.v1.routers.admin.exports import router as admin_exports_router
from app.api.v1.routers.admin.logs import router as admin_logs_router
from app.api.v1.routers.admin.support import router as admin_support_router
from app.api.v1.routers.admin.users import router as admin_users_router
from app.api.v1.routers.b2b.billing import router as b2b_billing_router
from app.api.v1.routers.b2b.credentials import router as enterprise_credentials_router
from app.api.v1.routers.b2b.usage import router as b2b_usage_router
from app.api.v1.routers.ops.b2b.entitlement_repair import (
    router as b2b_entitlement_repair_router,
)
from app.api.v1.routers.ops.b2b.entitlements_audit import (
    router as b2b_entitlements_audit_router,
)
from app.api.v1.routers.ops.b2b.reconciliation import router as b2b_reconciliation_router
from app.api.v1.routers.ops.entitlement_mutation_audits import (
    router as ops_entitlement_mutation_audits_router,
)
from app.api.v1.routers.ops.feature_flags import router as ops_feature_flags_router
from app.api.v1.routers.ops.monitoring import router as ops_monitoring_router
from app.api.v1.routers.public.astral import router as astral_router
from app.api.v1.routers.public.audit import router as audit_router
from app.api.v1.routers.public.auth import router as auth_router
from app.api.v1.routers.public.billing import router as billing_router
from app.api.v1.routers.public.entitlements import router as entitlements_router
from app.api.v1.routers.public.geocoding import router as geocoding_router
from app.api.v1.routers.public.help import router as help_router
from app.api.v1.routers.public.privacy import router as privacy_router
from app.api.v1.routers.public.reference_data import router as reference_data_router
from app.api.v1.routers.public.support import router as support_router
from app.api.v1.routers.public.users import router as users_router


@dataclass(frozen=True)
class RouterRegistration:
    """Décrit l'enregistrement FastAPI explicite d'un routeur API v1."""

    router: APIRouter
    prefix: str | None = None
    tags: Sequence[str] | None = None


API_V1_ROUTER_REGISTRY: tuple[RouterRegistration, ...] = (
    RouterRegistration(admin_dashboard_router),
    RouterRegistration(admin_entitlements_router),
    RouterRegistration(admin_logs_router),
    RouterRegistration(admin_exports_router),
    RouterRegistration(admin_users_router),
    RouterRegistration(admin_support_router),
    RouterRegistration(admin_audit_router),
    RouterRegistration(admin_content_router),
    RouterRegistration(auth_router),
    RouterRegistration(audit_router),
    RouterRegistration(billing_router),
    RouterRegistration(entitlements_router),
    RouterRegistration(astral_router),
    RouterRegistration(b2b_billing_router),
    RouterRegistration(b2b_reconciliation_router),
    RouterRegistration(b2b_usage_router),
    RouterRegistration(b2b_entitlement_repair_router),
    RouterRegistration(b2b_entitlements_audit_router),
    RouterRegistration(geocoding_router),
    RouterRegistration(enterprise_credentials_router),
    RouterRegistration(ops_monitoring_router),
    RouterRegistration(ops_feature_flags_router),
    RouterRegistration(ops_entitlement_mutation_audits_router),
    RouterRegistration(privacy_router),
    RouterRegistration(reference_data_router),
    RouterRegistration(users_router),
    RouterRegistration(support_router),
    RouterRegistration(help_router),
)


def include_api_v1_routers(application: FastAPI) -> None:
    """Monte tous les routeurs API v1 depuis l'inventaire canonique."""
    for registration in API_V1_ROUTER_REGISTRY:
        kwargs: dict[str, object] = {}
        if registration.prefix is not None:
            kwargs["prefix"] = registration.prefix
        if registration.tags is not None:
            kwargs["tags"] = list(registration.tags)
        application.include_router(registration.router, **kwargs)
