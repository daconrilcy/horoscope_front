# Gate d'acces B2C pour la projection transit publique.
"""Réutilise le gate B2C existant sans laisser le routeur manipuler la DB."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.auth_context import AuthenticatedUser
from app.infra.db.session import SessionLocal
from app.services.entitlement.b2c_runtime_gate import B2CAccessSnapshot, resolve_b2c_access

TRANSIT_PROJECTION_FEATURE_CODE = "transit_client_projection"


class TransitProjectionAccessDenied(Exception):
    """Signale un refus de plan B2C sous forme exploitable par le handler."""

    def __init__(
        self,
        reason: str,
        billing_status: str,
        plan_code: str,
        reason_code: str | None,
    ) -> None:
        self.reason = reason
        self.billing_status = billing_status
        self.plan_code = plan_code
        self.reason_code = reason_code


class TransitProjectionQuotaDenied(Exception):
    """Signale un refus quota pour la projection transit."""

    def __init__(
        self,
        quota_key: str,
        used: int,
        limit: int,
        window_end: datetime | None = None,
    ) -> None:
        self.quota_key = quota_key
        self.used = used
        self.limit = limit
        self.window_end = window_end


class TransitProjectionAccessResolver:
    """Résout l'accès transit via le gate B2C canonique."""

    def resolve(self, current_user: AuthenticatedUser) -> B2CAccessSnapshot:
        """Retourne le snapshot B2C ou lève un refus explicite."""
        with SessionLocal() as db:
            return self._resolve_with_session(db, current_user)

    def _resolve_with_session(
        self,
        db: Session,
        current_user: AuthenticatedUser,
    ) -> B2CAccessSnapshot:
        """Isole l'appel au gate B2C pour garder une seule responsabilite."""
        return resolve_b2c_access(
            db,
            user_id=current_user.id,
            feature_code=TRANSIT_PROJECTION_FEATURE_CODE,
            denied_error_factory=TransitProjectionAccessDenied,
            quota_error_factory=TransitProjectionQuotaDenied,
        )


def get_transit_projection_access_resolver() -> TransitProjectionAccessResolver:
    """Construit le resolver d'accès transit pour la dependance HTTP."""
    return TransitProjectionAccessResolver()
