from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.schemas.natal_interpretation import (
    InterpretationMeta,
    NatalInterpretationData,
    NatalInterpretationResponse,
)
from app.core.config import settings
from app.domain.astrology.natal_calculation import NatalResult
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
from app.infra.observability.metrics import observe_duration
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import InputValidationError
from app.llm_orchestration.schemas import (
    AstroErrorResponseV3,
    AstroResponseV1,
    AstroResponseV2,
    AstroResponseV3,
)
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2
from app.services.chart_json_builder import (
    build_chart_json,
    build_enriched_evidence_catalog,
)
from app.services.disclaimer_registry import get_disclaimers
from app.services.user_birth_profile_service import UserBirthProfileData

logger = logging.getLogger(__name__)

MODULE_TO_USE_CASE_KEY: dict[str, str] = {
    "NATAL_PSY_PROFILE": "natal_psy_profile",
    "NATAL_SHADOW_INTEGRATION": "natal_shadow_integration",
    "NATAL_LEADERSHIP_WORKSTYLE": "natal_leadership_workstyle",
    "NATAL_CREATIVITY_JOY": "natal_creativity_joy",
    "NATAL_RELATIONSHIP_STYLE": "natal_relationship_style",
    "NATAL_COMMUNITY_NETWORKS": "natal_community_networks",
    "NATAL_VALUES_SECURITY": "natal_values_security",
    "NATAL_EVOLUTION_PATH": "natal_evolution_path",
}


