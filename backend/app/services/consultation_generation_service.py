import logging

from sqlalchemy.orm import Session

from app.api.v1.schemas.consultation import (
    ConsultationGenerateData,
    ConsultationGenerateRequest,
    ConsultationSection,
    ConsultationStatus,
    FallbackMode,
)
from app.domain.astrology.natal_calculation import NatalCalculationError
from app.domain.astrology.natal_preparation import BirthInput
from app.services.consultation_fallback_service import ConsultationFallbackService
from app.services.consultation_precheck_service import ConsultationPrecheckService
from app.services.guidance_service import GuidanceService
from app.services.natal_calculation_service import NatalCalculationService
from app.services.natal_interpretation_service import build_natal_chart_summary
from app.services.reference_data_service import ReferenceDataService
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)


class ConsultationGenerationService:
    logger = logging.getLogger(__name__)

    @staticmethod
    def _detect_degraded_mode(
        *,
        birth_time: str | None,
        birth_place: str | None,
    ) -> str | None:
        no_time = birth_time is None or birth_time.strip() == ""
        no_location = birth_place is None or birth_place.strip() == ""
        if no_time and no_location:
            return "no_location_no_time"
        if no_time:
            return "no_time"
        if no_location:
            return "no_location"
        return None

    @staticmethod
    def _calculate_other_person_natal_summary(
        db: Session,
        request: ConsultationGenerateRequest,
    ) -> str | None:
        other_person = request.other_person
        if other_person is None:
            return None

        birth_input = BirthInput(
            birth_date=other_person.birth_date,
            birth_time=other_person.birth_time if other_person.birth_time_known else None,
            birth_place=other_person.birth_place,
            birth_timezone=None,
            place_resolved_id=other_person.place_resolved_id,
            birth_city=other_person.birth_city,
            birth_country=other_person.birth_country,
            birth_lat=other_person.birth_lat,
            birth_lon=other_person.birth_lon,
        )

        try:
            natal_result = NatalCalculationService.calculate(
                db,
                birth_input=birth_input,
                accurate=False,
                derive_enabled=True,
            )
        except NatalCalculationError as error:
            should_auto_seed = error.code == "reference_version_not_found"
            if should_auto_seed:
                ReferenceDataService.seed_reference_version(db)
                natal_result = NatalCalculationService.calculate(
                    db,
                    birth_input=birth_input,
                    accurate=False,
                    derive_enabled=True,
                )
            else:
                ConsultationGenerationService.logger.warning(
                    "consultation_other_person_chart_unavailable code=%s",
                    error.code,
                )
                return None

        degraded_mode = ConsultationGenerationService._detect_degraded_mode(
            birth_time=other_person.birth_time if other_person.birth_time_known else None,
            birth_place=other_person.birth_place,
        )
        return build_natal_chart_summary(
            natal_result=natal_result,
            birth_place=other_person.birth_place,
            birth_date=other_person.birth_date,
            birth_time=(other_person.birth_time if other_person.birth_time_known else "00:00"),
            degraded_mode=degraded_mode,
        )

    @staticmethod
    def _build_relation_natal_context(
        db: Session,
        *,
        user_id: int,
        request: ConsultationGenerateRequest,
    ) -> tuple[str | None, bool]:
        try:
            user_profile = UserBirthProfileService.get_for_user(db, user_id)
        except UserBirthProfileServiceError:
            return None, False

        user_summary = GuidanceService.build_natal_chart_summary_context(
            db,
            user_id=user_id,
            birth_date=user_profile.birth_date,
            birth_time=user_profile.birth_time,
            birth_place=user_profile.birth_place,
        )
        other_summary = ConsultationGenerationService._calculate_other_person_natal_summary(
            db,
            request,
        )
        if other_summary is None:
            return user_summary, False

        blocks: list[str] = []
        if user_summary:
            blocks.append(f"THEME NATAL UTILISATEUR:\n{user_summary}")
        blocks.append(f"THEME NATAL AUTRE PERSONNE:\n{other_summary}")
        blocks.append(
            "LECTURE RELATIONNELLE: compare les deux themes, les resonances, les tensions "
            "et les complementarites sans inventer de placements absents."
        )
        return "\n\n".join(blocks), True

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
        other_person_chart_used: bool,
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
            if other_person_chart_used:
                lines.append(
                    "Theme natal tiers calcule et integre dans la lecture relationnelle."
                )
            else:
                lines.append(
                    "Donnees tiers recues, mais theme natal tiers non exploite comme "
                    "contexte astrologique complet."
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
        natal_chart_summary_override: str | None = None
        other_person_chart_used = False
        if request.consultation_type == "relation" and request.other_person is not None:
            (
                natal_chart_summary_override,
                other_person_chart_used,
            ) = ConsultationGenerationService._build_relation_natal_context(
                db,
                user_id=user_id,
                request=request,
            )
        guidance = await GuidanceService.request_contextual_guidance_async(
            db,
            user_id=user_id,
            situation=request.question,
            objective=objective,
            time_horizon=request.horizon,
            natal_chart_summary_override=natal_chart_summary_override,
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
                    other_person_chart_used=other_person_chart_used,
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
                "other_person_chart_used": other_person_chart_used,
            },
        )
