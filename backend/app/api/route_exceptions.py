"""Registre explicite des routes montees hors registre API v1 canonique."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, FastAPI


@dataclass(frozen=True)
class RouteMountException:
    """Decrit une exception de montage runtime volontaire et auditable."""

    key: str
    route_path: str
    methods: tuple[str, ...]
    router_module: str
    endpoint_module: str
    reason: str
    decision: str
    condition: str
    include_prefix: str | None = None
    tags: tuple[str, ...] = ()


API_ROUTE_MOUNT_EXCEPTIONS: tuple[RouteMountException, ...] = (
    RouteMountException(
        key="health",
        route_path="/health",
        methods=("GET",),
        router_module="app.api.health",
        endpoint_module="app.api.health",
        reason="Route de sante applicative hors API v1 montee au bootstrap.",
        decision="Exception permanente de bootstrap.",
        condition="always",
    ),
    RouteMountException(
        key="public_email_unsubscribe",
        route_path="/api/email/unsubscribe",
        methods=("GET",),
        router_module="app.api.v1.routers.public.email",
        endpoint_module="app.api.v1.routers.public.email",
        reason="URL publique historique active de desabonnement email hors prefixe /v1.",
        decision=(
            "Decision needs-user-decision: route external-active conservee sans changement "
            "runtime en attente d une decision explicite de permanence, migration ou retrait."
        ),
        condition="always",
        include_prefix="/api",
        tags=("email",),
    ),
)


def _include_router(
    application: FastAPI,
    router: APIRouter,
    exception: RouteMountException,
) -> None:
    """Monte un routeur en appliquant uniquement les metadonnees du registre."""
    kwargs: dict[str, object] = {}
    if exception.include_prefix is not None:
        kwargs["prefix"] = exception.include_prefix
    if exception.tags:
        kwargs["tags"] = list(exception.tags)
    application.include_router(router, **kwargs)


def include_registered_route_exceptions(application: FastAPI) -> None:
    """Monte les exceptions runtime hors registre API v1 depuis un registre unique."""
    from app.api.health import router as health_router
    from app.api.v1.routers.public.email import router as email_router

    exceptions = {exception.key: exception for exception in API_ROUTE_MOUNT_EXCEPTIONS}
    _include_router(application, health_router, exceptions["health"])
    _include_router(application, email_router, exceptions["public_email_unsubscribe"])
