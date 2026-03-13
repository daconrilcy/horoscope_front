import logging

from sqlalchemy.orm import Session

from app.api.v1.schemas.consultation import (
    ConsultationGenerateData,
    ConsultationGenerateRequest,
    ConsultationSection,
    ConsultationStatus,
    FallbackMode,
)
from app.services.consultation_fallback_service import ConsultationFallbackService
from app.services.consultation_precheck_service import ConsultationPrecheckService
from app.services.guidance_service import GuidanceService


class ConsultationGenerationService:
    logger = logging.getLogger(__name__)

    @staticmethod
    def _build_consultation_objective(request: ConsultationGenerateRequest) -> str:
        explicit_objective = (request.objective or "").strip()
        if explicit_objective:
            return explicit_objective

        objective_by_type = {
            "period": "Comprendre le climat astrologique de la periode demandee.",
            "work": "Eclairer une interaction ou une decision liee au travail.",
            "orientation": "Clarifier une direction de vie ou une decision structurante.",
            "relation": "Lire la dynamique relationnelle de maniere prudente et non fataliste.",
            "timing": "Identifier le bon tempo d action avec une lecture astrologique prudente.",
        }
        return objective_by_type.get(
            request.consultation_type,
            f"Approfondir la consultation {request.consultation_type}.",
        )

    @staticmethod
    def _build_context_section(
        *,
        request: ConsultationGenerateRequest,
        route_key: str | None,
    ) -> ConsultationSection:
        lines = [
            f"Type de consultation: {request.consultation_type}",
            f"Question analysee: {request.question}",
        ]
        if request.objective:
            lines.append(f"Objet retenu: {request.objective}")
        if request.horizon:
            lines.append(f"Horizon temporel: {request.horizon}")
        if route_key:
            lines.append(
                "Mode astrologique applique: "
                f"{route_key}."
            )
        if request.other_person:
            lines.append(
                "Donnees tiers prises en compte: "
                f"{request.other_person.birth_date} / {request.other_person.birth_place}"
            )
        lines.append(
            "La lecture utilise le profil natal existant de l utilisateur "
            "quand il est disponible."
        )
        return ConsultationSection(
            id="consultation_basis",
            title="Base de lecture",
            content="\n".join(lines),
        )

    @staticmethod
    async def generate(
        db: Session,
        user_id: int,
        request: ConsultationGenerateRequest,
        request_id: str,
    ) -> ConsultationGenerateData:
        precheck = ConsultationPrecheckService.precheck(db, user_id, request)

        if precheck.fallback_mode == FallbackMode.safeguard_refused:
            return ConsultationGenerateData(
                consultation_id=f"refused_{request_id}",
                consultation_type=request.consultation_type,
                status=precheck.status,
                precision_level=precheck.precision_level,
                fallback_mode=precheck.fallback_mode,
                safeguard_issue=precheck.safeguard_issue,
                route_key=None,
                summary=(
                    "Cette consultation ne peut pas être générée pour des raisons "
                    "de sécurité ou de déontologie."
                ),
                sections=[],
                chat_prefill="",
                metadata={"request_id": request_id},
            )

        if precheck.status == ConsultationStatus.blocked:
            return ConsultationGenerateData(
                consultation_id=f"blocked_{request_id}",
                consultation_type=request.consultation_type,
                status=precheck.status,
                precision_level=precheck.precision_level,
                fallback_mode=precheck.fallback_mode,
                safeguard_issue=precheck.safeguard_issue,
                route_key=None,
                summary=(
                    "Cette consultation ne peut pas être générée tant que les "
                    "données requises ne sont pas complétées."
                ),
                sections=[],
                chat_prefill="",
                metadata={"request_id": request_id},
            )

        if precheck.fallback_mode == FallbackMode.safeguard_reframed:
            return ConsultationGenerateData(
                consultation_id=f"reframed_{request_id}",
                consultation_type=request.consultation_type,
                status=precheck.status,
                precision_level=precheck.precision_level,
                fallback_mode=precheck.fallback_mode,
                safeguard_issue=precheck.safeguard_issue,
                route_key=None,
                summary=(
                    "La consultation est recadrée vers une réponse prudente et "
                    "limitée aux aspects non sensibles."
                ),
                sections=[
                    ConsultationSection(
                        id="limitations",
                        title="Limites",
                        content=(
                            "Cette demande touche un domaine sensible. La réponse "
                            "reste volontairement générale et non prescriptive."
                        ),
                    )
                ],
                chat_prefill=(
                    "Je souhaite reformuler ma consultation dans un cadre non "
                    "sensible et plus général."
                ),
                metadata={"request_id": request_id},
            )

        route_key = ConsultationFallbackService.resolve_route_key(precheck)
        objective = ConsultationGenerationService._build_consultation_objective(request)
        guidance = await GuidanceService.request_contextual_guidance_async(
            db,
            user_id=user_id,
            situation=request.question,
            objective=objective,
            time_horizon=request.horizon,
            request_id=request_id,
        )

        sections = [
            ConsultationSection(
                id="analysis",
                title="Lecture astrologique",
                content=guidance.full_text,
            ),
            ConsultationSection(
                id="consultation_basis",
                title="Base de lecture",
                content=ConsultationGenerationService._build_context_section(
                    request=request,
                    route_key=route_key,
                ).content,
            ),
        ]

        return ConsultationGenerateData(
            consultation_id=f"consult_{request_id}",
            consultation_type=request.consultation_type,
            status=precheck.status,
            precision_level=precheck.precision_level,
            fallback_mode=precheck.fallback_mode,
            safeguard_issue=precheck.safeguard_issue,
            route_key=route_key,
            summary=guidance.summary,
            sections=sections,
            chat_prefill=(
                f"Je souhaite approfondir ma consultation "
                f"{request.consultation_type} sur : {request.question}"
            ),
            metadata={
                "request_id": request_id,
                "guidance_generated_at": str(guidance.generated_at),
                "route_key": route_key,
                "objective": objective,
            },
        )
