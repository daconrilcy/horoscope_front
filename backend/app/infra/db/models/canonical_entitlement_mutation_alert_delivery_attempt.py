# Shim legacy pour l'ancien chemin d'import des tentatives de delivery.
"""Réexporte le modèle canonique de delivery pour préserver la compatibilité locale."""

from app.infra.db.models.entitlement_mutation.alert.delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)

__all__ = ["CanonicalEntitlementMutationAlertDeliveryAttemptModel"]
