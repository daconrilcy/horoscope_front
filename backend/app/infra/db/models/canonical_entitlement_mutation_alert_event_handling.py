# Shim legacy pour l'ancien chemin et l'ancien nom de classe du handling courant.
"""Réexporte le modèle canonique de handling et fournit un alias legacy."""

from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)

CanonicalEntitlementMutationAlertEventHandlingModel = CanonicalEntitlementMutationAlertHandlingModel

__all__ = [
    "CanonicalEntitlementMutationAlertEventHandlingModel",
    "CanonicalEntitlementMutationAlertHandlingModel",
]
