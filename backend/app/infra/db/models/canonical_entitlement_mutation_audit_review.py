# Shim legacy pour l'ancien chemin d'import de la review courante.
"""Réexporte le modèle canonique de review pour préserver la compatibilité locale."""

from app.infra.db.models.entitlement_mutation.audit.review import (
    CanonicalEntitlementMutationAuditReviewModel,
)

__all__ = ["CanonicalEntitlementMutationAuditReviewModel"]
