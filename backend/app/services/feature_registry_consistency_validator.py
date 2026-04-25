from app.services.b2b_api_entitlement_gate import B2BApiEntitlementGate
from app.services.entitlement import feature_scope_registry
from app.services.entitlement.chat_entitlement_gate import ChatEntitlementGate
from app.services.entitlement.natal_chart_long_entitlement_gate import NatalChartLongEntitlementGate
from app.services.entitlement.thematic_consultation_entitlement_gate import (
    ThematicConsultationEntitlementGate,
)


class FeatureRegistryConsistencyError(ValueError):
    """Exception levée sur toute incohérence du registre de features."""


class FeatureRegistryConsistencyValidator:
    """Validateur central de la cohérence du registre de features."""

    # Liste canonique attendue : (feature_code, expected_scope)
    EXPECTED_GATE_SCOPES: list[tuple[str, feature_scope_registry.FeatureScope]] = [
        (ChatEntitlementGate.FEATURE_CODE, feature_scope_registry.FeatureScope.B2C),
        (
            ThematicConsultationEntitlementGate.FEATURE_CODE,
            feature_scope_registry.FeatureScope.B2C,
        ),
        (
            NatalChartLongEntitlementGate.FEATURE_CODE,
            feature_scope_registry.FeatureScope.B2C,
        ),
        (B2BApiEntitlementGate.FEATURE_CODE, feature_scope_registry.FeatureScope.B2B),
    ]

    # Features metered B2C du seed canonique (static, pas de DB)
    CANONICAL_B2C_METERED_FEATURES: frozenset[str] = frozenset(
        {
            "natal_chart_long",
            "astrologer_chat",
            "thematic_consultation",
        }
    )

    @staticmethod
    def _get_registry() -> dict[str, object]:
        return feature_scope_registry.FEATURE_SCOPE_REGISTRY

    @staticmethod
    def _format_scope(scope: object) -> str:
        if isinstance(scope, feature_scope_registry.FeatureScope):
            return scope.value
        return repr(scope)

    @staticmethod
    def validate() -> None:
        """
        Vérifie la cohérence entre le registre, les gates et le seed canonique.
        Lève FeatureRegistryConsistencyError si une incohérence est détectée.
        """
        errors: list[str] = []
        registry = FeatureRegistryConsistencyValidator._get_registry()

        # Vérif 1 & 2 : Exhaustivité registre <-> gates et Scopes canoniques imposés
        for (
            feature_code,
            expected_scope,
        ) in FeatureRegistryConsistencyValidator.EXPECTED_GATE_SCOPES:
            actual_scope = registry.get(feature_code)
            if actual_scope is None:
                errors.append(
                    f"Feature code '{feature_code}' manquant dans "
                    "FEATURE_SCOPE_REGISTRY (requis par sa gate quota)."
                )
            elif actual_scope != expected_scope:
                errors.append(
                    f"Scope invalide pour '{feature_code}' dans le registre : "
                    f"attendu {expected_scope.value}, "
                    f"trouvé {FeatureRegistryConsistencyValidator._format_scope(actual_scope)}."
                )

        # Vérif 3 : Cohérence seed B2C
        for feature_code in FeatureRegistryConsistencyValidator.CANONICAL_B2C_METERED_FEATURES:
            actual_scope = registry.get(feature_code)
            if actual_scope is None:
                errors.append(
                    f"Feature metered B2C '{feature_code}' (seed canonique) "
                    "manquante dans le registre."
                )
            elif actual_scope != feature_scope_registry.FeatureScope.B2C:
                errors.append(
                    f"Feature metered B2C '{feature_code}' doit avoir le scope "
                    "B2C dans le registre "
                    f"(trouvé {FeatureRegistryConsistencyValidator._format_scope(actual_scope)})."
                )

        # Vérif 4 : Validité du registre (enum membership check)
        # On vérifie que chaque valeur dans le registre est bien une instance de FeatureScope
        for feature_code, scope in registry.items():
            if not isinstance(scope, feature_scope_registry.FeatureScope):
                errors.append(
                    f"Scope invalide '{scope}' (type {type(scope).__name__}) "
                    f"pour la feature '{feature_code}' dans le registre. "
                    "Doit être une instance de FeatureScope."
                )

        if errors:
            raise FeatureRegistryConsistencyError(
                "Feature registry inconsistencies detected:\n"
                + "\n".join(f"  {i + 1}. {e}" for i, e in enumerate(errors))
            )
