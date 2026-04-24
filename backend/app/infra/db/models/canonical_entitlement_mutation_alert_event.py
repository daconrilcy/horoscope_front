# Shim legacy pour l'ancien chemin d'import des alert events.
"""Réexporte le modèle canonique d'alerte pour préserver la compatibilité locale."""

from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)

__all__ = ["CanonicalEntitlementMutationAlertEventModel"]
