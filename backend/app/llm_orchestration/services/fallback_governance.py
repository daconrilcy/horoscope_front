import logging
import re
from typing import Any, Dict, Optional, Set

from app.infra.observability.metrics import increment_counter
from app.llm_orchestration.feature_taxonomy import SUPPORTED_FAMILIES
from app.llm_orchestration.models import FallbackStatus, FallbackType

logger = logging.getLogger(__name__)


class FallbackGovernanceRegistry:
    """
    Registre central de gouvernance des mécanismes de compatibilité (Story 66.21).
    Définit le statut, le périmètre et la politique d'extinction de chaque fallback.
    """

    GOVERNANCE_MATRIX: Dict[FallbackType, Dict[str, Any]] = {
        FallbackType.LEGACY_WRAPPER: {
            "status": FallbackStatus.TRANSITORY,
            "justification": "Wrapper de façade pour non-régression immédiate.",
            "perimeter": "Appelants legacy existants (LLMGateway.execute).",
            "extinction_criteria": "Migration du dernier appelant vers execute_request.",
        },
        FallbackType.DEPRECATED_USE_CASE: {
            "status": FallbackStatus.TRANSITORY,
            "justification": "Permet la convergence sans casser les clients mobiles/externes.",
            "perimeter": "Use cases mappés dans DEPRECATED_USE_CASE_MAPPING.",
            "extinction_criteria": "Compteurs d'usage à zéro en production.",
        },
        FallbackType.USE_CASE_FIRST: {
            "status": FallbackStatus.TO_REMOVE,  # Par défaut, restreint
            "justification": "Éteindre la concurrence avec le pipeline canonique.",
            "forbidden_families": SUPPORTED_FAMILIES,
            "extinction_criteria": "Migration 100% des features vers assembly.",
        },
        FallbackType.RESOLVE_MODEL: {
            "status": FallbackStatus.TRANSITORY,
            "justification": "Filet de sécurité si ExecutionProfile est manquant.",
            "perimeter": "Chemins sans ExecutionProfile explicite.",
            "extinction_criteria": "Généralisation des ExecutionProfile sur tous les parcours.",
        },
        FallbackType.EXECUTION_CONFIG_ADMIN: {
            "status": FallbackStatus.TO_REMOVE,
            "justification": "Ancienne méthode de configuration directe (dette).",
            "extinction_criteria": "Suppression après migration complète vers ExecutionProfile.",
        },
        FallbackType.PROVIDER_OPENAI: {
            "status": FallbackStatus.TOLERATED,
            "justification": "Limitation runtime assumée (OpenAI-only).",
            "perimeter": "Runtime actuel.",
            "extinction_criteria": "Activation multi-provider réelle.",
        },
        FallbackType.NARRATOR_LEGACY: {
            "status": FallbackStatus.TO_REMOVE,
            "justification": "Obsolète, remplacé par le gateway.",
            "forbidden_families": {"horoscope_daily"},
            "extinction_criteria": "Suppression du fichier llm_narrator.py.",
        },
        FallbackType.TEST_LOCAL: {
            "status": FallbackStatus.TOLERATED,
            "justification": "Productivité développement hors-production.",
            "perimeter": "Environnements dev et test uniquement.",
            "extinction_criteria": "Pérenne (hors production).",
        },
        FallbackType.NATAL_NO_DB: {
            "status": FallbackStatus.TRANSITORY,
            "justification": "Souplesse de test historique et modes dégradés.",
            "perimeter": "Tests unitaires et modes dégradés Natal.",
            "extinction_criteria": "DB obligatoire en production nominale.",
        },
    }

    @staticmethod
    def _infer_family(feature: Optional[str], call_site: str) -> Optional[str]:
        """Infère la famille à partir du feature ou du call_site (use_case)."""
        if feature:
            return feature

        # Les call_sites de resolve_config et mapping contiennent souvent le use_case
        # ex: "resolve_config:horoscope_daily"
        match = re.search(r":([a-zA-Z0-9_-]+)$", call_site)
        if not match:
            return None

        use_case = match.group(1).lower()
        if use_case.startswith("chat"):
            return "chat"
        if use_case.startswith("guidance") or "guidance" in use_case:
            return "guidance"
        if use_case.startswith("natal") or "natal" in use_case:
            return "natal"
        # Story 66.28: daily_prediction is now absorbed into horoscope_daily
        if use_case.startswith("horoscope_daily") or use_case == "daily_prediction":
            return "horoscope_daily"

        return None

    @classmethod
    def track_fallback(
        self,
        fallback_type: FallbackType,
        call_site: str,
        feature: Optional[str] = None,
        is_nominal: bool = True,
    ) -> None:
        """
        Enregistre l'usage d'un fallback, vérifie sa conformité et émet la télémétrie.
        """
        from app.core.config import settings

        is_prod = settings.app_env in {"production", "prod"}

        gov = self.GOVERNANCE_MATRIX.get(fallback_type)
        if not gov:
            logger.warning(
                "governance_unknown_fallback type=%s call_site=%s", fallback_type, call_site
            )
            return

        status = gov["status"]
        forbidden_families: Set[str] = gov.get("forbidden_families", set())

        # AC3 Bypass Fix: Inférence de la famille si absente
        effective_feature = self._infer_family(feature, call_site)

        # 1. Gestion spécifique du statut conditionnel pour USE_CASE_FIRST (AC3)
        if fallback_type == FallbackType.USE_CASE_FIRST:
            if effective_feature not in forbidden_families:
                status = FallbackStatus.TRANSITORY

        # 2. Télémétrie (AC5, AC7, AC9) - Toujours émise même si blocage (Medium Issue Fix)
        labels = {
            "fallback_type": fallback_type.value,
            "status": status.value,
            "call_site": call_site,
            "feature": effective_feature or feature or "unknown",
            "is_nominal": "true" if is_nominal else "false",
        }
        increment_counter("llm_gateway_fallback_usage_total", labels=labels)

        # 3. Vérification du périmètre (Forbidden families)
        if effective_feature in forbidden_families and is_nominal:
            logger.error(
                "governance_violation_forbidden_fallback type=%s feature=%s call_site=%s status=%s",
                fallback_type.value,
                effective_feature,
                call_site,
                status.value,
            )
            if status == FallbackStatus.TO_REMOVE:
                from app.llm_orchestration.models import GatewayError

                msg = (
                    f"Usage du fallback '{fallback_type.value}' interdit pour "
                    f"la famille '{effective_feature}' (Gouvernance 66.21)"
                )
                raise GatewayError(
                    msg,
                    details={
                        "fallback_type": fallback_type.value,
                        "feature": effective_feature,
                        "status": status.value,
                    },
                )

        # 4. Vérification environnementale (AC9)
        if is_prod:
            if fallback_type == FallbackType.TEST_LOCAL:
                from app.llm_orchestration.models import GatewayError

                raise GatewayError(
                    f"Usage du fallback '{fallback_type.value}' strictement interdit en production",
                    details={"fallback_type": fallback_type.value, "call_site": call_site},
                )

            # Natal No DB en production: alerte critique si non nominal (erreur DB masquée)
            if fallback_type == FallbackType.NATAL_NO_DB and not is_nominal:
                logger.critical(
                    "governance_critical_prod_database_error_masked type=%s call_site=%s",
                    fallback_type.value,
                    call_site,
                )

        # 5. Restriction TO_REMOVE sur nouveaux parcours (AC6)
        if status == FallbackStatus.TO_REMOVE and is_nominal:
            logger.error(
                "governance_nominal_path_dependency_on_to_remove_fallback type=%s call_site=%s",
                fallback_type.value,
                call_site,
            )
            from app.llm_orchestration.models import GatewayError

            raise GatewayError(
                f"Dépendance nominale au fallback '{fallback_type.value}' interdite "
                "(Statut: À RETIRER)",
                details={"fallback_type": fallback_type.value, "call_site": call_site},
            )

        # Logging structuré pour observabilité (AC5)
        log_level = logging.WARNING if status == FallbackStatus.TO_REMOVE else logging.INFO
        logger.log(
            log_level,
            "governance_fallback_usage type=%s status=%s feature=%s call_site=%s nominal=%s",
            fallback_type.value,
            status.value,
            effective_feature,
            call_site,
            is_nominal,
        )

    @classmethod
    def get_status(self, fallback_type: FallbackType) -> FallbackStatus:
        return self.GOVERNANCE_MATRIX.get(fallback_type, {}).get(
            "status", FallbackStatus.TRANSITORY
        )
