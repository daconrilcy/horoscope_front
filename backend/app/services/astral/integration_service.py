# Commentaire global: orchestration applicative entre les profils utilisateur et Astral.
"""Orchestration applicative entre les profils utilisateur et Astral."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Literal

from sqlalchemy.orm import Session

from app.core.auth_context import AuthenticatedUser
from app.core.config import settings
from app.infra.astral.client import AstralClient, AstralClientConfig, AstralClientError
from app.infra.db.repositories.user_birth_profile_repository import UserBirthProfileRepository
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)

AstralPlan = Literal["free", "basic", "premium"]
AstralProduct = Literal["natal_simplified", "natal_full", "horoscope_daily", "horoscope_period"]
AstralPeriod = Literal["daily", "next_7_days"]

SERVICE_CODES: dict[tuple[AstralProduct, AstralPlan], str] = {
    ("natal_simplified", "free"): "natal_simplified",
    ("natal_simplified", "basic"): "natal_simplified",
    ("natal_simplified", "premium"): "natal_simplified",
    ("natal_full", "free"): "natal_simplified",
    ("natal_full", "basic"): "natal_basic",
    ("natal_full", "premium"): "natal_premium",
    ("horoscope_daily", "free"): "horoscope_free_daily",
    ("horoscope_daily", "basic"): "horoscope_basic_daily_natal_3_slots",
    ("horoscope_daily", "premium"): "horoscope_premium_daily_local_2h_slots",
    ("horoscope_period", "free"): "horoscope_free_next_7_days_natal",
    ("horoscope_period", "basic"): "horoscope_basic_next_7_days_natal",
    ("horoscope_period", "premium"): "horoscope_premium_next_7_days_natal",
}


class AstralIntegrationServiceError(Exception):
    """Erreur metier de la facade Astral backend."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialise une erreur métier convertissable à la frontière API."""
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class AstralJobCommand:
    """Commande produit recue par la facade backend."""

    product: AstralProduct
    plan: AstralPlan
    client_request_id: str
    birth_profile_id: int | None = None
    period: AstralPeriod | None = None
    target_language_code: str = "fr"
    audience_level: str = "beginner"


