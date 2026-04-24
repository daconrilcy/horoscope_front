# Shim legacy pour l'ancien chemin et l'ancien nom de classe de l'historique de handling.
"""Réexporte le modèle canonique d'historique de handling et fournit un alias legacy."""

from app.infra.db.models.entitlement_mutation.alert.handling_event import (
    CanonicalEntitlementMutationAlertHandlingEventModel,
)

CanonicalEntitlementMutationAlertEventHandlingEventModel = (
    CanonicalEntitlementMutationAlertHandlingEventModel
)

__all__ = [
    "CanonicalEntitlementMutationAlertEventHandlingEventModel",
    "CanonicalEntitlementMutationAlertHandlingEventModel",
]
