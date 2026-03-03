from __future__ import annotations

import json
import logging
import uuid
from typing import Literal, Optional

from sqlalchemy import delete, select
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
from app.services.chart_json_builder import (
    build_chart_json,
    build_enriched_evidence_catalog,
)
from app.services.disclaimer_registry import get_disclaimers
from app.services.user_birth_profile_service import UserBirthProfileData

logger = logging.getLogger(__name__)


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
    ) -> NatalInterpretationResponse:
        # 0. Check for existing persisted interpretation
        if not force_refresh:
            db_level = (
                InterpretationLevel.SHORT if level == "short" else InterpretationLevel.COMPLETE
            )
            stmt = select(UserNatalInterpretationModel).where(
                UserNatalInterpretationModel.user_id == user_id,
                UserNatalInterpretationModel.chart_id == chart_id,
                UserNatalInterpretationModel.level == db_level,
            )
            # For complete, we also check persona
            if level == "complete" and persona_id:
                try:
                    stmt = stmt.where(
                        UserNatalInterpretationModel.persona_id == uuid.UUID(persona_id)
                    )
                except (ValueError, TypeError):
                    pass

            existing = db.execute(stmt).scalar_one_or_none()
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
                    level=level,
                    use_case=existing.use_case,
                    persona_id=str(existing.persona_id) if existing.persona_id else None,
                    persona_name=existing.persona_name,
                    prompt_version_id=str(existing.prompt_version_id)
                    if existing.prompt_version_id
                    else None,
                    schema_version=schema_version,
                    validation_status="valid",
                    was_fallback=existing.was_fallback,
                    request_id=request_id,
                    cached=True,
                    persisted_at=existing.created_at,
                )
                return NatalInterpretationResponse(
                    data=NatalInterpretationData(
                        chart_id=chart_id,
                        use_case=existing.use_case,
                        interpretation=interpretation,
                        meta=meta,
                        degraded_mode=existing.degraded_mode,
                    ),
                    disclaimers=disclaimers,
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
        use_case_key = (
            "natal_interpretation" if level == "complete" else "natal_interpretation_short"
        )

        # 3. Persona resolution (AC3)
        persona_name = None
        if level == "complete" and not persona_id:
            raise InputValidationError("persona_id is required for complete interpretation.")

        if persona_id:
            try:
                persona = db.execute(
                    select(LlmPersonaModel).where(LlmPersonaModel.id == uuid.UUID(persona_id))
                ).scalar_one_or_none()
                if persona:
                    persona_name = persona.name
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
        if persona_name:
            context["persona_name"] = persona_name

        # 5. Call Gateway
        gateway = LLMGateway()
        gateway_result = await gateway.execute(
            use_case=use_case_key,
            user_input=user_input,
            context=context,
            request_id=request_id,
            trace_id=trace_id,
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
                except Exception:
                    try:
                        interpretation = AstroErrorResponseV3(**base_output)
                        schema_version = "v3_error"
                    except Exception as exc:
                        logger.warning(
                            "V3 deserialization failed (%s), falling back to V2 for request_id=%s",
                            exc,
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
        )

        # 7. Persist interpretation
        db_level = InterpretationLevel.SHORT if level == "short" else InterpretationLevel.COMPLETE

        if force_refresh:
            stmt_del = delete(UserNatalInterpretationModel).where(
                UserNatalInterpretationModel.user_id == user_id,
                UserNatalInterpretationModel.chart_id == chart_id,
                UserNatalInterpretationModel.level == db_level,
            )
            if level == "complete" and persona_id:
                try:
                    stmt_del = stmt_del.where(
                        UserNatalInterpretationModel.persona_id == uuid.UUID(persona_id)
                    )
                except (ValueError, TypeError):
                    pass
            db.execute(stmt_del)

        new_persisted = UserNatalInterpretationModel(
            user_id=user_id,
            chart_id=chart_id,
            level=db_level,
            use_case=gateway_result.use_case,
            persona_id=uuid.UUID(persona_id) if persona_id else None,
            persona_name=persona_name,
            prompt_version_id=uuid.UUID(gateway_result.meta.prompt_version_id)
            if gateway_result.meta.prompt_version_id
            else None,
            interpretation_payload=gateway_result.structured_output,
            was_fallback=gateway_result.meta.fallback_triggered,
            degraded_mode=degraded_mode_str,
        )
        db.add(new_persisted)
        db.commit()
        db.refresh(new_persisted)
        meta.persisted_at = new_persisted.created_at

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