def _normalize_persona_field(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    return []


def _build_persona_prompt_profile(persona: LlmPersonaModel) -> str:
    tone_value = persona.tone.value if hasattr(persona.tone, "value") else str(persona.tone)
    verbosity_value = (
        persona.verbosity.value if hasattr(persona.verbosity, "value") else str(persona.verbosity)
    )
    tone_label = {
        "warm": "chaleureux, empathique et soutenant",
        "direct": "clair, direct et factuel",
        "mystical": "symbolique, intuitif et inspirant",
        "rational": "rationnel, structuré et analytique",
    }.get(tone_value, tone_value)
    verbosity_label = {
        "short": "synthétique",
        "medium": "équilibré",
        "long": "approfondi",
    }.get(verbosity_value, verbosity_value)

    style_markers = _normalize_persona_field(persona.style_markers)
    boundaries = _normalize_persona_field(persona.boundaries)
    allowed_topics = _normalize_persona_field(persona.allowed_topics)

    style_fragment = ", ".join(style_markers) if style_markers else "pédagogie claire et concrète"
    boundaries_fragment = (
        "; ".join(boundaries) if boundaries else "pas de fatalisme et pas de promesse absolue"
    )
    topics_fragment = (
        ", ".join(allowed_topics) if allowed_topics else "thème natal et dynamiques de vie"
    )
    description = (persona.description or "").strip()
    if not description:
        description = "Profil astrologique orienté pédagogie et application concrète."

    return (
        f"Astrologue sélectionné : {persona.name}. "
        f"Personnalité : {description} "
        f"Style relationnel : ton {tone_label}, niveau {verbosity_label}. "
        f"Caractéristiques d'écriture : {style_fragment}. "
        f"Compétences clés : {topics_fragment}. "
        f"Cadre de pratique : {boundaries_fragment}. "
        "Méthode attendue : expliquer chaque notion au moment où elle apparaît, relier les indices "
        "astrologiques à des implications concrètes et rester non fataliste."
    )


class NatalInterpretationServiceV2:
    """
    Service for natal interpretation using LLM Gateway V2.
    """

    @staticmethod
    async def interpret(
        db: Session,
        user_id: int,
        chart_id: str,
        natal_result: NatalResult,
        birth_profile: UserBirthProfileData,
        level: Literal["short", "complete"],
        persona_id: Optional[str],
        locale: str,
        question: Optional[str],
        request_id: str,
        trace_id: str,
        force_refresh: bool = False,
        module: Optional[
            Literal[
                "NATAL_PSY_PROFILE",
                "NATAL_SHADOW_INTEGRATION",
                "NATAL_LEADERSHIP_WORKSTYLE",
                "NATAL_CREATIVITY_JOY",
                "NATAL_RELATIONSHIP_STYLE",
                "NATAL_COMMUNITY_NETWORKS",
                "NATAL_VALUES_SECURITY",
                "NATAL_EVOLUTION_PATH",
            ]
        ] = None,
        variant_code: Optional[str] = None,
    ) -> NatalInterpretationResponse:
        persona_uuid: uuid.UUID | None = None
        if persona_id:
            try:
                persona_uuid = uuid.UUID(persona_id)
            except (ValueError, TypeError):
                persona_uuid = None

        # Thematic modules must always bypass cache and DB persistence to avoid
        # mixing generic/premium cached payloads with module-specific responses.
        is_thematic_module = bool(module and level == "complete")
        effective_force_refresh = force_refresh or is_thematic_module

        # 0. Check for existing persisted interpretation
        if not effective_force_refresh:
            db_level = (
                InterpretationLevel.SHORT if level == "short" else InterpretationLevel.COMPLETE
            )
            stmt = select(UserNatalInterpretationModel).where(
                UserNatalInterpretationModel.user_id == user_id,
                UserNatalInterpretationModel.level == db_level,
            )
            if level == "complete":
                stmt = stmt.where(UserNatalInterpretationModel.persona_id == persona_uuid)
            else:
                stmt = stmt.where(UserNatalInterpretationModel.persona_id.is_(None))

            # story 64.3: variant_code must match for cached complete interpretations
            if level == "complete":
                stmt = stmt.where(UserNatalInterpretationModel.variant_code == variant_code)

            stmt = stmt.order_by(
                UserNatalInterpretationModel.created_at.desc(),
                UserNatalInterpretationModel.id.desc(),
            )

            existing_rows = list(db.execute(stmt).scalars().all())
            existing = existing_rows[0] if existing_rows else None
            if len(existing_rows) > 1:
                logger.warning(
                    "Multiple cached natal interpretations found for unique key; keeping latest "
                    "user_id=%s level=%s persona_id=%s duplicates=%s",
                    user_id,
                    db_level.value,
                    persona_id,
                    len(existing_rows),
                )
            if existing:
                # Avoid serving stale cached payloads produced with an archived prompt version.
                active_prompt = PromptRegistryV2.get_active_prompt(db, existing.use_case)
                active_prompt_id = str(active_prompt.id) if active_prompt else None
                existing_prompt_id = (
                    str(existing.prompt_version_id) if existing.prompt_version_id else None
                )
                if (
                    active_prompt_id
                    and existing_prompt_id
                    and active_prompt_id != existing_prompt_id
                ):
                    logger.info(
                        "Ignoring stale cached interpretation chart_id=%s use_case=%s "
                        "stored_prompt=%s active_prompt=%s",
                        chart_id,
                        existing.use_case,
                        existing_prompt_id,
                        active_prompt_id,
                    )
                    existing = None

            if existing:
                schema_version = "v1"
                disclaimers = get_disclaimers(locale)
                base_payload = (
                    existing.interpretation_payload
                    if isinstance(existing.interpretation_payload, dict)
                    else {}
                )
                full_payload = {**base_payload, "disclaimers": disclaimers}

                if level == "complete":
                    use_v3 = settings.natal_schema_version == "v3"
                    if use_v3:
                        try:
                            interpretation = AstroResponseV3(**base_payload)
                            schema_version = "v3"
                        except Exception:
                            try:
                                interpretation = AstroErrorResponseV3(**base_payload)
                                schema_version = "v3_error"
                            except Exception:
                                try:
                                    interpretation = AstroResponseV2(**full_payload)
                                    schema_version = "v2"
                                except Exception:
                                    interpretation = AstroResponseV1(**full_payload)
                    else:
                        try:
                            interpretation = AstroResponseV2(**full_payload)
                            schema_version = "v2"
                        except Exception:
                            interpretation = AstroResponseV1(**full_payload)
                else:
                    interpretation = AstroResponseV1(**full_payload)

                meta = InterpretationMeta(
                    id=existing.id,
                    level=level,
                    use_case=existing.use_case,
                    persona_id=str(existing.persona_id) if existing.persona_id else None,
                    persona_name=existing.persona_name,
                    prompt_version_id=str(existing.prompt_version_id)
                    if existing.prompt_version_id
                    else None,
                    schema_version="unknown",  # Will be set by format method
                    validation_status="valid",
                    was_fallback=existing.was_fallback,
                    request_id=request_id,
                    cached=True,
                    persisted_at=existing.created_at,
                    module=module,
                )
                return NatalInterpretationServiceV2.format_interpretation_response(
                    existing, meta, locale
                )

        # 1. Normalization (N1)
        no_time = birth_profile.birth_time is None
        no_location = birth_profile.birth_lat is None or birth_profile.birth_lon is None

        degraded_mode_str = None
        if no_time and no_location:
            degraded_mode_str = "no_location_no_time"
        elif no_time:
            degraded_mode_str = "no_time"
        elif no_location:
            degraded_mode_str = "no_location"

        chart_json_dict = build_chart_json(natal_result, birth_profile, degraded_mode_str)
        evidence_catalog = build_enriched_evidence_catalog(chart_json_dict)

        # 2. Use case selection
        if level == "complete" and variant_code == "free_short":
            return await NatalInterpretationServiceV2._generate_free_short(
                db=db,
                user_id=user_id,
                chart_id=chart_id,
                natal_result=natal_result,
                birth_profile=birth_profile,
                chart_json_dict=chart_json_dict,
                evidence_catalog=evidence_catalog,
                locale=locale,
                request_id=request_id,
                trace_id=trace_id,
                degraded_mode_str=degraded_mode_str,
            )

        if level == "complete" and module:
            use_case_key = MODULE_TO_USE_CASE_KEY.get(module, "natal_interpretation")
        else:
            use_case_key = (
                "natal_interpretation" if level == "complete" else "natal_interpretation_short"
            )

        # 3. Persona resolution (AC3)
        persona_name = None
        persona_prompt_profile = None
        if level == "complete" and not persona_id:
            raise InputValidationError("persona_id is required for complete interpretation.")

        if persona_id:
            try:
                if persona_uuid is None:
                    raise InputValidationError(f"Persona {persona_id} not found.")
                persona = db.execute(
                    select(LlmPersonaModel).where(LlmPersonaModel.id == persona_uuid)
                ).scalar_one_or_none()
                if persona:
                    persona_name = persona.name
                    persona_prompt_profile = _build_persona_prompt_profile(persona)
                else:
                    logger.warning(f"Persona {persona_id} not found in DB")
                    raise InputValidationError(f"Persona {persona_id} not found.")
            except InputValidationError:
                raise
            except Exception as e:
                logger.error(f"Error resolving persona {persona_id}: {e}")
                raise

        # 4. Build user_input vs context (AC4)
        user_input: dict = {
            "chart_json": chart_json_dict,
            "locale": locale,
        }
        if level == "short":
            user_input["question"] = question or "Interprète mon thème natal."

        context = {
            "locale": locale,
            "chart_json": json.dumps(chart_json_dict, ensure_ascii=False),
            "evidence_catalog": evidence_catalog,
            "use_case": use_case_key,
            "validation_strict": level == "complete",
        }
        if persona_id:
            context["persona_id"] = persona_id
        if persona_prompt_profile:
            context["persona_name"] = persona_prompt_profile

        # 5. Call Gateway
        gateway = LLMGateway()
        gateway_result = await gateway.execute(
            use_case=use_case_key,
            user_input=user_input,
            context=context,
            request_id=request_id,
            trace_id=trace_id,
            user_id=user_id,
            db=db,
        )

        # 6. Handle result and map to schema
        if not gateway_result.structured_output:
            logger.error(f"Gateway returned no structured output for {use_case_key}")
            raise RuntimeError("Gateway returned no structured output")

        disclaimers = get_disclaimers(locale)
        base_output = (
            gateway_result.structured_output
            if isinstance(gateway_result.structured_output, dict)
            else {}
        )
        full_output = {**base_output, "disclaimers": disclaimers}

        # Mapping structured_output to AstroResponseV1/V2/V3 (Story 30-8 T7.4)
        schema_version = "v1"
        use_v3 = settings.natal_schema_version == "v3"

        if level == "complete" and not gateway_result.meta.fallback_triggered:
            if use_v3:
                # complete + v3 flag → try v3 first, then v3_error, then v2, then v1
                try:
                    # AstroResponseV3 does NOT have disclaimers in schema
                    interpretation: (  # noqa: E501
                        AstroResponseV3 | AstroErrorResponseV3 | AstroResponseV2 | AstroResponseV1
                    ) = AstroResponseV3(**base_output)
                    schema_version = "v3"
                except Exception as exc:
                    logger.debug(f"AstroResponseV3 deserialization failed: {exc}")
                    try:
                        interpretation = AstroErrorResponseV3(**base_output)
                        schema_version = "v3_error"
                    except Exception as exc2:
                        logger.debug(f"AstroErrorResponseV3 deserialization failed: {exc2}")
                        logger.warning(
                            "V3 deserialization failed, falling back to V2 for request_id=%s",
                            request_id,
                        )
                        try:
                            interpretation = AstroResponseV2(**full_output)
                            schema_version = "v2"
                        except Exception:
                            interpretation = AstroResponseV1(**full_output)
            else:
                # complete (payant) → schéma v2
                try:
                    interpretation = AstroResponseV2(**full_output)
                    schema_version = "v2"
                except Exception as exc:
                    logger.warning(
                        "V2 deserialization failed (%s), falling back to V1 for request_id=%s",
                        exc,
                        request_id,
                    )
                    interpretation = AstroResponseV1(**full_output)
        else:
            # short (gratuit) ou fallback vers short → schéma v1
            interpretation = AstroResponseV1(**full_output)

        # Observe metrics
        if hasattr(interpretation, "summary"):
            observe_duration("natal_summary_len", float(len(interpretation.summary)))
        if hasattr(interpretation, "sections"):
            for _section in interpretation.sections:
                if hasattr(_section, "content"):
                    observe_duration("natal_section_len", float(len(_section.content)))

        # Gateway meta to our InterpretationMeta
        meta = InterpretationMeta(
            id=None,
            level=level,
            use_case=gateway_result.use_case,
            persona_id=persona_id or gateway_result.meta.persona_id,
            persona_name=persona_name,
            prompt_version_id=gateway_result.meta.prompt_version_id,
            schema_version=schema_version,
            validation_status=gateway_result.meta.validation_status,
            repair_attempted=gateway_result.meta.repair_attempted,
            fallback_triggered=gateway_result.meta.fallback_triggered,
            was_fallback=gateway_result.meta.fallback_triggered,
            latency_ms=gateway_result.meta.latency_ms,
            request_id=request_id,
            cached=False,
            module=module,
        )

        # 7. Persist interpretation
        db_level = InterpretationLevel.SHORT if level == "short" else InterpretationLevel.COMPLETE

        # Story 30-8 T7.4: Ensure persisted payload does NOT contain disclaimers if it's V3
        # (The gateway structured_output shouldn't have them, but we sanitize to be sure)
        persist_payload = (
            gateway_result.structured_output
            if isinstance(gateway_result.structured_output, dict)
            else {}
        )
        if schema_version.startswith("v3") and "disclaimers" in persist_payload:
            persist_payload = persist_payload.copy()
            persist_payload.pop("disclaimers", None)

        try:
            if not is_thematic_module:
                unique_stmt = select(UserNatalInterpretationModel).where(
                    UserNatalInterpretationModel.user_id == user_id,
                    UserNatalInterpretationModel.level == db_level,
                )
                if db_level == InterpretationLevel.SHORT:
                    unique_stmt = unique_stmt.where(
                        UserNatalInterpretationModel.persona_id.is_(None)
                    )
                else:
                    unique_stmt = unique_stmt.where(
                        UserNatalInterpretationModel.persona_id == persona_uuid
                    )
                unique_stmt = unique_stmt.order_by(
                    UserNatalInterpretationModel.created_at.desc(),
                    UserNatalInterpretationModel.id.desc(),
                )

                rows = list(db.execute(unique_stmt).scalars().all())
                primary = rows[0] if rows else None
                for duplicate in rows[1:]:
                    db.delete(duplicate)

                prompt_version_uuid = (
                    uuid.UUID(gateway_result.meta.prompt_version_id)
                    if gateway_result.meta.prompt_version_id
                    else None
                )
                if primary is None:
                    primary = UserNatalInterpretationModel(
                        user_id=user_id,
                        chart_id=chart_id,
                        level=db_level,
                        use_case=gateway_result.use_case,
                        variant_code=variant_code,
                        persona_id=persona_uuid,
                        persona_name=persona_name,
                        prompt_version_id=prompt_version_uuid,
                        interpretation_payload=persist_payload,
                        was_fallback=gateway_result.meta.fallback_triggered,
                        degraded_mode=degraded_mode_str,
                    )
                    db.add(primary)
                else:
                    primary.chart_id = chart_id
                    primary.use_case = gateway_result.use_case
                    primary.variant_code = variant_code
                    primary.persona_id = persona_uuid
                    primary.persona_name = persona_name
                    primary.prompt_version_id = prompt_version_uuid
                    primary.interpretation_payload = persist_payload
                    primary.was_fallback = gateway_result.meta.fallback_triggered
                    primary.degraded_mode = degraded_mode_str

                db.commit()
                db.refresh(primary)
                meta.id = primary.id
                meta.persisted_at = primary.created_at
        except Exception as persist_exc:
            # Best-effort persistence: do not fail user response when DB write fails.
            db.rollback()
            logger.exception(
                "Failed to persist natal interpretation request_id=%s use_case=%s error=%s",
                request_id,
                gateway_result.use_case,
                persist_exc,
            )

        return NatalInterpretationResponse(
            data=NatalInterpretationData(
                chart_id=chart_id,
                use_case=gateway_result.use_case,
                interpretation=interpretation,
                meta=meta,
                degraded_mode=degraded_mode_str,
            ),
            disclaimers=disclaimers,
        )

    @staticmethod
    async def _generate_free_short(
        db: Session,
        user_id: int,
        chart_id: str,
        natal_result: NatalResult,
        birth_profile: UserBirthProfileData,
        chart_json_dict: dict,
        evidence_catalog: list,
        locale: str,
        request_id: str,
        trace_id: str,
        degraded_mode_str: str | None,
    ) -> NatalInterpretationResponse:
        """
        Génère une interprétation restreinte pour les utilisateurs free.
        Appelle un prompt unique 'natal_long_free' qui produit summary + accordion_titles.
        """
        use_case_key = "natal_long_free"

        user_input = {
            "chart_json": chart_json_dict,
            "locale": locale,
        }
        context = {
            "locale": locale,
            "chart_json": json.dumps(chart_json_dict, ensure_ascii=False),
            "evidence_catalog": evidence_catalog,
            "use_case": use_case_key,
            "validation_strict": False,
        }

        gateway = LLMGateway()
        gateway_result = await gateway.execute(
            use_case=use_case_key,
            user_input=user_input,
            context=context,
            request_id=request_id,
            trace_id=trace_id,
            user_id=user_id,
            db=db,
        )

        if not gateway_result.structured_output:
            logger.error(f"Gateway returned no structured output for {use_case_key}")
            raise RuntimeError("Gateway returned no structured output")

        disclaimers = get_disclaimers(locale)
        structured = gateway_result.structured_output
        
        # On mappe vers AstroResponseV1 (summary présent, sections vides)
        # story 64.3: accordion_titles est retourné par le LLM mais pas encore dans AstroResponseV1.
        # On va l'injecter dans interpretation_payload pour persistence et UI.
        
        interpretation = AstroResponseV1(
            title="Thème Natal (Résumé)",
            summary=structured.get("summary", ""),
            sections=[
                {
                    "key": "overall",
                    "heading": "Résumé Global",
                    "content": "Contenu restreint. Passez au plan Basic ou Premium pour débloquer l'analyse complète.",
                },
                {
                    "key": "inner_life",
                    "heading": "Vie Intérieure",
                    "content": "Contenu restreint. Passez au plan Basic ou Premium pour débloquer l'analyse complète.",
                }
            ],
            highlights=["Résumé Premium", "Analyse des dominantes", "Potentiel d'évolution"],
            key_points=[],
            advice=["Passez au plan Basic pour l'analyse complète", "Explorez vos dominantes", "Suivez votre guide quotidien"],
            disclaimers=disclaimers
        )

        meta = InterpretationMeta(
            id=None,
            level="complete",
            use_case=use_case_key,
            persona_id=None,
            persona_name=None,
            prompt_version_id=gateway_result.meta.prompt_version_id,
            schema_version="v1",
            validation_status=gateway_result.meta.validation_status,
            was_fallback=gateway_result.meta.fallback_triggered,
            latency_ms=gateway_result.meta.latency_ms,
            request_id=request_id,
            cached=False,
        )

        # Persistence
        persist_payload = {
            **structured,
            "title": "Thème Natal (Résumé)",
            "sections": [
                {
                    "key": "overall",
                    "heading": "Résumé Global",
                    "content": "Contenu restreint. Passez au plan Basic ou Premium pour débloquer l'analyse complète.",
                },
                {
                    "key": "inner_life",
                    "heading": "Vie Intérieure",
                    "content": "Contenu restreint. Passez au plan Basic ou Premium pour débloquer l'analyse complète.",
                }
            ],
            "highlights": ["Résumé Premium", "Analyse des dominantes", "Potentiel d'évolution"],
            "key_points": [],
            "advice": ["Passez au plan Basic pour l'analyse complète", "Explorez vos dominantes", "Suivez votre guide quotidien"]
        }
        
        prompt_version_uuid = (
            uuid.UUID(gateway_result.meta.prompt_version_id)
            if gateway_result.meta.prompt_version_id
            else None
        )
        
        # Nettoyage anciens doublons éventuels
        stmt_del = select(UserNatalInterpretationModel).where(
            UserNatalInterpretationModel.user_id == user_id,
            UserNatalInterpretationModel.level == InterpretationLevel.COMPLETE,
            UserNatalInterpretationModel.variant_code == "free_short"
        )
        existing_rows = list(db.execute(stmt_del).scalars().all())
        for row in existing_rows:
            db.delete(row)

        primary = UserNatalInterpretationModel(
            user_id=user_id,
            chart_id=chart_id,
            level=InterpretationLevel.COMPLETE,
            use_case=use_case_key,
            variant_code="free_short",
            persona_id=None,
            persona_name=None,
            prompt_version_id=prompt_version_uuid,
            interpretation_payload=persist_payload,
            was_fallback=gateway_result.meta.fallback_triggered,
            degraded_mode=degraded_mode_str,
        )
        db.add(primary)
        db.flush()
        meta.id = primary.id
        meta.persisted_at = primary.created_at or datetime.now(timezone.utc)

        return NatalInterpretationResponse(
            data=NatalInterpretationData(
                chart_id=chart_id,
                use_case=use_case_key,
                interpretation=interpretation,
                meta=meta,
                degraded_mode=degraded_mode_str,
            ),
            disclaimers=disclaimers,
        )

    @staticmethod
    def list_interpretations(
        db: Session,
        user_id: int,
        chart_id: Optional[str] = None,
        level: Optional[Literal["short", "complete"]] = None,
        persona_id: Optional[str] = None,
        module: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[UserNatalInterpretationModel], int]:
        stmt = select(UserNatalInterpretationModel).where(
            UserNatalInterpretationModel.user_id == user_id
        )
        if chart_id:
            stmt = stmt.where(UserNatalInterpretationModel.chart_id == chart_id)
        if level:
            db_level = (
                InterpretationLevel.SHORT if level == "short" else InterpretationLevel.COMPLETE
            )
            stmt = stmt.where(UserNatalInterpretationModel.level == db_level)
        if persona_id:
            try:
                stmt = stmt.where(UserNatalInterpretationModel.persona_id == uuid.UUID(persona_id))
            except (ValueError, TypeError):
                pass
        if module:
            # Match use_case based on module mapping if possible
            use_case = MODULE_TO_USE_CASE_KEY.get(module, module)
            stmt = stmt.where(UserNatalInterpretationModel.use_case == use_case)

        total = int(db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)

        stmt = (
            stmt.order_by(UserNatalInterpretationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = db.execute(stmt).scalars().all()
        return list(items), total

    @staticmethod
    def delete_interpretation(
        db: Session,
        user_id: int,
        interpretation_id: int,
        request_id: str,
        actor_role: str = "user",
    ) -> bool:
        stmt = select(UserNatalInterpretationModel).where(
            UserNatalInterpretationModel.id == interpretation_id,
            UserNatalInterpretationModel.user_id == user_id,
        )
        item = db.execute(stmt).scalar_one_or_none()
        if not item:
            return False

        # Audit before delete
        from app.services.audit_service import AuditEventCreatePayload, AuditService

        audit_payload = AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=user_id,
            actor_role=actor_role,
            action="natal_interpretation_deleted",
            target_type="natal_interpretation",
            target_id=str(interpretation_id),
            status="success",
            details={
                "target_interpretation_id": interpretation_id,
                "chart_id": item.chart_id,
                "level": item.level.value,
                "persona_id": str(item.persona_id) if item.persona_id else None,
                "created_at": item.created_at.isoformat(),
                "deleted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        db.delete(item)
        db.commit()

        try:
            AuditService.record_event(db, payload=audit_payload)
        except Exception as e:
            logger.warning(f"Failed to record audit event for interpretation deletion: {e}")

        return True

    @staticmethod
    def get_interpretation_by_id(
        db: Session,
        user_id: int,
        interpretation_id: int,
    ) -> Optional[UserNatalInterpretationModel]:
        stmt = select(UserNatalInterpretationModel).where(
            UserNatalInterpretationModel.id == interpretation_id,
            UserNatalInterpretationModel.user_id == user_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def format_interpretation_response(
        model: UserNatalInterpretationModel,
        meta: InterpretationMeta,
        locale: str,
    ) -> NatalInterpretationResponse:
        """
        Formats a UserNatalInterpretationModel into a NatalInterpretationResponse.
        Handles schema versioning (v1, v2, v3).
        """
        meta.id = model.id
        disclaimers = get_disclaimers(locale)
        base_payload = (
            model.interpretation_payload if isinstance(model.interpretation_payload, dict) else {}
        )
        full_payload = {**base_payload, "disclaimers": disclaimers}

        schema_version = "v1"
        if model.level == InterpretationLevel.COMPLETE:
            use_v3 = settings.natal_schema_version == "v3"
            if use_v3:
                try:
                    interpretation = AstroResponseV3(**base_payload)
                    schema_version = "v3"
                except Exception:
                    try:
                        interpretation = AstroErrorResponseV3(**base_payload)
                        schema_version = "v3_error"
                    except Exception:
                        try:
                            interpretation = AstroResponseV2(**full_payload)
                            schema_version = "v2"
                        except Exception:
                            interpretation = AstroResponseV1(**full_payload)
            else:
                try:
                    interpretation = AstroResponseV2(**full_payload)
                    schema_version = "v2"
                except Exception:
                    interpretation = AstroResponseV1(**full_payload)
        else:
            interpretation = AstroResponseV1(**full_payload)

        meta.schema_version = schema_version

        return NatalInterpretationResponse(
            data=NatalInterpretationData(
                chart_id=model.chart_id,
                use_case=model.use_case,
                interpretation=interpretation,
                meta=meta,
                degraded_mode=model.degraded_mode,
            ),
            disclaimers=disclaimers,
        )