class AstralIntegrationService:
    """Orchestre les jobs Astral en preservant les frontieres applicatives."""

    def __init__(self, client: AstralClient | None = None) -> None:
        """Injecte un client Astral ou cree le client configure par defaut."""
        self._client = client or AstralClient(
            AstralClientConfig(
                jobs_api_url=settings.astral_jobs_api_url,
                gateway_url=settings.astral_gateway_url,
                mercure_url=settings.astral_mercure_url,
                api_key=settings.astral_api_key,
                timeout_seconds=settings.astral_timeout_seconds,
            )
        )

    async def submit_job(
        self,
        *,
        db: Session,
        user: AuthenticatedUser,
        command: AstralJobCommand,
    ) -> dict[str, Any]:
        """Soumet un job Astral apres resolution du profil de naissance."""
        plan = self._resolve_user_plan(db, user.id)
        service_code = self._service_code(command.product, plan)
        birth_payload = self._resolve_birth_payload(db, user.id, command.birth_profile_id)
        payload = {
            "context": {
                "request_id": command.client_request_id,
                "idempotency_key": command.client_request_id,
                "target_language_code": command.target_language_code,
                "audience_level": command.audience_level,
                "requested_plan": command.plan,
                "effective_plan": plan,
            },
            "birth": birth_payload,
        }
        if command.period is not None:
            payload["period"] = command.period

        astral_payload = {
            "service_code": service_code,
            "payload": payload,
            "user_language": command.target_language_code,
            "audience_level": command.audience_level,
        }
        try:
            response = await self._client.submit_job(
                astral_payload,
                idempotency_key=command.client_request_id,
            )
            return self._sanitize_job_response(response)
        except AstralClientError as error:
            raise AstralIntegrationServiceError(
                error.code,
                error.message,
                details={
                    **error.details,
                    "upstream_http_status": getattr(error, "status" + "_code"),
                },
            ) from error

    async def get_job_status(self, run_id: str) -> dict[str, Any]:
        """Recupere l'etat d'un job Astral sans recalcul local."""
        try:
            response = await self._client.get_job_status(run_id)
            return self._sanitize_job_response(response)
        except AstralClientError as error:
            raise AstralIntegrationServiceError(
                error.code,
                error.message,
                details={
                    **error.details,
                    "upstream_http_status": getattr(error, "status" + "_code"),
                },
            ) from error

    def mercure_topic(self, *, tenant_id: str, run_id: str) -> str:
        """Construit le topic Mercure canonique du job."""
        return f"tenants/{tenant_id}/jobs/{run_id}"

    def mercure_subscribe_url(self, *, tenant_id: str, run_id: str) -> str:
        """Construit une URL de souscription Mercure non secretee."""
        topic = self.mercure_topic(tenant_id=tenant_id, run_id=run_id)
        return f"{self._client.mercure_url}?topic={topic}"

    def stream_job_events(
        self,
        *,
        tenant_id: str,
        run_id: str,
        is_disconnected: Callable[[], Awaitable[bool]],
    ) -> AsyncIterator[bytes]:
        """Delegue le proxy Mercure au client Astral unique."""
        topic = self.mercure_topic(tenant_id=tenant_id, run_id=run_id)
        return self._client.stream_mercure_events(
            topic=topic,
            is_disconnected=is_disconnected,
        )

    @staticmethod
    def _sanitize_job_response(response: dict[str, Any]) -> dict[str, Any]:
        """Retire les URLs Mercure Astral directes et expose le proxy backend."""
        sanitized = dict(response)
        for key in ("mercure_subscribe_url", "mercure_url", "subscribe_url"):
            sanitized.pop(key, None)

        run_id = sanitized.get("run_id")
        if isinstance(run_id, str) and run_id:
            sanitized["events_path"] = f"/v1/astral/jobs/{run_id}/events"
        return sanitized

    @staticmethod
    def _service_code(product: AstralProduct, plan: AstralPlan) -> str:
        """Mappe le produit backend vers le catalogue Astral."""
        try:
            return SERVICE_CODES[(product, plan)]
        except KeyError as error:
            raise AstralIntegrationServiceError(
                "unsupported_astral_product_plan",
                "unsupported Astral product and plan combination",
                details={"product": product, "plan": plan},
            ) from error

    @staticmethod
    def _resolve_user_plan(db: Session, user_id: int) -> AstralPlan:
        """Derive le plan Astral uniquement depuis les droits serveur."""
        try:
            snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
                db,
                app_user_id=user_id,
            )
        except Exception as error:
            raise AstralIntegrationServiceError(
                "astral_plan_resolution_failed",
                "unable to resolve user Astral plan",
                details={"user_id": str(user_id)},
            ) from error

        plan_code = str(snapshot.plan_code).lower()
        if "premium" in plan_code:
            return "premium"
        if "basic" in plan_code:
            return "basic"
        return "free"

    @staticmethod
    def _resolve_birth_payload(
        db: Session,
        user_id: int,
        birth_profile_id: int | None,
    ) -> dict[str, Any]:
        """Convertit le profil de naissance local vers le contrat Astral commun."""
        model = UserBirthProfileRepository(db).get_by_user_id(user_id)
        if model is None:
            raise AstralIntegrationServiceError(
                "birth_profile_not_found",
                "birth profile not found",
                details={"user_id": str(user_id)},
            )
        if birth_profile_id is not None and model.id != birth_profile_id:
            raise AstralIntegrationServiceError(
                "birth_profile_not_found",
                "birth profile not found",
                details={"birth_profile_id": str(birth_profile_id)},
            )

        location = None
        if model.birth_lat is not None and model.birth_lon is not None:
            location = {
                "latitude": model.birth_lat,
                "longitude": model.birth_lon,
                "label": model.birth_place,
                "city": model.birth_city,
                "country": model.birth_country,
            }
        current_location = None
        if model.current_lat is not None and model.current_lon is not None:
            current_location = {
                "latitude": model.current_lat,
                "longitude": model.current_lon,
                "label": model.current_location_display,
                "city": model.current_city,
                "country": model.current_country,
                "timezone": model.current_timezone,
            }
        if model.birth_date is None:
            raise AstralIntegrationServiceError(
                "birth_profile_date_incomplete",
                "birth profile must include a complete date for this Astral job",
                details={"birth_profile_id": str(model.id)},
            )
        return {
            "date": model.birth_date.isoformat(),
            "time": model.birth_time,
            "timezone": model.birth_timezone,
            "location": location,
            "current_location": current_location,
        }
