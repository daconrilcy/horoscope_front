"""Contrats d'identité authentifiée partagés hors de la couche HTTP."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    """Identité utilisateur résolue par l'adaptateur HTTP d'authentification."""

    id: int
    role: str
    email: str
    created_at: datetime
    permissions: list[str] = []


class AuthenticatedEnterpriseClient(BaseModel):
    """Identité client B2B résolue depuis une clé API entreprise."""

    account_id: int
    credential_id: int
    key_prefix: str
