"""Orchestre la génération LLM des consultations thématiques à partir du contexte métier."""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.domain.astrology.natal_calculation import NatalCalculationError
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparationError
from app.infra.db.repositories.consultation_third_party_repository import (
    ConsultationThirdPartyRepository,
)
from app.services.api_contracts.public.consultation import (
    ConsultationBlock,
    ConsultationBlockKind,
    ConsultationGenerateData,
    ConsultationGenerateRequest,
    ConsultationSection,
    ConsultationStatus,
    ConsultationThirdPartyProfileCreate,
    FallbackMode,
)
from app.services.consultation.catalogue_service import ConsultationCatalogueService
from app.services.consultation.fallback_service import ConsultationFallbackService
from app.services.consultation.precheck_service import ConsultationPrecheckService
from app.services.consultation.third_party_service import ConsultationThirdPartyService
from app.services.llm_generation.guidance.guidance_service import GuidanceService
from app.services.llm_generation.shared.contextual_text import parse_structured_guidance_blocks
from app.services.llm_generation.shared.natal_context import (
    build_natal_chart_summary_with_defaults,
    build_user_natal_chart_summary_context,
)
from app.services.natal.calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService
from app.services.user_profile.birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)


class ConsultationGenerationService:
    """Orchestre la preparation metier et le rendu des consultations thematiques."""

    logger = logging.getLogger(__name__)

    @staticmethod
    def _parse_section_blocks(content: str) -> list[ConsultationBlock]:
        """Mappe le texte guidance canonique vers les blocs consultation."""
        shared_blocks = parse_structured_guidance_blocks(content)
        kind_mapping = {
            "title": ConsultationBlockKind.title,
            "subtitle": ConsultationBlockKind.subtitle,
            "paragraph": ConsultationBlockKind.paragraph,
            "bullet_list": ConsultationBlockKind.bullet_list,
        }
        consultation_blocks: list[ConsultationBlock] = []
        for block in shared_blocks:
            payload: dict[str, object] = {"kind": kind_mapping[block.kind]}
            if block.text is not None:
                payload["text"] = block.text
            if block.items is not None:
                payload["items"] = block.items
            consultation_blocks.append(ConsultationBlock(**payload))
        return consultation_blocks

    @staticmethod
    def _build_text_blocks(content: str) -> list[ConsultationBlock]:
        blocks: list[ConsultationBlock] = []
        for line in content.splitlines():
            normalized = line.strip()
            if not normalized:
                continue
            blocks.append(
                ConsultationBlock(
                    kind=ConsultationBlockKind.paragraph,
                    text=normalized,
                )
            )
        return blocks

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
                try:
                    natal_result = NatalCalculationService.calculate(
                        db,
                        birth_input=birth_input,
                        accurate=False,
                        derive_enabled=True,
                    )
                except (BirthPreparationError, NatalCalculationError) as recalculation_error:
                    ConsultationGenerationService.logger.warning(
                        "consultation_other_person_chart_unavailable code=%s",
                        getattr(recalculation_error, "code", "unknown"),
                    )
                    return None
            else:
                ConsultationGenerationService.logger.warning(
                    "consultation_other_person_chart_unavailable code=%s",
                    error.code,
                )
                return None
        except BirthPreparationError as error:
            ConsultationGenerationService.logger.warning(
                "consultation_other_person_chart_unavailable code=%s",
                error.code,
            )
            return None

        return build_natal_chart_summary_with_defaults(
            natal_result=natal_result,
            birth_date=other_person.birth_date,
            birth_time=other_person.birth_time if other_person.birth_time_known else None,
            birth_place=other_person.birth_place,
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

        user_summary = build_user_natal_chart_summary_context(
            db,
            user_id=user_id,
            birth_date=user_profile.birth_date,
            birth_time=user_profile.birth_time,
            birth_place=user_profile.birth_place,
            warning_event="consultation_natal_chart_context_unavailable",
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
    def _build_consultation_objective(db: Session, request: ConsultationGenerateRequest) -> str:
        explicit_objective = (request.objective or "").strip()
        if explicit_objective:
            return explicit_objective

        # AC1: Pilotage par la DB si disponible
        template = ConsultationCatalogueService.get_template_by_key(db, request.consultation_type)
        if template and template.prompt_content:
            return template.prompt_content

        objective_by_type = {
            "period": "Comprendre le climat astrologique de la periode demandee.",
            "career": "Eclairer une interaction ou une decision liee au travail.",
            "orientation": "Clarifier une direction de vie ou une decision structurante.",
            "relationship": "Lire la dynamique relationnelle de maniere prudente et non fataliste.",
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
            lines.append(f"Mode astrologique applique: {route_key}.")
        if request.other_person:
            lines.append(
                "Donnees tiers prises en compte: "
                f"{request.other_person.birth_date} / {request.other_person.birth_place}"
            )
            if other_person_chart_used:
                lines.append("Theme natal tiers calcule et integre dans la lecture relationnelle.")
            else:
                lines.append(
                    "Donnees tiers recues, mais theme natal tiers non exploite comme "
                    "contexte astrologique complet."
                )
        lines.append(
            "La lecture utilise le profil natal existant de l utilisateur quand il est disponible."
        )
        return ConsultationSection(
            id="consultation_basis",
            title="Base de lecture",
            content="\n".join(lines),
            blocks=ConsultationGenerationService._build_text_blocks("\n".join(lines)),
        )

    @staticmethod
    def _record_third_party_usage(
        db: Session,
        *,
        user_id: int,
        consultation_id: str,
        consultation_type: str,
        context_summary: str,
        third_party_external_id: str | None = None,
        request: ConsultationGenerateRequest | None = None,
    ) -> None:
        repo = ConsultationThirdPartyRepository(db)
        profile = None

        if third_party_external_id:
            profile = repo.get_by_external_id(third_party_external_id)
            if profile is not None and profile.user_id != user_id:
                profile = None

        if (
            profile is None
            and request is not None
            and request.save_third_party
            and request.other_person
            and request.third_party_nickname
        ):
            created_profile = ConsultationThirdPartyService.create_third_party(
                db,
                user_id,
                ConsultationThirdPartyProfileCreate(
                    nickname=request.third_party_nickname,
                    birth_date=request.other_person.birth_date,
                    birth_time=request.other_person.birth_time,
                    birth_time_known=request.other_person.birth_time_known,
                    birth_place=request.other_person.birth_place,
                    birth_city=request.other_person.birth_city,
                    birth_country=request.other_person.birth_country,
                    birth_lat=request.other_person.birth_lat,
                    birth_lon=request.other_person.birth_lon,
                    place_resolved_id=request.other_person.place_resolved_id,
                ),
            )
            profile = repo.get_by_external_id(created_profile.external_id)

        if profile is None:
            return

        repo.record_usage(
            third_party_profile_id=profile.id,
            consultation_id=consultation_id,
            consultation_type=consultation_type,
            context_summary=context_summary[:255],
        )
        db.commit()

    @staticmethod
    async def generate(
        db: Session,
        user_id: int,
        request: ConsultationGenerateRequest,
        request_id: str,
        entitlement_result: Any = None,
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
                        blocks=ConsultationGenerationService._build_text_blocks(
                            "Cette demande touche un domaine sensible. La réponse "
                            "reste volontairement generale et non prescriptive."
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
        objective = ConsultationGenerationService._build_consultation_objective(db, request)
        natal_chart_summary_override: str | None = None
        other_person_chart_used = False
        if request.consultation_type == "relationship" and request.other_person is not None:
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
            entitlement_result=entitlement_result,
        )

        consultation_id = f"consult_{request_id}"
        if request.other_person is not None:
            try:
                ConsultationGenerationService._record_third_party_usage(
                    db,
                    user_id=user_id,
                    consultation_id=consultation_id,
                    consultation_type=request.consultation_type,
                    context_summary=guidance.summary or "",
                    third_party_external_id=request.third_party_external_id,
                    request=request,
                )
            except Exception as error:
                ConsultationGenerationService.logger.exception(
                    "failed_to_record_third_party_usage error=%s",
                    error,
                )

        sections = [
            ConsultationSection(
                id="analysis",
                title="Lecture astrologique",
                content=guidance.full_text,
                blocks=ConsultationGenerationService._parse_section_blocks(guidance.full_text),
            ),
            ConsultationGenerationService._build_context_section(
                request=request,
                route_key=route_key,
                other_person_chart_used=other_person_chart_used,
            ),
        ]

        return ConsultationGenerateData(
            consultation_id=consultation_id,
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
